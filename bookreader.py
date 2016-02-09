'''
convenience functions for dealing with book (now epub) files
'''

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

    bookdata = {}
    for key, manifest_item in book.opf.manifest.iteritems():
        ## WARNING NOTE
        ## not clear where this heuristic is from, may not be general
        if not key.startswith('html'):
            continue
        bookdata[key] = book.read_item(manifest_item)

    # strips out the leading 'html' for numbering
    keyfunc = lambda k: int(k[4:])
    sorted_klist = list(sorted(bookdata.keys(), key=keyfunc))
    for key in sorted_klist:
        xml = bookdata[key]
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
        corpus.append(text)

    if as_dict:
        return dict(zip(sorted_klist, corpus))
    return corpus


if __name__ == '__main__':

    corpus = epub_to_corpus('test.epub')
    print(len(corpus))
    print(len(corpus[0]))
    print(corpus[-1][:100])
