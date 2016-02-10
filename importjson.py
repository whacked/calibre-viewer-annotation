'''
import a json generated from nw-extractor


usage:
    python importjson.py $JSONFILE

    or

    python importjson.py $JSONFILE $EPUBFILE

if $EPUBFILE is specified and exists, this will attempt to
derive (Anchor) values as well, and save them inside the
`extras` field in the (Annotator) object.
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
import bookreader as bkr
import anchortext as at

json_filepath = sys.argv[1].strip()


book = None
corpus = None
uri2key = {}
# check if should load the corpus
if len(sys.argv) == 3:
    ebook_filepath = sys.argv[2].strip()
    if os.path.exists(ebook_filepath):
        book = bkr.epub.open_epub(ebook_filepath)
        print('reading book: %s' % ebook_filepath)
        corpus = bkr.epub_to_corpus(book, as_dict=True)

        # build uri2key
        for key in book.opf.manifest.keys():
            if key not in corpus: continue
            item = book.get_item(key)
            epub_uri = 'epub://%s' % item.href.split('/')[-1]
            uri2key[epub_uri] = key

DSN = 'sqlite:///%s' % os.path.expanduser('~/ebook-viewer-annotation.db')
AStore.setup_database(DSN)

# TODO: move into Annotation model
def add_extra(self, dc):
    '''
    since `extra` is currently a json-serialized string,
    this convenience fn reads a (dict)dc and adds it to
    the serialization
    '''
    extra = json.loads(self.extras)
    extra.update(dc)
    self.extras = json.dumps(extra)
    return self.extras

input_data = json.loads(open(sys.argv[1]).read())
for i, entry in enumerate(input_data.values(), start=1):
    print('processing %s of %s' % (i, len(input_data)))
    d = entry.copy()
    d.update({
        'created': datetime.datetime.fromtimestamp(entry['created']/1000),
        'user': entry.get('user') or AStore.CURRENT_USER_ID,
    })
    ann = AModel.Annotation()
    ann.from_dict(d)

    corpus_key = uri2key.get(ann.uri)
    if corpus_key:
        anc = at.make_anchor(
                # TODO should be quote
                ann.text,

                ann.ranges[0].startOffset,
                corpus_key,
                corpus,
                )
        add_extra(ann, dict(anchor = anc.to_dict()))

    AStore.session.add(ann)
AStore.session.commit()

