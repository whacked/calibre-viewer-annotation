#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2014, github.com/whacked'
__docformat__ = 'restructuredtext en'

# The class that all Interface Action plugin wrappers must inherit from
from calibre.customize import InterfaceActionBase
from calibre.customize import ViewerPlugin

from PyQt5.Qt import QStandardItem, QStandardItemModel
from calibre.ebooks.metadata.toc import TOC as MetaTOC
from calibre.gui2.viewer.toc import TOC, TOCItem, TOCSearch
import os
import json

from calibre.gui2.viewer.toc import TOCView
from calibre.gui2.search_box import SearchBox2
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.Qt import (
        QApplication, QWidget, QModelIndex,
        QPixmap, QIcon, QAction,
        QDockWidget, QVBoxLayout, pyqtSlot,
        )

from calibre_plugins.viewer_annotation import annotator_model as AModel
from calibre_plugins.viewer_annotation import annotator_store as AStore
from calibre_plugins.viewer_annotation.config import prefs
import types
import re

# init database + create tables if not exist
AStore.setup_database('sqlite:///%s' % prefs['annotator_db_path'])

DEBUG_LEVEL = 0
def dlog(*s):
    if DEBUG_LEVEL == 0:
        return
    for ss in s:
        print('[DLOG] ---> %s' % ss)

class AnnotationTOC(TOC):

    _filter = None

    def set_filter(self, flt):
        self._filter = flt
    def clear_filter(self):
        self._filter = None

    def update_current_annotation_list(self):
        self.clear()
        res = []
        toc = []
        for spine in self._spine_list:
            base_path, href = os.path.split(spine)
            dlog('updating annotation list for %s' % self.book_title)
            annot_resultset = json.loads(AStore.search_annotations(
                uri = AModel.Annotation.make_uri(href),
                title = self.book_title,
            ))
            # dlog('searching for: %s/%s' % (base_path, href))
            if annot_resultset["total"] > 0:
                for row in annot_resultset["rows"]:
                    annot = json.loads(AStore.read_annotation(str(row["id"])))
                    frag = (annot["uri"] + "#").split("#")[1]
                    text = annot.get("quote") or "(highlight)"
                
                    toc.append(MetaTOC(
                        href = href,
                        fragment = frag,
                        text = text,
                        base_path = base_path,
                        ))
                    ## HACK: store bookmark pos in the frag
                    toc[-1].bookmark = annot.get("calibre_bookmark", {})
        self.all_items = depth_first = []

        # set up TOC filter (based on search)
        filter_func = None
        if   self._filter is None:
            filter_func = lambda _: True
        elif type(self._filter) == types.FunctionType:
            filter_func = self._filter
        elif isinstance(self._filter, basestring):
            filter_func = re.compile('.*' + self._filter.lower() + '.*', re.IGNORECASE).match

        for t in toc:
            
            if filter_func:
                if not filter_func(t.text):
                    continue

            ti = TOCItem(self._spine_list, t, 0, depth_first)
            ti.bookmark = t.bookmark
            self.appendRow(ti)
        self.setHorizontalHeaderItem(0, QStandardItem(_('Notes')))

        for x in depth_first:
            possible_enders = [ t for t in depth_first if t.depth <= x.depth
                    and t.starts_at >= x.starts_at and t is not x and t not in
                    x.ancestors]
            if possible_enders:
                min_spine = min(t.starts_at for t in possible_enders)
                possible_enders = { t.fragment for t in possible_enders if
                        t.starts_at == min_spine }
            else:
                min_spine = len(self._spine_list) - 1
                possible_enders = set()
            x.ends_at = min_spine
            x.possible_end_anchors = possible_enders

        self.currently_viewed_entry = None

    def __init__(self, spine, book_title):
        QStandardItemModel.__init__(self)
        toc = []

        self.base_path = os.path.split(spine[0])[0]
        self.book_title = book_title
        self._spine_list = spine
        ## now populate the current notes 
        self.update_current_annotation_list()

    #def update_indexing_state(self, *args):
    #    items_being_viewed = []
    #    for t in self.all_items:
    #        t.update_indexing_state(*args)
    #        if t.is_being_viewed:
    #            items_being_viewed.append(t)
    #            self.currently_viewed_entry = t
    #    return items_being_viewed

    #def next_entry(self, spine_pos, anchor_map, viewport_rect, in_paged_mode,
    #        backwards=False, current_entry=None):
    #    current_entry = (self.currently_viewed_entry if current_entry is None
    #            else current_entry)
    #    if current_entry is None: return
    #    items = reversed(self.all_items) if backwards else self.all_items
    #    found = False

    #    if in_paged_mode:
    #        start = viewport_rect[0]
    #        anchor_map = {k:v[0] for k, v in anchor_map.iteritems()}
    #    else:
    #        start = viewport_rect[1]
    #        anchor_map = {k:v[1] for k, v in anchor_map.iteritems()}

    #    for item in items:
    #        if found:
    #            start_pos = anchor_map.get(item.start_anchor, 0)
    #            if backwards and item.is_being_viewed and start_pos >= start:
    #                # This item will not cause any scrolling
    #                continue
    #            if item.starts_at != spine_pos or item.start_anchor:
    #                return item
    #        if item is current_entry:
    #            found = True


class Responder(QtCore.QObject):
    @pyqtSlot(str, str)
    def AJAX(self, q_url, q_data_string):
        url = str(q_url)
        jsr = json.loads(str(q_data_string))
        request_type = jsr["type"]

        dlog("<AJAX REQUEST> %s %s" % (request_type, url))
        dlog(q_data_string)

        data = {}
        # data = json.loads(jsr["data"])

        should_update_annotation_list = False
        should_update_documentview = False

        document = self.parent()
        ebookviewer = document.parent().manager

        #read:    GET
        #search:  GET
        if request_type == "GET":
            dlog("GET %s" % url)
            if jsr["data"]:
                ## search request. by convention it probably ends with /search
                ## but who cares now
                ## document.bridge_value = AStore.search_annotations(uri = jsr["data"]["uri"])
                annot_resultset = json.loads(AStore.search_annotations(
                    uri = jsr["data"]["uri"],
                    title = ebookviewer.current_title,
                ))
                if annot_resultset["total"] > 0:
                    res = {"rows": []}
                    for row in annot_resultset["rows"]:
                        res["rows"].append(json.loads(AStore.read_annotation(str(row["id"]))))
                    res["total"] = len(res["rows"])
                    document.bridge_value = json.dumps(res)
                ## document.bridge_value = AStore.index()
            else:
                ## this is the vanilla action: get all
                document.bridge_value = AStore.index()
            should_update_documentview = True
            dlog(document.bridge_value)
        #create:  POST
        elif request_type == "POST":
            dlog("POST %s" % url)
            data = json.loads(jsr["data"])
            ## hack in the calibre viewer position
            bm = document.bookmark()
            bm['spine'] = ebookviewer.current_index
            data['calibre_bookmark'] = bm
            data['title'] = ebookviewer.current_title
            AStore.create_annotation(data)
            should_update_annotation_list = True
        #update:  PUT
        elif request_type == "PUT":
            dlog("PUT %s" % url)
            data = json.loads(jsr["data"])
            data['title'] = ebookviewer.current_title
            if "id" in data:
                AStore.update_annotation(data["id"], data)
        #destroy: DELETE
        elif request_type == "DELETE":
            dlog("DELETE %s" % url)
            data = json.loads(jsr["data"])
            if "id" in data:
                AStore.delete_annotation(data["id"])
            should_update_documentview = True
            should_update_annotation_list = True

        if should_update_documentview:
            document.mainFrame().evaluateJavaScript("if(window.evil_callback) {console.log('executing evil callback'); window.evil_callback(JSON.parse(py_bridge.value)); window.evil_callback = null; }")
        if should_update_annotation_list:
            ebookviewer.annotation_toc_model.update_current_annotation_list()

class AnnotationSearchBox(SearchBox2):
    '''
    the default SearchBox2.initialize requires an `opt_name` parameter,
    which is a required key, and must exist in the `config` ConfigProxy.

    we subclass it here mainly to bypass this requirement.
    '''

    INTERVAL = 500  #: Time to wait before emitting search signal

    # to use with store_in_history later?
    _my_search_history = []

    def _do_search(self, store_in_history=True, as_you_type=False):
        # generally C&P from search_box.py:SearchBox2._do_search,
        # except to bypass the config(ConfigProxy) interaction
        self.hide_completer_popup()
        text = unicode(self.currentText()).strip()
        if not text:
            return self.clear()
        print('searched for %s'%text)
        #if as_you_type:
        #    text = AsYouType(text)
        self.search.emit(text)

        if store_in_history:
            idx = self.findText(text, Qt.MatchFixedString|Qt.MatchCaseSensitive)
            self.block_signals(True)
            if idx < 0:
                self.insertItem(0, text)
            else:
                t = self.itemText(idx)
                self.removeItem(idx)
                self.insertItem(0, t)
            self.setCurrentIndex(0)
            self.block_signals(False)
            self._my_search_history = [unicode(self.itemText(i)) for i in
                    range(self.count())]

    # only difference with original is setting the interval
    def key_pressed(self, event):
        k = event.key()
        if k in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down,
                Qt.Key_Home, Qt.Key_End, Qt.Key_PageUp, Qt.Key_PageDown,
                Qt.Key_unknown):
            return
        self.normalize_state()
        if self._in_a_search:
            self.changed.emit()
            self._in_a_search = False
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.do_search()
            self.focus_to_library.emit()
        elif self.as_you_type and unicode(event.text()):
            self.timer.start(self.INTERVAL)

class ViewerAnnotationPlugin(ViewerPlugin):
    '''

    '''
    name                = 'Viewer Annotation Plugin'
    description         = 'adds annotation capability to ebook-viewer'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'whacked'
    version             = (0, 0, 1)
    minimum_calibre_version = (0, 7, 53)

    # def customize_context_menu(self, menu, event, hit_test_result):
    #     pass

    def customize_ui(self, ui):
        self._view = ui

        ui.tool_bar.addSeparator()

        # to be detected later for toc population
        ui.annotation_toc_model = None
        ui.annotation_toc = None
        
        # HACK?
        # append a callback to the javaScriptWindowObjectCleared
        # signal receiver. If you don't do this, the `py_annotator`
        # object will be empty (has no python functions callable)
        # from js
        ui.view.document.mainFrame().javaScriptWindowObjectCleared.connect(
                self.add_window_objects)

        ui.annotation_toc_dock = d = QDockWidget(_('Annotations'), ui)
        ui.annotation_toc_container = w = QWidget(ui)
        w.l = QVBoxLayout(w)
        d.setObjectName('annotation-toc-dock')
        d.setWidget(w)

        # d.close()  # start hidden? or leave default
        ui.addDockWidget(Qt.LeftDockWidgetArea, d)
        d.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        name = 'action_annotate'
        pixmap = QPixmap()
        pixmap.loadFromData(self.load_resources(['images/icon.png']).itervalues().next())
        icon = QIcon(pixmap)
        ac = ui.annotation_toc_dock.toggleViewAction()
        ac.setIcon(icon)

        setattr(ui.tool_bar, name, ac)
        ac.setObjectName(name)
        ui.tool_bar.addAction(ac)

    def add_window_objects(self):
        self._view.view.document.mainFrame().addToJavaScriptWindowObject('py_annotator', Responder(self._view.view.document))

    def set_annotation_toc_visible(self, yes):
        self.annotation_toc.setVisible(yes)

    def annotation_toc_clicked(self, index, force=False):
        from calibre.gui2 import error_dialog
        if force or QApplication.mouseButtons() & Qt.LeftButton:
            item = self._view.annotation_toc_model.itemFromIndex(index)
            if item.bookmark:
                self._view.goto_bookmark(item.bookmark)
            else:
                return error_dialog(None,
                                    _('No such location'),
                                    _('The location pointed to by this item'
                                      ' does not exist.'),
                                      det_msg=item.fragment or "no location saved",
                                      show=True)
        self._view.setFocus(Qt.OtherFocusReason)

    def run_javascript(self, evaljs):
        '''
        this gets called after load_javascript.

        we use it to initialize the annotator jquery plugin, as
        well as to inject the annotator css styling because there
        isn't currently a load_css() function available.
        '''
        # inject css
        dlog('injecting styling')
        # return
        for css_file in (
                'annotator-full.1.2.7/annotator.min.css',
                ):
            evaljs('''\
                $("#%(CSS_ID)s").remove();
                $("<style>", {id: "%(CSS_ID)s"}) \
                    .html("%(CSS_TEXT)s") \
                    .appendTo(document.head);
                ''' % dict(
                    CSS_ID = css_file.replace('/', ''),
                    CSS_TEXT = get_resources(css_file).replace('"', '\\"'),
                ))
        if self._view.iterator:
            current_spine = self._view.view.last_loaded_path
            base_path, href = os.path.split(current_spine)
            evaljs('''\
            $(document.body).annotator()
               .annotator('addPlugin', 'Store', {
                 // The endpoint of the store on your server.
                   prefix: 'http://localhost:5000/store'

                 // Attach the uri of the current page to all annotations to allow search.
                 , annotationData: {
                   'uri': '%(uri)s'
                 }
                 , loadFromSearch: {
                     'uri': '%(uri)s'
                 }
               });
            ''' % dict(uri = AModel.Annotation.make_uri(href)))

    def load_javascript(self, evaljs):
        '''
        from calibre docs:
        This method is called every time a new HTML document is
        loaded in the viewer. Use it to load javascript libraries
        into the viewer.
        '''

        dlog('loading javascript...')
        for js_file in (
                'annotator-full.1.2.7/annotator-full.min.js',
                'store.js',
                ):
            evaljs(get_resources(js_file))
        dlog('javascript ok')

        # NOTE: EbookViewer.iterator is None upon init.  it doesn't get reified
        # until the book is ready to render (or at least javascript is ready to
        # load). that's why the annotation toc is populated at this late stage.
        if self._view.annotation_toc_model is None and \
                self._view.iterator is not None:

            # QtWidgets.QWidget(self._view)
            ui = self._view

            # not sure if needed?
            splitter = QtWidgets.QSplitter(self._view)
            splitter.setOrientation(QtCore.Qt.Horizontal)
            splitter.setChildrenCollapsible(False)
            splitter.setObjectName('annotation_toc_splitter')
            # not sure if correct:
            # an_list = TOCView(splitter)

            w = ui.annotation_toc_container
            an_list = TOCView(w)
            an_list.setMinimumSize(QtCore.QSize(150, 0))
            an_list.setMinimumWidth(80)
            an_list.setObjectName('annotation_toc')
            an_list.setCursor(Qt.PointingHandCursor)

            self._view.annotation_toc_model = AnnotationTOC(ui.iterator.spine, self._view.current_title)
            an_list.setModel(self._view.annotation_toc_model)

            ui.annotation_toc = an_list

            an_list.pressed[QModelIndex].connect(self.annotation_toc_clicked)
            an_list.setCursor(Qt.PointingHandCursor)

            w.l.addWidget(ui.annotation_toc)

            # search box setup
            # ref calibre/gui2/viewer/toc.py
            ui.annotation_toc_search = AnnotationSearchBox(self._view)
            ui.annotation_toc_search.setMinimumContentsLength(15)
            ui.annotation_toc_search.line_edit.setPlaceholderText(_('Search Annotations'))
            ui.annotation_toc_search.setToolTip(_('Search for text in the Annotations'))
            ui.annotation_toc_search.search.connect(self.do_annotation_search)
            w.l.addWidget(ui.annotation_toc_search)

            w.l.setContentsMargins(0, 0, 0, 0)

    def do_annotation_search(self, text):
        annotation_toc = self._view.annotation_toc_model
        if not text or not text.strip():
            if annotation_toc._filter is None:
                # no change
                return
            self._view.annotation_toc_search.clear(emit_search=False)
            annotation_toc.clear_filter()
        else:
            annotation_toc.set_filter(text)
        annotation_toc.update_current_annotation_list()

    def is_customizable(self):
        '''
        This method must return True to enable customization via
        Preferences->Plugins
        '''
        return True

    def config_widget(self):
        '''
        Implement this method and :meth:`save_settings` in your plugin to
        use a custom configuration dialog.

        This method, if implemented, must return a QWidget. The widget can have
        an optional method validate() that takes no arguments and is called
        immediately after the user clicks OK. Changes are applied if and only
        if the method returns True.

        If for some reason you cannot perform the configuration at this time,
        return a tuple of two strings (message, details), these will be
        displayed as a warning dialog to the user and the process will be
        aborted.

        The base class implementation of this method raises NotImplementedError
        so by default no user configuration is possible.
        '''
        # It is important to put this import statement here rather than at the
        # top of the module as importing the config class will also cause the
        # GUI libraries to be loaded, which we do not want when using calibre
        # from the command line
        from calibre_plugins.viewer_annotation.config import ConfigWidget
        dlog('config config')
        return ConfigWidget()

    def save_settings(self, config_widget):
        '''
        Save the settings specified by the user with config_widget.

        :param config_widget: The widget returned by :meth:`config_widget`.
        '''
        config_widget.save_settings()

