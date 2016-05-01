var fs = require("fs"),
    path = require("path"),
    sqlite3 = require("sqlite3"),
    yesql = require("seduce"),
    m = require("mithril"),
    clipboard = require("clipboard"),
    exec = require("child_process").exec,
    username = require("username"),
    dialog = require("remote").require("dialog");
var $ADB_FILENAME = "ebook-viewer-annotation.db",
    $HOME = process.env[(process.platform === "win32") ? "USERPROFILE" : "HOME"],
    $CALIBRE_HOME = path.join($HOME, "Calibre Library"),
    $ADB_FILEPATH = path.join($HOME, $ADB_FILENAME),
    $CDB_FILEPATH = path.join($CALIBRE_HOME, "metadata.db"),
    $USERNAME = null;
(function() {
  try {
    return fs.statSync($ADB_FILEPATH);
  } catch (e) {
    return fs.statSync($CDB_FILEPATH);
  }
}).call(this);
var aDb = (new sqlite3.Database($ADB_FILEPATH));
var aSql = yesql("sql/main.sql");
var cDb = (new sqlite3.Database($CDB_FILEPATH));
var cSql = yesql("sql/calibre.sql");
var cleanup = (function cleanup$() {
  /* cleanup manager/js/init.sib:40:0 */

  aDb.close();
  cDb.close();
  return console.log("cleanup ok");
});
window.onunload = (function() {
  /* manager/js/init.sib:46:8 */

  return cleanup();
});
username().then((function() {
  /* manager/js/init.sib:51:5 */

  return $USERNAME = arguments[0];
}));
console.log("initialized.");