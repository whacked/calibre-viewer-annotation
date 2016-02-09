'''
convenience functions for dealing with book (now epub) files
'''

import re
import textwrap
from collections import Counter
import epub
from lxml import etree


def epub_to_corpus(mixed, as_dict=False):
    '''
    mixed: a filepath or an epub object
    '''
    if   isinstance(mixed, epub.EpubFile):
        book = mixed
    elif isinstance(mixed, basestring):
        book = epub.open_epub(mixed)
    else:
        raise TypeError("don't know how to handle %s of type %s" % (mixed, type(mixed)))

    # RETURNS:
    corpus = []
    valid_klist = []

    # we only want page/document content
    p_page = re.compile(r'(.*?)\.(html?)$')
    # to separate the key from its numbering
    p_key = re.compile(r'^(\D+)(\d+)$')

    #page_prefix = sorted(prefix_counter, key=prefix_counter.get, reverse=True)[0]
    prefix_counter = Counter()

    bookdata = {}
    for key in book.opf.manifest.keys():
        manifest_item = book.opf.manifest[key]
        match = p_page.match(manifest_item.href)
        if match:
            prefix = p_key.match(key).group(1)
            prefix_counter[prefix] += 1
            bookdata[key] = book.read_item(manifest_item)

    page_prefix = sorted(prefix_counter, key=prefix_counter.get, reverse=True)[0]

    # strips out the leading 'html' for numbering
    keyfunc = lambda k: int(k[len(page_prefix):])
    for key in sorted(bookdata.keys(), key=keyfunc):
        xml = bookdata[key]

        # it turns out the book data may be binary data, e.g. JPEG
        tree = etree.fromstring(xml)

        ## simple xpath won't work due to namespace prefixing
        ## either use this notation
        ## tree.xpath("//xhtml:style", namespaces={'xhtml': tree.nsmap[None]})
        ## here, the None ns is actually the 'xhtml' ns
        ## though i think you can redefine it to whatever you want
        ## as opposed to 'xhtml' in the query
        ## or this
        for node in tree.xpath('''//*[local-name() = "style"]'''):
            node.getparent().remove(node)
        text = etree.tostring(tree, encoding = 'utf8', method = 'text')

        valid_klist.append(key)
        corpus.append(text)

    if as_dict:
        return dict(zip(valid_klist, corpus))
    return corpus


if __name__ == '__main__':

    import sys
    book_filepath = len(sys.argv)>1 and sys.argv[-1] or 'test.epub'
    print('loading: %s' % book_filepath)

    corpus = epub_to_corpus(book_filepath)
    print(len(corpus))
    print(len(corpus[0]))
    print(corpus[-1][:100])


