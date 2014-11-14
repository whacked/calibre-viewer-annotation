#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__   = 'GPL v3'
__copyright__ = '2014, github.com/whacked'
__docformat__ = 'restructuredtext en'

from PyQt5.Qt import QWidget, QVBoxLayout, QLabel, QLineEdit

from calibre.utils.config import JSONConfig

# This is where all preferences for this plugin will be stored
# Remember that this name (i.e. plugins/viewer_annotation) is also
# in a global namespace, so make it as unique as possible.
# You should always prefix your config file name with plugins/,
# so as to ensure you dont accidentally clobber a calibre config file
prefs = JSONConfig('plugins/viewer_annotation')

# Set defaults
import os
prefs.defaults['annotator_db_path'] = os.path.join(os.path.expanduser('~'),
        'ebook-viewer-annotation.db')

class ConfigWidget(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('''\
Specify path for annotation database. If left blank, defaults to
%s
''' %prefs.defaults['annotator_db_path'])
        self.l.addWidget(self.label)

        self.annotator_db_path = QLineEdit(self)
        self.annotator_db_path.setText(prefs['annotator_db_path'])
        self.l.addWidget(self.annotator_db_path)
        self.label.setBuddy(self.annotator_db_path)

    def save_settings(self):
        # TODO add more intelligence here
        given_path = unicode(self.annotator_db_path.text()).strip()
        if os.path.exists(given_path):
            prefs['annotator_db_path'] = given_path
        else:
            prefs['annotator_db_path'] = prefs.defaults['annotator_db_path']

