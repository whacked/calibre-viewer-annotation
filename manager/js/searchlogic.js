var DEBUG_LEVEL = 10;
var consoleLogOrig = console.log;
var dlog = (function dlog$(argv) {
  /* dlog manager/js/searchlogic.sib:6:0 */

  var argv = Array.prototype.slice.call(arguments, 0);

  return (function() {
    if (0 < DEBUG_LEVEL) {
      return consoleLogOrig.apply(console, argv);
    }
  }).call(this);
});
console.log = dlog;
var arrPres = [],
    htmlMap = {  },
    spineMap = {  },
    allResult = {  };
var makeResult = (function makeResult$(index, score, sourceFile) {
  /* make-result manager/js/searchlogic.sib:30:0 */

  return {
    index: index,
    score: score,
    source: sourceFile
  };
});
var maybeResult = (function maybeResult$(entry) {
  /* maybe-result manager/js/searchlogic.sib:33:0 */

  return allResult[makeEntryId(entry)];
});
var getFileIndex = (function getFileIndex$(fname) {
  /* get-file-index manager/js/searchlogic.sib:37:0 */

  var idxRtn = 0;
  return (function() {
    var while$1 = undefined;
    while (idxRtn < arrPres.length) {
      while$1 = (function() {
        var pres = arrPres[idxRtn];
        (function() {
          if (pres) {
            var matchFname = pres.href;
            return (function() {
              if (fname === matchFname) {
                console.log("RETURNING ", idxRtn);
                return idxRtn;
              }
            }).call(this);
          }
        }).call(this);
        return ((idxRtn)++);
      }).call(this);
    };
    return while$1;
  }).call(this);
});
var runNaiveSearch = (function runNaiveSearch$(entryList) {
  /* run-naive-search manager/js/searchlogic.sib:49:0 */

  return (function() {
    /* manager/js/searchlogic.sib:51:11 */
  
    var lastFileIndex = 0;
    var stat = { found: 0 };
    entryList.forEach((function(entry, idxEntry) {
      /* manager/js/searchlogic.sib:54:13 */
    
      var entryId = makeEntryId(entry);
      var curResult = (allResult[entryId] || {  });
      return (curResult.score) ? (function() {
        /* manager/js/searchlogic.sib:60:21 */
      
        return console.log("%cALREADY FOUND!!!", "background:black;color:red;font-weight:bold;");
      }).call(this) : (function() {
        /* manager/js/searchlogic.sib:65:21 */
      
        // console.log(("searching for string in entry " + (1 + idxEntry) + " out of " + entryList.length + ", starting at " + lastFileIndex));
        var searchString = cleanString(entry.highlight);
        return arrPres.slice(lastFileIndex).forEach((function(pres, presOffset) {
          /* manager/js/searchlogic.sib:73:22 */
        
          var foundIndex = htmlMap[pres.id].indexOf(searchString);
          return (function() {
            if (-1 < foundIndex) {
              console.log(("FOUND IT at " + foundIndex));
              stat.found = (1 + stat.found);
              lastFileIndex = (lastFileIndex + presOffset);
              return allResult[entryId] = makeResult(foundIndex, 1, pres.href);
            }
          }).call(this);
        }));
      }).call(this);
    }));
    return console.log(("TOTAL: " + stat.found));
  }).call(this);
});
var runTokenizedSearch = (function runTokenizedSearch$(entryList) {
  /* run-tokenized-search manager/js/searchlogic.sib:85:0 */

  var total = 0;
  var reWhitespace = (new RegExp("\\s+"));
  var fileStartIndex = 0;
  entryList.forEach((function(entry) {
    /* manager/js/searchlogic.sib:95:11 */
  
    (function() {
      if (maybeResult(entry)) {
        ((total)++);
        return ;
      }
    }).call(this);
    var entryId = makeEntryId(entry);
    var searchString = cleanString(entry.highlight);
    var tokenList = searchString.split(reWhitespace);
    var checkLength = (2 * searchString.length);
    var safety = 1000;
    var substring = null;
    var niter = 0;
    // console.log("SEARCHING FOR:", searchString);
    var break0 = false,
        i = fileStartIndex;
    return (function() {
      var while$2 = undefined;
      while ((i < arrPres.length && !(break0))) {
        while$2 = (function() {
          var fileIndex = i;
          var pres = arrPres[fileIndex];
          ((i)++);
          (function() {
            if ((11 < i && i < 15)) {
              return console.log("...", fileIndex, pres.href);
            }
          }).call(this);
          var offset = 0;
          var fullHtml = htmlMap[pres.id];
          var fullText = cleanString(striptags(fullHtml)).replace((new RegExp("\\s+", "g")), " ");
          var matchIdx = fullText.indexOf(searchString);
          var break1 = false;
          return (function() {
            var while$3 = undefined;
            while ((offset < fullText.length && !(break1))) {
              while$3 = (function() {
                ((niter)++);
                (function() {
                  if (safety < niter) {
                    console.log(("%cOUT OF CONTROL: " + niter), "color:white;background:red;");
                    offset = fullText.length;
                    break1 = true;
                    return ;
                  }
                }).call(this);
                var leadToken = tokenList[0];
                // console.log(("looking for: " + leadToken + " in: %c#" + fullText.substring(offset, (offset + 50)) + "#"), "color:gray;");
                var matchIndex = fullText.substr(offset).indexOf(leadToken);
                (function() {
                  if (-1 === matchIndex) {
                    // console.log((".   no more to search from %c" + pres.href + ". %cQUIT"), "font-weight:bold;", "font-weight:normal");
                    break1 = true;
                    return ;
                  }
                }).call(this);
                var foundIndex = (offset + matchIndex);
                var endIndex = (foundIndex + checkLength);
                substring = "";
                var break2 = false;
                (function() {
                  var while$4 = undefined;
                  while ((substring.length < checkLength && !(break2))) {
                    while$4 = (function() {
                      substring = fullText.substring(foundIndex, endIndex);
                      (function() {
                        if (fullText.length < endIndex) {
                          break2 = true;
                          return ;
                        }
                      }).call(this);
                      return endIndex += checkLength;
                    }).call(this);
                  };
                  return while$4;
                }).call(this);
                return (-1 === substring.indexOf(tokenList.slice(-1)[0])) ? (function() {
                  /* manager/js/searchlogic.sib:197:34 */
                
                  return offset = (foundIndex + leadToken.length);
                }).call(this) : (function() {
                  /* manager/js/searchlogic.sib:200:34 */
                
                  var hitCount = getCorpusCoverage(substring, tokenList);
                  var score = (hitCount / tokenList.length);
                  return (0.7 < score) ? (function() {
                    /* manager/js/searchlogic.sib:207:44 */
                  
                    console.log("%c   OK!   ", "color:white;background:lime;");
                    allResult[entryId] = makeResult(offset, score, pres.href);
                    fileStartIndex = fileIndex;
                    break0 = true;
                    break1 = true;
                    return ;
                  }).call(this) : (function() {
                    /* manager/js/searchlogic.sib:214:44 */
                  
                    return offset = (foundIndex + leadToken.length);
                  }).call(this);
                }).call(this);
              }).call(this);
            };
            return while$3;
          }).call(this);
        }).call(this);
      };
      return while$2;
    }).call(this);
  }));
  return console.log(("TOTAL: " + total));
});