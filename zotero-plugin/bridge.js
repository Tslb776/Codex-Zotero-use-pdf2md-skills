CodexZoteroBridge = {
  id: null,
  version: null,
  rootURI: null,
  // Replace before installing. Do not commit a real token.
  token: "CHANGE_ME_TO_A_LONG_RANDOM_LOCAL_TOKEN",
  endpointPaths: [],

  init({ id, version, rootURI }) {
    this.id = id;
    this.version = version;
    this.rootURI = rootURI;
  },

  json(status, value) {
    return [status, "application/json; charset=utf-8", JSON.stringify(value)];
  },

  error(status, message) {
    return this.json(status, { ok: false, error: message });
  },

  authenticate(headers) {
    return headers["x-codex-zotero-key"] === this.token;
  },

  getItem(itemKey, libraryID) {
    let id = libraryID ? Number(libraryID) : Zotero.Libraries.userLibraryID;
    if (!Number.isInteger(id)) {
      throw new Error("Invalid libraryID");
    }
    let item = Zotero.Items.getByLibraryAndKey(id, itemKey);
    if (!item) {
      throw new Error(`Item not found: ${itemKey} in library ${id}`);
    }
    return item;
  },

  requireObject(data) {
    if (!data || typeof data !== "object" || Array.isArray(data)) {
      throw new Error("JSON object body required");
    }
  },

  async updateItem(item, data) {
    this.requireObject(data);
    let changed = false;

    if (data.fields !== undefined) {
      this.requireObject(data.fields);
      for (let [field, value] of Object.entries(data.fields)) {
        if (typeof value !== "string" && typeof value !== "number") {
          throw new Error(`Field '${field}' must be a string or number`);
        }
        item.setField(field, value);
        changed = true;
      }
    }

    if (data.extra !== undefined) {
      this.requireObject(data.extra);
      let mode = data.extra.mode || "append";
      let text = data.extra.text;
      if (typeof text !== "string" || !text.trim()) {
        throw new Error("extra.text must be a non-empty string");
      }
      let current = item.getField("extra") || "";
      if (mode === "append") {
        let marker = data.extra.dedupeMarker;
        if (!marker || !current.includes(marker)) {
          item.setField("extra", current ? current.trimEnd() + "\n\n" + text : text);
          changed = true;
        }
      }
      else if (mode === "replace") {
        item.setField("extra", text);
        changed = true;
      }
      else {
        throw new Error("extra.mode must be 'append' or 'replace'");
      }
    }

    if (data.tags !== undefined) {
      this.requireObject(data.tags);
      if (data.tags.replace !== undefined) {
        if (!Array.isArray(data.tags.replace)) throw new Error("tags.replace must be an array");
        item.setTags(data.tags.replace.map(tag => ({ tag: String(tag) })));
        changed = true;
      }
      if (data.tags.add !== undefined) {
        if (!Array.isArray(data.tags.add)) throw new Error("tags.add must be an array");
        for (let tag of data.tags.add) item.addTag(String(tag));
        changed = true;
      }
      if (data.tags.remove !== undefined) {
        if (!Array.isArray(data.tags.remove)) throw new Error("tags.remove must be an array");
        for (let tag of data.tags.remove) item.removeTag(String(tag));
        changed = true;
      }
    }

    if (changed) {
      await item.saveTx();
    }
    return changed;
  },

  register(path, endpoint) {
    Zotero.Server.Endpoints[path] = endpoint;
    this.endpointPaths.push(path);
  },

  registerEndpoints() {
    let bridge = this;

    this.register("/codex-zotero-bridge/ping", class {
      supportedMethods = ["GET"];
      init({ headers }) {
        if (!bridge.authenticate(headers)) return bridge.error(401, "Unauthorized");
        return bridge.json(200, {
          ok: true,
          bridgeVersion: bridge.version,
          zoteroVersion: Zotero.version,
          userLibraryID: Zotero.Libraries.userLibraryID
        });
      }
    });

    this.register("/codex-zotero-bridge/items/:itemKey", class {
      supportedMethods = ["GET"];
      init({ headers, pathParams, searchParams }) {
        if (!bridge.authenticate(headers)) return bridge.error(401, "Unauthorized");
        try {
          let item = bridge.getItem(pathParams.itemKey, searchParams.get("libraryID"));
          return bridge.json(200, { ok: true, item: item.toJSON() });
        }
        catch (error) {
          return bridge.error(404, error.message);
        }
      }
    });

    this.register("/codex-zotero-bridge/items/:itemKey/update", class {
      supportedMethods = ["POST"];
      supportedDataTypes = ["application/json"];
      async init({ headers, pathParams, data }) {
        if (!bridge.authenticate(headers)) return bridge.error(401, "Unauthorized");
        try {
          let item = bridge.getItem(pathParams.itemKey, data?.libraryID);
          let changed = await bridge.updateItem(item, data);
          return bridge.json(200, { ok: true, changed, item: item.toJSON() });
        }
        catch (error) {
          Zotero.logError(error);
          return bridge.error(400, error.message);
        }
      }
    });

    this.register("/codex-zotero-bridge/items/:itemKey/attachments", class {
      supportedMethods = ["POST"];
      supportedDataTypes = ["application/json"];
      async init({ headers, pathParams, data }) {
        if (!bridge.authenticate(headers)) return bridge.error(401, "Unauthorized");
        try {
          bridge.requireObject(data);
          if (typeof data.path !== "string" || !data.path) throw new Error("path is required");
          let parent = bridge.getItem(pathParams.itemKey, data.libraryID);
          let mode = data.mode || "import";
          let options = {
            file: data.path,
            parentItemID: parent.id,
            title: data.title || undefined,
            contentType: data.contentType || undefined
          };
          let attachment;
          if (mode === "import") {
            attachment = await Zotero.Attachments.importFromFile(options);
          }
          else if (mode === "link") {
            attachment = await Zotero.Attachments.linkFromFile(options);
          }
          else {
            throw new Error("mode must be 'import' or 'link'");
          }
          return bridge.json(201, { ok: true, attachment: attachment.toJSON() });
        }
        catch (error) {
          Zotero.logError(error);
          return bridge.error(400, error.message);
        }
      }
    });

    this.register("/codex-zotero-bridge/items/:itemKey/notes", class {
      supportedMethods = ["POST"];
      supportedDataTypes = ["application/json"];
      async init({ headers, pathParams, data }) {
        if (!bridge.authenticate(headers)) return bridge.error(401, "Unauthorized");
        try {
          bridge.requireObject(data);
          if (typeof data.html !== "string" || !data.html) throw new Error("html is required");
          let parent = bridge.getItem(pathParams.itemKey, data.libraryID);
          let note = new Zotero.Item("note");
          note.libraryID = parent.libraryID;
          note.parentID = parent.id;
          note.setNote(data.html);
          await note.saveTx();
          return bridge.json(201, { ok: true, note: note.toJSON() });
        }
        catch (error) {
          Zotero.logError(error);
          return bridge.error(400, error.message);
        }
      }
    });
  },

  unregisterEndpoints() {
    for (let path of this.endpointPaths) {
      delete Zotero.Server.Endpoints[path];
    }
    this.endpointPaths = [];
  }
};
