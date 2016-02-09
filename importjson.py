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

DSN = 'sqlite:///%s' % os.path.expanduser('~/ebook-viewer-annotation.db')
AStore.setup_in_file(DSN)

input_data = json.loads(open(sys.argv[1]).read())
for i, entry in enumerate(input_data.values(), start=1):
    print('processing %s of %s' % (i, len(input_data)))
    d = entry.copy()
    d.update({
        'timestamp': datetime.datetime.fromtimestamp(entry['timestamp']/1000),
        'user': entry.get('user') or AStore.CURRENT_USER_ID,
    })
    a = AModel.Annotation()
    a.from_dict(d)

    AStore.session.add(a)
AStore.session.commit()

