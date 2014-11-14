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
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.Qt import (
        QApplication, QWidget, QModelIndex,
        QDockWidget, QVBoxLayout, pyqtSlot,
        )

from calibre_plugins.viewer_annotation import annotator_model as AModel
from calibre_plugins.viewer_annotation import annotator_store as AStore
from calibre_plugins.viewer_annotation.config import prefs

AModel.metadata.bind = 'sqlite:///%s' % prefs['annotator_db_path']
# Create tables
# NOTE: this is needed to trigger elixir's binding of `query` to model objects
AModel.setup_all(True)

DEBUG_LEVEL = 10
def dlog(*s):
    if DEBUG_LEVEL == 0:
        return
    for ss in s:
        print('[DLOG] ---> %s' % ss)

class AnnotationTOC(TOC):

    def update_current_annotation_list(self):
        self.clear()
        res = []
        toc = []
        for spine in self._spine_list:
            base_path, href = os.path.split(spine)
            annot_resultset = json.loads(AStore.search_annotations(uri = "epub://" + href))
            # dlog('searching for: %s/%s' % (base_path, href))
            if annot_resultset["total"] > 0:
                for row in annot_resultset["rows"]:
                    annot = json.loads(AStore.read_annotation(str(row["id"])))
                    frag = (annot["uri"] + "#").split("#")[1]
                    text = annot.get("text") or "(highlight)"
                
                    toc.append(MetaTOC(
                        href = href,
                        fragment = frag,
                        text = text,
                        base_path = base_path,
                        ))
                    ## HACK: store bookmark pos in the frag
                    toc[-1].bookmark = annot.get("calibre_bookmark", {})
        self.all_items = depth_first = []
        for t in toc:
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
        for i in range(10):
            toc.append(MetaTOC(
                href = 'foo',
                fragment = 'bar',
                text = 'baz',
                base_path = str(i),
                ))


    def __init__(self, spine):
        QStandardItemModel.__init__(self)
        toc = []

        self.base_path = os.path.split(spine[0])[0]
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
                annot_resultset = json.loads(AStore.search_annotations(uri = jsr["data"]["uri"]))
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
            bm = self.parent().bookmark()
            bm['spine'] = ebookviewer.current_index
            data["calibre_bookmark"] = bm
            AStore.create_annotation(data)
            should_update_annotation_list = True
        #update:  PUT
        elif request_type == "PUT":
            dlog("PUT %s" % url)
            data = json.loads(jsr["data"])
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


class ViewerAnnotationPlugin(ViewerPlugin):
    '''

    '''
    name                = 'Viewer Annotation Plugin'
    description         = 'adds annotation capability to ebook-viewer'
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'whacked'
    version             = (0, 0, 1)
    minimum_calibre_version = (0, 7, 53)

    def customize_context_menu(self, menu, event, hit_test_result):
        dlog('hello context menu')

    def customize_ui(self, ui):
        from PyQt5.Qt import (
            QPixmap,
            QIcon, QAction, QDockWidget,
        )
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
        if force or QApplication.mouseButtons() & Qt.LeftButton:
            item = self._view.annotation_toc_model.itemFromIndex(index)
            if item.bookmark:
                self._view.goto_bookmark(item.bookmark)
            else:
                return error_dialog(self, _('No such location'),
                        _('The location pointed to by this item'
                            ' does not exist.'), det_msg=item.fragment or "no location saved", show=True)
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
                   'uri': 'epub://%(href)s'
                 }
                 , loadFromSearch: {
                     'uri': 'epub://%(href)s'
                 }
               });
            ''' % dict(href = href))

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

            self._view.annotation_toc_model = AnnotationTOC(ui.iterator.spine)
            an_list.setModel(self._view.annotation_toc_model)

            ui.annotation_toc = an_list

            an_list.pressed[QModelIndex].connect(self.annotation_toc_clicked)
            an_list.setCursor(Qt.PointingHandCursor)

            w.l.addWidget(ui.annotation_toc)

            # no, this does not work without extra code!
            # ui.annotation_toc_search = TOCSearch(ui.annotation_toc, parent=w)
            # w.l.addWidget(ui.annotation_toc_search)
            w.l.setContentsMargins(0, 0, 0, 0)

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

