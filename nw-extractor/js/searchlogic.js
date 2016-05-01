var DEBUG_LEVEL = 10;
var consoleLogOrig = console.log;
var dlog = (function dlog$(argv) {
  /* dlog eval.sibilant:6:0 */

  var argv = Array.prototype.slice.call(arguments, 0);

  return (function() {
    if (0 < DEBUG_LEVEL) {
      return consoleLogOrig.apply(console, argv);
    }
  }).call(this);
});
eval("console.log = dlog");
var arrPres = [];
var htmlMap = {  };
var allResult = {  };
var makeResult = (function makeResult$(index, score, sourceFile) {
  /* make-result eval.sibilant:25:0 */

  return {
    index: index,
    score: score,
    source: sourceFile
  };
});
var maybeResult = (function maybeResult$(entry) {
  /* maybe-result eval.sibilant:28:0 */

  return allResult[makeEntryId(entry)];
});
var getFileIndex = (function getFileIndex$(fname) {
  /* get-file-index eval.sibilant:32:0 */

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
var loadAllPublicationResource = (function loadAllPublicationResource$() {
  /* load-all-publication-resource eval.sibilant:44:0 */

  var htmlFileMatch = (new RegExp("\.htm.$"));
  Object.keys(epub.manifest).forEach((function(key) {
    /* eval.sibilant:46:5 */
  
    var pres = epub.manifest[key];
    return (function() {
      if (pres.href.match(htmlFileMatch)) {
        return arrPres.push(pres);
      }
    }).call(this);
  }));
  console.log(("finished processing epub manifest, length: " + arrPres.length));
  return arrPres.forEach((function(pres, idx) {
    /* eval.sibilant:53:5 */
  
    return epub.getFile(pres.id, (function(err, data, mimetype) {
      /* eval.sibilant:54:33 */
    
      htmlMap[pres.id] = data.toString("utf8");
      return console.log(("loaded: " + pres.id));
    }));
  }));
});
var runNaiveSearch = (function runNaiveSearch$() {
  /* run-naive-search eval.sibilant:60:0 */

  return (function() {
    /* eval.sibilant:61:5 */
  
    var lastFileIndex = 0;
    var stat = { found: 0 };
    yml.highlight_list.forEach((function(entry, idxEntry) {
      /* eval.sibilant:64:13 */
    
      var entryId = makeEntryId(entry);
      var curResult = (allResult[entryId] || {  });
      return (curResult.score) ? (function() {
        /* eval.sibilant:70:21 */
      
        return console.log("%cALREADY FOUND!!!", "background:black;color:red;font-weight:bold;");
      }).call(this) : (function() {
        /* eval.sibilant:75:21 */
      
        // console.log(("searching for string in entry " + (1 + idxEntry) + " out of " + yml.highlight_list.length + ", starting at " + lastFileIndex));
        var searchString = cleanString(entry.highlight);
        return arrPres.slice(lastFileIndex).forEach((function(pres, presOffset) {
          /* eval.sibilant:83:22 */
        
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
var runTokenizedSearch = (function runTokenizedSearch$() {
  /* run-tokenized-search eval.sibilant:95:0 */

  var total = 0;
  var reWhitespace = (new RegExp("\\s+"));
  var fileStartIndex = 0;
  yml.highlight_list.forEach((function(entry) {
    /* eval.sibilant:105:11 */
  
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
                  /* eval.sibilant:207:34 */
                
                  return offset = (foundIndex + leadToken.length);
                }).call(this) : (function() {
                  /* eval.sibilant:210:34 */
                
                  var hitCount = getCorpusCoverage(substring, tokenList);
                  var score = (hitCount / tokenList.length);
                  return (0.7 < score) ? (function() {
                    /* eval.sibilant:217:44 */
                  
                    console.log("%c   OK!   ", "color:white;background:lime;");
                    allResult[entryId] = makeResult(offset, score, pres.href);
                    fileStartIndex = fileIndex;
                    break0 = true;
                    break1 = true;
                    return ;
                  }).call(this) : (function() {
                    /* eval.sibilant:224:44 */
                  
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
var monsterTimer = undefined;
var reconcileAll = (function reconcileAll$() {
  /* reconcile-all eval.sibilant:233:0 */

  var intervalTime = 150;
  var entryIndex = 0;
  return monsterTimer = setInterval((function() {
    /* eval.sibilant:238:14 */
  
    console.log(("working on entry " + (1 + entryIndex) + " of " + yml.highlight_list.length));
    (entryIndex < yml.highlight_list.length) ? (function() {
      /* eval.sibilant:243:24 */
    
      var entry = yml.highlight_list[entryIndex];
      var result = maybeResult(entry);
      (function() {
        if ((result && !(output[entry.highlight]))) {
          return launchAndFind(result.source, entry, intervalTime);
        }
      }).call(this);
      return ((entryIndex)++);
    }).call(this) : (function() {
      if (0 === n_active_search) {
        process.stdout.write("ALL DONE :D\n");
        clearInterval(monsterTimer);
        process.stdout.write(("wrote to " + JSON_OUT_PATH + "\n"));
        return fs.writeFile(JSON_OUT_PATH, JSON.stringify(output, null, 2));
      }
    }).call(this);
    return console.log((entryIndex + ", OK!"));
  }), intervalTime);
});