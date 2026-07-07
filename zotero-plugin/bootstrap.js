var CodexZoteroBridge;

function log(message) {
  Zotero.debug("Codex Zotero Bridge: " + message);
}

function install() {
  log("Installed");
}

async function startup({ id, version, rootURI }) {
  await Zotero.initializationPromise;
  Services.scriptloader.loadSubScript(rootURI + "bridge.js");
  CodexZoteroBridge.init({ id, version, rootURI });
  CodexZoteroBridge.registerEndpoints();
  log("Started " + version);
}

function shutdown() {
  if (CodexZoteroBridge) {
    CodexZoteroBridge.unregisterEndpoints();
  }
  CodexZoteroBridge = undefined;
  log("Stopped");
}

function uninstall() {
  log("Uninstalled");
}
