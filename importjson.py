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
import datetime

AModel.metadata.bind = 'sqlite:///%s' % os.path.expanduser('~/ebook-viewer-annotation.db')
AModel.setup_all(True)

input_data = json.loads(open(sys.argv[1]).read())
for i, entry in enumerate(input_data.values(), start=1):
    print('processing %s of %s' % (i, len(input_data)))
    d = {
        'timestamp': datetime.datetime.fromtimestamp(entry.pop('timestamp')/1000),
    }
    for k in 'uri title text'.split():
        d[k] = entry.pop(k)
    a = AModel.Annotation()
    a.from_dict(entry)
    for k in d:
        setattr(a, k, d[k])
    AModel.session.add(a)
AModel.session.commit()

