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

    # first pass: discover what the page prefix is
    p_page = re.compile(r'^(\D+)(\d+)$')
    manifest_klist = book.opf.manifest.keys()

    prefix_counter = Counter()
    for key in manifest_klist:
        match = p_page.match(key)
        if not match:
            continue
        prefix, idstr = match.groups()
        prefix_counter[prefix] += 1

    if not prefix_counter:
        raise Exception(textwrap.dedent('''
            no page candidate found.

            here are the keys in the manifest:
            %s
        ''' % (', '.join(sorted(manifest_klist)))))

    page_prefix = sorted(prefix_counter, key=prefix_counter.get, reverse=True)[0]

    # second pass: build bookdata
    bookdata = {}
    for key in manifest_klist:
        if not key.startswith(page_prefix):
            continue
        manifest_item = book.opf.manifest[key]
        bookdata[key] = book.read_item(manifest_item)

    # strips out the leading 'html' for numbering
    keyfunc = lambda k: int(k[len(page_prefix):])

    for key in sorted(bookdata.keys(), key=keyfunc):
        xml = bookdata[key]

        # it turns out the book data may be binary data, e.g. JPEG
        try:
            tree = etree.fromstring(xml)
        except etree.XMLSyntaxError:
            continue

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


