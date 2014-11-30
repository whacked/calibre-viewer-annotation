'''
import a json generated from nw-extractor


usage:
    python importjson.py $JSONFILE
'''
import sys

if len(sys.argv) < 2:
    print __doc__
    sys.exit()

import json
# path hack... to bypass calibre import needed in the plugin
sys.path.append('ViewerAnnotationPlugin')
import annotator_model as AModel
import annotator_store as AStore
import os

AModel.metadata.bind = 'sqlite:///%s' % os.path.expanduser('~/ebook-viewer-annotation.db')
AModel.setup_all(True)

input_data = json.loads(open(sys.argv[1]).read())
for i, entry in enumerate(input_data.values(), start=1):
    print('processing %s of %s' % (i, len(input_data)))
    uri = entry.pop('uri')
    title = entry.pop('title')
    text = entry.pop('text')
    a = AModel.Annotation()
    a.from_dict(entry)
    a.text = text
    a.uri = uri
    a.title = title
    AModel.session.add(a)
AModel.session.commit()

