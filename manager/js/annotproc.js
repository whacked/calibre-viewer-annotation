var acache = {
  data: {  },
  loadForTitle: (function(title) {
    /* manager/js/annotproc.sib:3:30 */
  
    return (function() {
      if (!(acache.data[title])) {
        var collection = [];
        acache.data[title] = collection;
        return aDb.serialize((function() {
          /* manager/js/annotproc.sib:8:39 */
        
          return aDb.each(aSql.getFullAnnotationsWithTitleLike(title), (function(err, row) {
            /* manager/js/annotproc.sib:10:51 */
          
            return collection.push(row);
          }));
        }));
      }
    }).call(this);
  }),
  findMatch: (function(title, rngMatch) {
    /* manager/js/annotproc.sib:12:26 */
  
    var result = null,
        searchList = acache.data[title],
        i = 0;
    (function() {
      var while$1 = undefined;
      while ((searchList && !(result) && i < searchList.length)) {
        while$1 = (function() {
          var dbrow = searchList[i];
          (function() {
            if ((dbrow.start === rngMatch.start && dbrow.startOffset === rngMatch.startOffset && dbrow.end === rngMatch.end && dbrow.endOffset === rngMatch.endOffset)) {
              return result = dbrow;
            }
          }).call(this);
          return ((i)++);
        }).call(this);
      };
      return while$1;
    }).call(this);
    return result;
  })
};
var processEpub = (function processEpub$(epub) {
  /* process-epub manager/js/annotproc.sib:28:0 */

  console.log("PROCESSING EPUB!");
  var htmlMatch = (new RegExp("\\.htm.+$"));
  arrPres = [];
  htmlMap = {  };
  Object.keys(epub.manifest).forEach((function(key) {
    /* manager/js/annotproc.sib:33:5 */
  
    var pres = epub.manifest[key];
    return (function() {
      if (pres.href.match(htmlMatch)) {
        return arrPres.push(pres);
      }
    }).call(this);
  }));
  console.log(("finished processing epub manifest, length: " + arrPres.length));
  return arrPres.forEach((function(pres, entryIndex) {
    /* manager/js/annotproc.sib:39:5 */
  
    return epub.getFile(pres.id, (function(err, data, mimetype) {
      /* manager/js/annotproc.sib:48:12 */
    
      console.log("GOT FILE ", pres.id);
      htmlMap[pres.id] = data.toString("utf8");
      spineMap[pres.href] = (1 + entryIndex);
      return (function() {
        if (Object.keys(htmlMap).length === arrPres.length) {
          console.log("OK, READY.");
          m.startComputation();
          arrPres.sort((function(a, b) {
            /* manager/js/annotproc.sib:59:21 */
          
            return (getNumeric(a.href) - getNumeric(b.href));
          }));
          runNaiveSearch(mResult.vm.entryList());
          runTokenizedSearch(mResult.vm.entryList());
          mResult.vm.entryList().forEach((function(entry) {
            /* manager/js/annotproc.sib:66:20 */
          
            return (function() {
              if (!(maybeResult(entry))) {
                return failureList.push(entry.highlight);
              }
            }).call(this);
          }));
          console.log((Object.keys(allResult).length + " found, " + failureList.length + " failures (" + mResult.vm.entryList().length + " total)"));
          return m.endComputation();
        }
      }).call(this);
    }));
  }));
});
var launchAndFind = (function launchAndFind$(sourceFilepath, entry) {
  /* launch-and-find manager/js/annotproc.sib:84:0 */

  mySourceFilepath = sourceFilepath;
  myEntry = entry;
  var sourceFilepath = mySourceFilepath,
      entry = myEntry;
  console.clear();
  var panel = document.getElementById("matcher-panel");
  panel.innerHTML = "";
  var ifr = document.createElement("iframe");
  ifr.setAttribute("id", "matcher-window");
  panel.appendChild(ifr);
  console.log("LAUNCH AND FIND!", sourceFilepath);
  var doc = ifr.contentWindow.document;
  doc.open();
  doc.write(getSourceHtml(sourceFilepath).replace((new RegExp("</head>", undefined)), ("<script type=\"text/javascript\">" + fs.readFileSync(cfijsPath, "utf-8") + "</script></html>")));
  doc.close();
  var ifr = document.getElementById("matcher-window"),
      ifrWindow = (ifr.contentWindow || ifr);
  return ifr.onload = (function() {
    /* manager/js/annotproc.sib:119:6 */
  
    var searchString = cleanString(entry.highlight);
    (function() {
      if (ifrWindow.find(searchString)) {
        return null;
      } else if (true) {
        var sel = ifrWindow.getSelection(),
            searchLength = searchString.length,
            finished__QUERY = false;
        (function() {
          var while$4 = undefined;
          while ((!(finished__QUERY) && searchLength > 1)) {
            while$4 = (function() {
              ((searchLength)--);
              return (function() {
                if (ifrWindow.find(searchString.substr(0, searchLength))) {
                  console.log(("breaking from start find on iter: " + searchLength));
                  finished__QUERY = true;
                  return ;
                }
              }).call(this);
            }).call(this);
          };
          return while$4;
        }).call(this);
        var rng = ifrWindow.getSelection().getRangeAt(0),
            startNode = rng.startContainer,
            startOffset = rng.startOffset;
        sel.removeAllRanges();
        var finished__QUERY = false,
            startIndex = 1;
        (function() {
          var while$5 = undefined;
          while ((!(finished__QUERY) && startIndex < searchString.length)) {
            while$5 = (function() {
              ((startIndex)++);
              return (function() {
                if (ifrWindow.find(searchString.substr(startIndex))) {
                  console.log(("breaking from end find on iter: " + startIndex));
                  finished__QUERY = true;
                  return ;
                }
              }).call(this);
            }).call(this);
          };
          return while$5;
        }).call(this);
        var rng = ifrWindow.getSelection().getRangeAt(0),
            endNode = rng.endContainer,
            endOffset = rng.endOffset;
        sel.removeAllRanges();
        var finalRange = ifrWindow.document.createRange();
        finalRange.setStart(startNode, startOffset);
        finalRange.setEnd(endNode, endOffset);
        return sel.addRange(finalRange);
      }
    }).call(this);
    var sel = ifrWindow.getSelection(),
        verifString = sel.toString(),
        verifTokenList = verifString.split(reWhitespace),
        coverageHitCount = getCorpusCoverage(entry.highlight, verifTokenList),
        coverageScore = (coverageHitCount / verifTokenList.length),
        curScrollX = window.scrollX,
        curScrollY = window.scrollY;
    setTimeout((function() {
      /* manager/js/annotproc.sib:197:8 */
    
      console.log("trigger scroll...");
      ifrWindow.scrollTo(0, (function() {
        /* manager/js/annotproc.sib:202:32 */
      
        var el = sel.anchorNode.parentNode,
            elRect = el.getBoundingClientRect(),
            absTop = (elRect.top + ifrWindow.pageYOffset);
        return (absTop - (ifrWindow.innerHeight / 4));
      }).call(this));
      return window.scrollTo(curScrollX, curScrollY);
    }), 200);
    var range = ifrWindow.getSelection().getRangeAt(0),
        bRange = (new Range.BrowserRange(range)),
        sRange = bRange.serialize(ifrWindow.document.body),
        ann = {
      uri: ("epub://" + sourceFilepath.split(path.sep).pop()),
      title: epub.metadata.title,
      created: entry.timestamp,
      quote: searchString,
      ranges: [ sRange.toObject() ],
      extras: { calibre_bookmark: {
        type: "cfi",
        pos: ifrWindow.cfi.at_current().replace((new RegExp("([^/]+)$")), ""),
        spine: spineMap[sourceFilepath]
      } }
    };
    (function() {
      if (entry.note) {
        return ann.note = entry.note;
      }
    }).call(this);
    output[entry.highlight] = ann;
    entry.verification({
      content: verifString,
      score: coverageScore,
      annotation: ann
    });
    var maybeInDb = acache.findMatch(mResult.vm.title(), ann.ranges[0]);
    (function() {
      if (maybeInDb) {
        return entry.dbEntry(maybeInDb);
      }
    }).call(this);
    m.endComputation();
    return console.log("DONE");
  });
});
var mFile = {
  vm: (function() {
    /* manager/js/annotproc.sib:295:10 */
  
    var vm = {  };
    vm.init = (function() {
      /* manager/js/annotproc.sib:298:19 */
    
      return vm.fileList = m.prop([]);
    });
    return vm;
  }).call(this),
  view: (function(ctrl) {
    /* manager/js/annotproc.sib:300:13 */
  
    return m("div.table", mFile.vm.fileList().map((function(fpath) {
      /* manager/js/annotproc.sib:303:24 */
    
      return m("div.tr", [ m("div.td", m("a", { onclick: (function() {
        /* manager/js/annotproc.sib:307:46 */
      
        m.startComputation();
        var fullPath = path.join(__dirname, "..", "kindle-highlights", fpath);
        mFcontent.vm.filePath(fullPath);
        mFcontent.vm.content(fs.readFileSync(fullPath, "utf-8"));
        var yml = jsyaml.safeLoad(mFcontent.vm.content()),
            mEntryList = [];
        yml.highlight_list.sort((function(a, b) {
          /* manager/js/annotproc.sib:320:60 */
        
          return (a.startLocation - b.startLocation);
        })).forEach((function(entry) {
          /* manager/js/annotproc.sib:319:47 */
        
          return mEntryList.push((new mEntry(entry)));
        }));
        mResult.vm.title(yml.title);
        mResult.vm.entryList(mEntryList);
        acache.loadForTitle(yml.title);
        cDb.serialize((function() {
          /* manager/js/annotproc.sib:326:48 */
        
          cDb.each(cSql.getEpubPathInfoByTitle(("%" + mResult.vm.title() + "%")), (function(err, row) {
            /* manager/js/annotproc.sib:329:50 */
          
            console.log(row);
            var epubFilepath = path.join($CALIBRE_HOME, row.path, (row.name + ".epub"));
            epub = (new EPub(epubFilepath, "imagewebroot_ignore", "chapterwebroot_ignore"));
            epub.on("end", (function() {
              /* manager/js/annotproc.sib:340:73 */
            
              return processEpub(epub);
            }));
            return epub.parse();
          }));
          return yml.highlight_list = mResult.vm.entryList();
        }));
        return m.endComputation();
      }) }, fpath)) ]);
    })));
  })
};
m.mount(document.getElementById("file-panel"), {
  controller: mFile.vm.init,
  view: mFile.view
});
fs.readdir(path.resolve(path.join(__dirname, "..", "kindle-highlights")), (function(err, fileList) {
  /* manager/js/annotproc.sib:362:1 */

  m.startComputation();
  var filteredList = [],
      reYml = (new RegExp("yml$"));
  fileList.forEach((function(fpath) {
    /* manager/js/annotproc.sib:366:3 */
  
    return (function() {
      if (fpath.match(reYml)) {
        return filteredList.push(fpath);
      }
    }).call(this);
  }));
  mFile.vm.fileList(filteredList);
  return m.endComputation();
}));