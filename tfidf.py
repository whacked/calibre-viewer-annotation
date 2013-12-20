import os, sys
import yaml
import epub
import re
from lxml import etree
import math
import random
import operator

from collections import Counter


# TODO
# if document_list is small should use some heuristic to measure word
# complexity, and prefer to anchor on rare words

## here's the simple rare word scoring heuristic
## this chart from http://www.math.cornell.edu/~mec/2003-2004/cryptography/subs/frequencies.html
## retrieved on Thu Nov  7 17:30:49 EST 2013
dletterscore = dict([(ch, 14-float(score)) for ch, score in map(str.split, """
E   12.02
T   9.10
A   8.12
O   7.68
I   7.31
N   6.95
S   6.28
R   6.02
H   5.92
D   4.32
L   3.98
U   2.88
C   2.71
M   2.61
F   2.30
Y   2.11
W   2.09
G   2.03
P   1.82
B   1.49
V   1.11
K   0.69
X   0.17
Q   0.11
J   0.10
Z   0.07
""".strip().split("\n"))])
def get_word_score(word):
    modword = re.sub(r'[^a-zA-Z]', '', word)
    return sum(map(dletterscore.get, modword.upper())) / len(modword) * math.log(len(word))


def tokenize(s):
    """
    returns: [(token:str, offset:int)]
    entities will get split too!
    """
    lastidx = 0
    rtn = []
    for match in re.finditer(r"[\W\s]", s):
        beg, end = match.start(), match.end()
        if lastidx is 0 and beg == lastidx:
            pass
        else:
            rtn.append((lastidx, s[lastidx:beg]))
        lastidx = end
    if lastidx < len(s):
        rtn.append((lastidx, s[lastidx:]))
    return rtn

def map_get_second(ls):
    return map(operator.itemgetter(1), ls)

def tf(term, document):
    """term frequency

    - `term`: the search token
    - `document`: a string that is just a bunch of text that should contain some number of instances of `term`
    """
    return map_get_second(tokenize(document.lower())).count(term.lower())

def idf(term, document_list):
    """inverse document frequency
    
    - `document_list`: list of string
    """
    n_doc_total = float(len(document_list))
    n_doc_wterm = len(filter(lambda doc: 1 if tf(term, doc) > 0 else 0, document_list))
    return math.log(n_doc_total / n_doc_wterm)

def tfidf(term, idx_document, document_list):
    return tf(term, document_list[idx_document]) * idf(term, document_list)

class TFIDF:

    dstopword = set("""
    I a about an are as at be by com for from how in is it of on or that the this to was what when where who will with the
    """.strip().split())

    _dmemo = {}
    def __init__(self, document_list):
        self.document_list = document_list
        self.ndoc = len(document_list)
        for i, document in enumerate(document_list):
            self._dmemo[i] = Counter(map_get_second(tokenize(document.lower())))

    def tfidf(self, term, idx_document):
        term = term.lower()
        n_doc_wterm = len(filter(lambda doc_id: self._dmemo[doc_id].get(term) or 0, range(self.ndoc)))
        return self._dmemo[idx_document][term] * math.log(float(self.ndoc) / n_doc_wterm)

    def bestn(self, docidx, N = 6):
        """

        returns: a tuple of (tfidf score, index of *first* occurence, token in question)
        
        """
        dcount = {}
        # save index of occurence, we want to give precedence to earlier
        # indexes (for human readability if one somehow wants to scan through
        # the text for the matching anchor keyword), so save the first matching
        # token's index
        for idx, token in tokenize(self.document_list[docidx]):
            if token not in dcount:
                dcount[token] = []
            dcount[token].append(idx)

        used = set()
        res = []
        for token, idxlist in dcount.iteritems():
            if token in self.dstopword: continue
            ltoken = token.lower()
            if ltoken in used: continue
            used.add(ltoken)
            res.append((self.tfidf(token, docidx), idxlist[0], token))
        res.sort()
        return res[-N:]

if __name__ == "__main__":

    book = epub.open_epub("test.epub")

    mydc = dict((key, book.read_item(item)) for key, item in filter(lambda (k, i): k.startswith("html"), book.opf.manifest.items()))

    ls_text = []
    for key in sorted(mydc.keys(), lambda a, b: int(a[4:]) > int(b[4:]) and 1 or -1):
        xml = mydc[key]
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
        text = etree.tostring(tree, encoding = "utf8", method = "text")
        ls_text.append(text)

    tfidfer = TFIDF(ls_text)
    
    docnum = random.randint(1, len(ls_text))
    docnum = 22
    docidx = docnum - 1
    if False:
        res = []
        alltoken = set(map_get_second(tokenize(" ".join(ls_text[docidx:docidx+1]))))
        print "DOCNUM: ", docnum
        for i, token in enumerate(alltoken):
            sys.stdout.write("%04d / %04d\r" % (i, len(alltoken)))
            sys.stdout.flush()
            res.append((tfidfer.tfidf(token, docidx), token))
        print
        res.sort()
    else:

        res = tfidfer.bestn(docidx)

    mytext = ls_text[docidx]
    for score, firstidx, token in res:
        print token, "\t", score, firstidx, mytext[firstidx:firstidx+len(token)]


