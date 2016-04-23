console.log("utility included.");
var score2rgb = (function score2rgb$(score) {
  /* score2rgb eval.sibilant:4:0 */

  var r = 0,
      g = 0,
      b = 0;
  (0.5 < score) ? (function() {
    /* eval.sibilant:9:14 */
  
    r = Math.floor((255 * (1 - (2 * (score - 0.5)))));
    return g = 255;
  }).call(this) : (function() {
    /* eval.sibilant:12:14 */
  
    r = 255;
    return g = Math.floor((255 * (1 - (2 * (0.5 - score)))));
  }).call(this);
  return ("rgb(" + Math.floor(r) + "," + Math.floor(g) + "," + b + ")");
});
var makeEntryId = (function makeEntryId$(entry) {
  /* make-entry-id eval.sibilant:17:0 */

  return (entry.startLocation + "-" + entry.endLocation);
});
var cleanString = (function cleanString$(s) {
  /* clean-string eval.sibilant:20:0 */

  return entities.decode(s.replace((new RegExp("\\s+$", undefined)), "").replace((new RegExp("^\\s+", undefined)), ""));
});
var getCorpusCoverage = (function getCorpusCoverage$(corpus, tokenList) {
  /* get-corpus-coverage eval.sibilant:26:0 */

  var hitCount = 0,
      offset = 0;
  tokenList.forEach((function(token) {
    /* eval.sibilant:29:5 */
  
    var foundIndex = corpus.substr(offset).indexOf(token);
    return (function() {
      if (-1 < foundIndex) {
        ((hitCount)++);
        return offset = (offset + foundIndex);
      }
    }).call(this);
  }));
  return hitCount;
});
var renderEntryResultRow = (function renderEntryResultRow$(entry) {
  /* render-entry-result-row eval.sibilant:38:0 */

  var entryId = makeEntryId(entry);
  var result = (allResult[entryId] || {  });
  var tr = $("<tr>");
  [ "check?", "timestamp", "location", "found?", "highlight", "note", "verification" ].forEach((function(key) {
    /* eval.sibilant:42:5 */
  
    var td = $("<td>");
    var entryVal = entry[key];
    (function() {
      if (key === "check?") {
        return td.append($("<button>").html("check").click((function() {
          /* eval.sibilant:50:35 */
        
          return launchAndFind(result.source, entry);
        })));
      } else if (key === "timestamp") {
        return td.html((new Date(entryVal)));
      } else if (key === "location") {
        return td.html((entry.startLocation + "~" + entry.endLocation + " (" + (entry.endLocation - entry.startLocation) + ")"));
      } else if (key === "found?") {
        return (function() {
          /* eval.sibilant:63:15 */
        
          return ((result.score && 0 < result.score)) ? (function() {
            /* eval.sibilant:66:25 */
          
            return td.attr({ class: "yes-found" }).html(("" + result.score.toFixed(3) + " " + result.source));
          }).call(this) : (function() {
            /* eval.sibilant:74:25 */
          
            return td.attr({ class: "not-found" });
          }).call(this);
        }).call(this);
      } else if (key === "verification") {
        return td.attr({
          id: ("td-sel-" + entryId),
          class: "td-sel"
        });
      } else {
        return td.html(entryVal);
      }
    }).call(this);
    return td.appendTo(tr);
  }));
  return tr;
});
