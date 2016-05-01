(function() {
  /* manager/js/app.sib:3:0 */

  var allLink = document.getElementsByTagName("link"),
      i = 0;
  return (function() {
    var while$1 = undefined;
    while (i < allLink.length) {
      while$1 = (function() {
        var link = allLink[i];
        (function() {
          if (-1 < link.getAttribute("type").indexOf("css")) {
            console.log("reload ", link);
            return link.href = (link.href + "?t=" + (new Date()).getTime());
          }
        }).call(this);
        return ((i)++);
      }).call(this);
    };
    return while$1;
  }).call(this);
}).call(this);
var Range = (function(data) {
  /* manager/js/app.sib:16:11 */

  this.id = data.id;
  this.start = data.start;
  this.end = data.end;
  this.startOffset = data.startOffset;
  this.endOffset = data.endOffset;
  this.annotation = data.annotation;
  return this;
}),
    Annotation = (function(data) {
  /* manager/js/app.sib:25:16 */

  this.id = data.id;
  this.uri = data.uri;
  this.title = data.title;
  this.text = data.text;
  this.quote = data.quote;
  this.user = data.user;
  this.extras = data.extras;
  this.created = data.created;
  this.updated = data.updated;
  this._extras = JSON.parse(data.extras);
  this._ranges = null;
  this.getRanges = (function() {
    /* manager/js/app.sib:38:32 */
  
    (function() {
      if (this._ranges) {
        return this._ranges;
      }
    }).call(this);
    return this._ranges = [ "STUFF" ];
  });
  this.getExtras = (function(key) {
    /* manager/js/app.sib:43:32 */
  
    return this._extras[key];
  });
  return this;
});
var Book = (function(data) {
  /* manager/js/app.sib:48:5 */

  this.id = data.id;
  this.title = data.title;
  this.sort = data.sort;
  this.timestamp = data.timestamp;
  this.pubdate = data.pubdate;
  this.series_index = data.series_index;
  this.author_sort = data.author_sort;
  this.isbn = data.isbn;
  this.lccn = data.lccn;
  this.path = data.path;
  this.flags = data.flags;
  this.uuid = data.uuid;
  this.has_cover = data.has_cover;
  this.last_modified = data.last_modified;
  return this;
});
var mAnnot = { view: (function(ctrl, ann) {
  /* manager/js/app.sib:66:19 */

  return m("div.tr", [ m("div.td .date-string", ann.created.toString().substr(0, 10)), m("div.td", ann.text), m("div.td", ann.quote) ]);
}) };
var mAnn = {
  vm: (function() {
    /* manager/js/app.sib:74:16 */
  
    var vm = {  };
    vm.init = (function() {
      /* manager/js/app.sib:77:25 */
    
      vm.book = m.prop(null);
      vm.list = m.prop([]);
      vm.query = m.prop("");
      return vm.ignorecase = m.prop(true);
    });
    return vm;
  }).call(this),
  controller: (function() {
    /* manager/js/app.sib:83:25 */
  
    return mAnn.vm.init();
  }),
  view: (function() {
    /* manager/js/app.sib:84:19 */
  
    var book = mAnn.vm.book();
    return (book) ? m("div", [ m("h3", [ book.title, " ", m("button[type=button]", { onclick: (function() {
      /* manager/js/app.sib:91:63 */
    
      return findAndOpenEpubById(book.id);
    }) }, "open") ]), m("div", [ m("input", {
      onkeyup: m.withAttr("value", mAnn.vm.query),
      value: mAnn.vm.query()
    }), m("label", [ m("input[type=checkbox]", {
      onclick: m.withAttr("checked", mAnn.vm.ignorecase),
      checked: mAnn.vm.ignorecase()
    }), "case insensitive search" ]) ]), m("div.table", (function() {
      /* manager/js/app.sib:105:44 */
    
      var rtn = [ m("div.tr", [ m("div.th", "date"), m("div.th", "text"), m("div.th", "quote") ]) ],
          RE = (new RegExp(mAnn.vm.query(), (mAnn.vm.ignorecase()) ? "i" : ""));
      mAnn.vm.list().forEach((function(ann) {
        /* manager/js/app.sib:113:45 */
      
        return (function() {
          if (((ann.quote && ann.quote.match(RE)) || (ann.text && ann.text.match(RE)))) {
            return rtn.push(m.component(mAnnot, ann));
          }
        }).call(this);
      }));
      return rtn;
    }).call(this)) ]) : m("div", "select a book");
  })
};
m.mount(document.getElementById("annotation-panel"), {
  controller: mAnn.controller,
  view: mAnn.view
});
var refreshAnnotationList = (function refreshAnnotationList$() {
  /* refresh-annotation-list manager/js/app.sib:125:0 */

  var book = mAnn.vm.book();
  return (function() {
    if (book) {
      return aDb.serialize((function() {
        /* manager/js/app.sib:129:12 */
      
        m.startComputation();
        var annList = [];
        return aDb.each(aSql.getAnnotationsWithTitleLike({ title: ("%" + book.title + "%") }), (function(err, row) {
          /* manager/js/app.sib:133:24 */
        
          return annList.push((new Annotation(row)));
        }), (function() {
          /* manager/js/app.sib:136:24 */
        
          console.log(annList.length);
          mAnn.vm.list(annList);
          return m.endComputation();
        }));
      }));
    }
  }).call(this);
});
var findAndOpenEpubById = (function findAndOpenEpubById$(bookId) {
  /* find-and-open-epub-by-id manager/js/app.sib:143:0 */

  return cDb.serialize((function() {
    /* manager/js/app.sib:145:6 */
  
    return cDb.each(cSql.getEpubPathInfoById(bookId), (function(err, row) {
      /* manager/js/app.sib:147:18 */
    
      var epubFilepath = path.join($CALIBRE_HOME, row.path, (row.name + ".epub"));
      console.log(("opening: " + epubFilepath + "..."));
      return (function() {
        try {
          return (function() {
            /* manager/js/app.sib:155:27 */
          
            fs.statSync(epubFilepath);
            return exec(("ebook-viewer '" + epubFilepath + "'"));
          }).call(this);
        } catch (e) {
          return ;
        }
      }).call(this);
    }));
  }));
});
var mBook = { view: (function(ctrl, book) {
  /* manager/js/app.sib:159:18 */

  var activeBook = mAnn.vm.book();
  return m("div.tr", [ m("div.td .book-id", book.id), m("div.td", [ ((activeBook && activeBook.title === book.title)) ? m("b", book.title) : m("a", {
    href: "#",
    onclick: (function(evt) {
      /* manager/js/app.sib:170:58 */
    
      mAnn.vm.book(book);
      return refreshAnnotationList();
    })
  }, book.title) ]), m("div.td", book.author_sort) ]);
}) };
var mBk = {
  vm: (function() {
    /* manager/js/app.sib:176:15 */
  
    var vm = {  };
    vm.init = (function() {
      /* manager/js/app.sib:179:25 */
    
      vm.list = m.prop([]);
      vm.query = m.prop("");
      return vm.ignorecase = m.prop(true);
    });
    return vm;
  }).call(this),
  controller: (function() {
    /* manager/js/app.sib:184:24 */
  
    return mBk.vm.init();
  }),
  view: (function() {
    /* manager/js/app.sib:185:18 */
  
    return m("div", [ m("h3", "search for books in calibre DB"), m("div", [ m("input", {
      onkeyup: m.withAttr("value", mBk.vm.query),
      value: mBk.vm.query()
    }), m("label", [ m("input[type=checkbox]", {
      onclick: m.withAttr("checked", mBk.vm.ignorecase),
      checked: mBk.vm.ignorecase()
    }), "case insensitive search" ]) ]), m("div.table", (function() {
      /* manager/js/app.sib:198:39 */
    
      var RE = (new RegExp(mBk.vm.query(), (mBk.vm.ignorecase()) ? "i" : "")),
          rtn = [];
      mBk.vm.list().forEach((function(book) {
        /* manager/js/app.sib:202:40 */
      
        return (function() {
          if ((book.title.match(RE) || book.author_sort.match(RE))) {
            return rtn.push(m.component(mBook, book));
          }
        }).call(this);
      }));
      return rtn;
    }).call(this)) ]);
  })
};
m.mount(document.getElementById("book-panel"), {
  controller: mBk.controller,
  view: mBk.view
});
var loadBookList = (function loadBookList$() {
  /* load-book-list manager/js/app.sib:213:0 */

  return cDb.serialize((function() {
    /* manager/js/app.sib:215:6 */
  
    console.log("loading books...");
    m.startComputation();
    var bookList = [];
    return cDb.each(cSql.getAllEpubBooks(), (function(err, row) {
      /* manager/js/app.sib:220:18 */
    
      return bookList.push((new Book(row)));
    }), (function() {
      /* manager/js/app.sib:223:18 */
    
      mBk.vm.list(bookList);
      return m.endComputation();
    }));
  }));
});
var mTab = {
  vm: (function() {
    /* manager/js/app.sib:232:10 */
  
    var vm = { panelList: [] };
    vm.init = (function() {
      /* manager/js/app.sib:235:19 */
    
      var i = 0,
          elList = document.getElementsByClassName("tab-panel");
      return (function() {
        var while$2 = undefined;
        while (i < elList.length) {
          while$2 = (function() {
            var panel = elList[i];
            mTab.vm.panelList.push(panel);
            return ((i)++);
          }).call(this);
        };
        return while$2;
      }).call(this);
    });
    return vm;
  }).call(this),
  view: (function(ctrl) {
    /* manager/js/app.sib:244:13 */
  
    return m("ul", (function() {
      /* manager/js/app.sib:246:18 */
    
      var body = [];
      mTab.vm.panelList.forEach((function(panel) {
        /* manager/js/app.sib:248:19 */
      
        var panelId = panel.getAttribute("id");
        return body.push(m("li", { onclick: (function(evt) {
          /* manager/js/app.sib:251:49 */
        
          var i = 0,
              swList = evt.target.parentNode.childNodes;
          (function() {
            var while$3 = undefined;
            while (i < swList.length) {
              while$3 = (function() {
                swList[i].setAttribute("class", "");
                return ((i)++);
              }).call(this);
            };
            return while$3;
          }).call(this);
          evt.target.setAttribute("class", "active");
          return mTab.vm.panelList.forEach((function(p) {
            /* manager/js/app.sib:259:51 */
          
            return p.setAttribute("class", "tab-panel".concat((panelId === p.getAttribute("id")) ? " active" : ""));
          }));
        }) }, panelId));
      }));
      return body;
    }).call(this));
  })
};
m.mount(document.getElementById("tab-switcher"), {
  controller: mTab.vm.init,
  view: mTab.view
});
loadBookList();
var EPub = require("epub"),
    striptags = require("striptags"),
    jsyaml = require("js-yaml"),
    entities = (function() {
  /* manager/js/app.sib:281:15 */

  var Entities = require("html-entities").AllHtmlEntities;
  return (new Entities());
}).call(this),
    Range = require("xpath-range").Range;
var epub = null,
    yml = null,
    failureList = [],
    arrPres = [],
    htmlMap = {  },
    spineMap = {  },
    reWhitespace = (new RegExp("\\s+")),
    output = {  },
    cfijsPath = path.join(__dirname, "js", "cfi.js"),
    yml = { highlight_list: [] };
var saveOutputToFile = (function saveOutputToFile$(filepath) {
  /* save-output-to-file manager/js/app.sib:307:0 */

  return (function() {
    if (filepath) {
      console.log(("saving " + Object.keys(output).length + " items to " + filepath));
      return fs.writeFile(filepath, JSON.stringify(output, null, 2));
    } else if (true) {
      return dialog.showSaveDialog((function(filepath) {
        /* manager/js/app.sib:316:10 */
      
        return (function() {
          if (filepath) {
            return saveOutputToFile(filepath);
          }
        }).call(this);
      }));
    }
  }).call(this);
});
var mEntry = (function(data) {
  /* manager/js/app.sib:320:12 */

  return {
    asin: data.asin,
    customerId: data.customerId,
    embeddedId: data.embeddedId,
    endLocation: data.endLocation,
    highlight: data.highlight,
    howLongAgo: data.howLongAgo,
    startLocation: data.startLocation,
    timestamp: data.timestamp,
    note: data.note,
    verification: m.prop({  }),
    dbEntry: m.prop(null)
  };
});
var mFcontent = {
  vm: (function() {
    /* manager/js/app.sib:339:10 */
  
    var vm = {  };
    vm.init = (function() {
      /* manager/js/app.sib:342:19 */
    
      vm.filePath = m.prop(null);
      return vm.content = m.prop(null);
    });
    return vm;
  }).call(this),
  view: (function(ctrl) {
    /* manager/js/app.sib:345:13 */
  
    return m("div", (function() {
      /* manager/js/app.sib:347:18 */
    
      var fc = mFcontent.vm.content(),
          body = [];
      body.push(m("pre", (fc) ? ("selected: " + mResult.vm.title() + "; file length: " + fc.length) : "select a file"));
      return body;
    }).call(this));
  })
};
m.mount(document.getElementById("file-content"), {
  controller: mFcontent.vm.init,
  view: mFcontent.view
});
var reconcilerInterval = 500,
    reconcilerTimer = null;
var reconcileAll = (function reconcileAll$() {
  /* reconcile-all manager/js/app.sib:367:0 */

  var i = 0,
      bookTitle = mResult.vm.title(),
      entryList = mResult.vm.entryList(),
      checkProc = (function() {
    /* manager/js/app.sib:371:21 */
  
    console.log(i);
    var entry = entryList[i],
        verf = entry.verification(),
        maybeMatch = null;
    (function() {
      if (verf.annotation) {
        return maybeMatch = acache.findMatch(bookTitle, verf.annotation.ranges[0]);
      }
    }).call(this);
    console.log("MAYBE?");
    console.log(maybeMatch);
    (function() {
      if (maybeMatch) {
        return console.log(("%calready in db, skipping:%c " + entry.highlight), "color:white;background:green;", "color:none;");
      } else if (true) {
        var entryId = makeEntryId(entry),
            result = allResult[entryId];
        return (function() {
          if ((result && result.source)) {
            return launchAndFind(result.source, entry);
          }
        }).call(this);
      }
    }).call(this);
    ((i)++);
    return (function() {
      if (i < entryList.length) {
        console.log(("running" + (1 + i) + " of " + entryList.length));
        return reconcilerTimer = setTimeout(checkProc, reconcilerInterval);
      } else if (true) {
        return m.endComputation();
      }
    }).call(this);
  });
  m.startComputation();
  return reconcilerTimer = setTimeout(checkProc, reconcilerInterval);
});
var mResult = {
  hdrList: [ "check?", "info", "highlight", "note", "verification", "in db?" ],
  vm: (function() {
    /* manager/js/app.sib:413:11 */
  
    var vm = {  };
    vm.init = (function() {
      /* manager/js/app.sib:416:20 */
    
      vm.title = m.prop(null);
      return vm.entryList = m.prop([]);
    });
    return vm;
  }).call(this),
  view: (function(ctrl) {
    /* manager/js/app.sib:420:13 */
  
    var vm = mResult.vm;
    return m("div", [ m("button", { onclick: (function() {
      /* manager/js/app.sib:424:32 */
    
      return reconcileAll();
    }) }, "RECONCILE ALL"), m("button", { onclick: (function() {
      /* manager/js/app.sib:427:33 */
    
      return clearInterval(reconcilerTimer);
    }) }, "terminate reconcilation process"), m("button", { onclick: (function() {
      /* manager/js/app.sib:430:33 */
    
      return saveOutputToFile();
    }) }, "save output to file"), m("div", m("table", (function() {
      /* manager/js/app.sib:435:24 */
    
      var body = [ m("tr", mResult.hdrList.map((function(k) {
        /* manager/js/app.sib:436:68 */
      
        return m("th", k);
      }))) ];
      vm.entryList().forEach((function(entry) {
        /* manager/js/app.sib:437:25 */
      
        var entryId = makeEntryId(entry),
            result = (allResult[entryId] || {  });
        return body.push(m("tr", mResult.hdrList.map((function(hdr) {
          /* manager/js/app.sib:443:36 */
        
          var entryVal = entry[hdr],
              score = result.score;
          return m("td", (function() {
            if (hdr === "check?") {
              return m("button", { onclick: (function() {
                /* manager/js/app.sib:449:58 */
              
                console.log("CLICK CHECK!");
                console.log(result);
                return (function() {
                  if (result.source) {
                    console.log(entry);
                    m.startComputation();
                    return launchAndFind(result.source, entry);
                  }
                }).call(this);
              }) }, "check");
            } else if (hdr === "info") {
              return m("div", [ ((score && 0 < score)) ? (function() {
                /* manager/js/app.sib:462:58 */
              
                return m("div", { class: "yes-found" }, ("" + score.toFixed(3) + " " + result.source));
              }).call(this) : m("div", { class: "not-found" }), m("div", ("" + entry.startLocation + "~" + entry.endLocation + " (" + (entry.endLocation - entry.startLocation) + ")")), m("div", (new Date(entry.timestamp)).toString()) ]);
            } else if (hdr === "verification") {
              return (function() {
                /* manager/js/app.sib:482:45 */
              
                var verf = entry.verification();
                return m("div", {
                  id: ("td-sel-" + entryId),
                  class: "td-sel",
                  style: { backgroundColor: (verf.score) ? score2rgb(verf.score) : "" }
                }, verf.content);
              }).call(this);
            } else if (hdr === "in db?") {
              return m("div", (function() {
                /* manager/js/app.sib:494:48 */
              
                var dbEntry = entry.dbEntry(),
                    verf = entry.verification();
                return (function() {
                  if (dbEntry) {
                    return dbEntry.quote;
                  } else if (verf.annotation) {
                    return m("button", { onclick: (function() {
                      /* manager/js/app.sib:502:66 */
                    
                      m.startComputation();
                      var newAnnotation = {
                        created: (new Date(entry.timestamp)).toISOString().replace((new RegExp("T", undefined)), " "),
                        updated: (new Date()).toISOString().replace((new RegExp("T", undefined)), " "),
                        title: verf.annotation.title,
                        text: entry.note,
                        quote: entry.highlight,
                        extras: verf.annotation.extras,
                        uri: verf.annotation.uri,
                        user: $USERNAME
                      };
                      return aDb.serialize((function() {
                        /* manager/js/app.sib:517:68 */
                      
                        aDb.run(aSql.insertAnnotation().replace((new RegExp("null", "g")), "?"), [ newAnnotation.created, newAnnotation.updated, newAnnotation.title, newAnnotation.text, newAnnotation.quote, JSON.stringify(newAnnotation.extras), newAnnotation.uri, newAnnotation.user ]);
                        return aDb.serialize((function() {
                          /* manager/js/app.sib:534:70 */
                        
                          return aDb.get(aSql.getLastInsertedId(), (function(err, row) {
                            /* manager/js/app.sib:536:81 */
                          
                            console.log("INSERTED:", row.id);
                            newAnnotation.id = row.id;
                            var rng = verf.annotation.ranges[0],
                                sql = aSql.appendRangeToAnnotation({
                              start: rng.start,
                              end: rng.end,
                              startOffset: rng.startOffset,
                              endOffset: rng.endOffset,
                              annotation_id: newAnnotation.id
                            });
                            console.log(sql);
                            return aDb.run(sql, (function(err, row) {
                              /* manager/js/app.sib:549:93 */
                            
                              entry.dbEntry(newAnnotation);
                              m.endComputation();
                              return console.log("OK!!!!");
                            }));
                          }));
                        }));
                      }));
                    }) }, "add to db");
                  } else if (true) {
                    return "";
                  }
                }).call(this);
              }).call(this));
            } else if (true) {
              return m("div", (entryVal) ? m.trust(entryVal) : "");
            }
          }).call(this));
        }))));
      }));
      return body;
    }).call(this))) ]);
  })
};
m.mount(document.getElementById("result-display"), {
  controller: mResult.vm.init,
  view: mResult.view
});
var getSourceHtml = (function getSourceHtml$(sourcePath) {
  /* get-source-html manager/js/app.sib:578:0 */

  var rtn = null;
  arrPres.forEach((function(pres) {
    /* manager/js/app.sib:580:5 */
  
    (function() {
      if (rtn) {
        return ;
      }
    }).call(this);
    return (function() {
      if (pres.href === sourcePath) {
        return rtn = htmlMap[pres.id];
      }
    }).call(this);
  }));
  return rtn;
});