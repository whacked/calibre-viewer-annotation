console.log("utility included.");
var score2rgb = (function score2rgb$(score) {
  /* score2rgb manager/js/utility.sib:4:0 */

  var r = 0,
      g = 0,
      b = 0;
  (0.5 < score) ? (function() {
    /* manager/js/utility.sib:9:14 */
  
    r = Math.floor((255 * (1 - (2 * (score - 0.5)))));
    return g = 255;
  }).call(this) : (function() {
    /* manager/js/utility.sib:12:14 */
  
    r = 255;
    return g = Math.floor((255 * (1 - (2 * (0.5 - score)))));
  }).call(this);
  return ("rgb(" + Math.floor(r) + "," + Math.floor(g) + "," + b + ")");
});
var makeEntryId = (function makeEntryId$(entry) {
  /* make-entry-id manager/js/utility.sib:17:0 */

  return (entry.startLocation + "-" + entry.endLocation);
});
var cleanString = (function cleanString$(s) {
  /* clean-string manager/js/utility.sib:20:0 */

  return entities.decode(s.replace((new RegExp("\\s+$", undefined)), "").replace((new RegExp("^\\s+", undefined)), ""));
});
var getNumeric = (function getNumeric$(s) {
  /* get-numeric manager/js/utility.sib:26:0 */

  return parseFloat(s.replace((new RegExp("\\D", "g")), ""));
});
var getCorpusCoverage = (function getCorpusCoverage$(corpus, tokenList) {
  /* get-corpus-coverage manager/js/utility.sib:29:0 */

  var hitCount = 0,
      offset = 0;
  tokenList.forEach((function(token) {
    /* manager/js/utility.sib:40:5 */
  
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