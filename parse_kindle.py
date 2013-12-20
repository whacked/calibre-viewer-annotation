# -*- coding: utf-8 -*-
"""
work in progress.

The aim is to read some annotation files (here, Kindle output) and convert them
for consumption into the calibre annotation mechanism detailed in README.org
(sqlite backend).

Currently all this does is creates anchors. It does not derive the xpath from
the anchors (though I think we actually want a plugin for annotator that uses
the anchors, instead of using absolute positioning).

usage:

    python parse_kindle.py NOTE_FILE.txt BOOK_FILE.epub

    where NOTE_FILE is a plain text file containing annotations copy/pasted from the kindle site.
    if you really do a copy/paste from your browser, it will be a series of excerpts like this:
'''
This is a bit of text taken from your book. Blah blah blah
Add a note
'''
    based on a copy/paste on Thu Dec 19 20:42:52 EST 2013
    the 'Add a note' is thus a link in your browser.

    the BOOK_FILE is an epub. Currently I am testing with an epub converted using calibre.

"""

import sys
import epub
from collections import namedtuple
from anchortext import *
import lxml.html

class KindleNote:
    """convenience class, will probably scrap later"""
    NOTE = 'note'

    def __init__(self, annot_type, annot_content):
        self.type = annot_type
        self.content = annot_content

    def __repr__(self):
        spl = self.content.split()[:10]
        if len(self.content) > 200:
            return ' '.join(spl[:20]) + '...'
        else:
            return ' '.join(spl[:20])

IndexRange = namedtuple('IndexRange', ['len', 'beg', 'end'])

if __name__ == '__main__':


    filepath = sys.argv[-2]
    bookpath = sys.argv[-1]

    book = epub.open_epub(bookpath)
    mydc = dict((key, book.read_item(item)) for key, item in book.opf.manifest.items())

    # compile the list of notes
    note_list = []
    for line_orig in open(filepath).readlines():
        if line_orig.lstrip().startswith('Add a note'):
            continue
        line_type = None

        # preprocessing
        line = line_orig.replace('• Delete this highlight', '').strip()
        if not line:
            continue
        if line.startswith('Note: ') and line.endswith('Edit'):
            line_type = KindleNote.NOTE
            line = line[:-4].strip()
        note_list.append(KindleNote(line_type, line))

    def forceint(s):
        stripped = ''.join([ch for ch in s if ch.isdigit()])
        return stripped and int(stripped) or -1
    def make_lossy(xml_string):
        s = lxml.html.fromstring(xml_string).text_content().replace('\n', ' ').replace('  ', ' ')
        return s.lower()
    def find_lossy_needle_in_xmlhaystack(needle, haystack):
        """
        probabilistically determine if `needle` is in `haystack` after
        stripping out all special characters and other special punctuation, and
        measuring some inexact criteria.

        currently it is dumb, and works this way:
        1. from the needle, we look token by token into the haystack
           for whether the needle exists at all.
        2. if it does, record the index
        3. if most of the needle tokens exist, within some proximity of each other
           return True, else False
        """
        mynd = make_lossy(needle)
        myhs = make_lossy(haystack)
        # first tokenize
        # note if this is like Chinese or something
        # we will end up with a ch by ch search, which
        # might just work out of the box.
        # also dtoken_score is stupid
        # in that repeats are just 
        hs_token_list = mynd.split()
        if len(hs_token_list) > 1:
            hs_bigram_list = map(lambda (a, b): a+' '+b, zip(hs_token_list[:-1], hs_token_list[1:]))
        else:
            hs_bigram_list = hs_token_list
        dtoken_score = {}
        bonus = 0.0 # number of tokens that match
        # penalty_list: in exact string match, is zero, else larger
        # using a list, because if we match for e.g. 'the' on first
        # try, we will anchor very quickly, causing later indexes
        # to accrue a high penalty. if `needle` is large, then
        # in a document with the target, we will quickly converge
        # onto the correct index. so penalty should exclude the worst
        # indexes if they are bunched towards the beginning.
        # we seed penalty_list with the length of the needle
        # so if needle is not found (and penalty list is empty)
        # the penalty = 1.0.
        # on successive finds (given exclusion of the N worst occurs,
        # which is set to PENALTY_EXCLUDE), we will decrease the penalty
        # mean towards 0.0
        penalty_list = [len(mynd)]
        PENALTY_EXCLUDE = 3
        lastindex = 0
        for token in hs_bigram_list:
            if token in myhs[lastindex:]:
                bonus += 1
                index_occur = myhs[lastindex:].index(token)
                penalty_list.append(index_occur)
                lastindex += index_occur
        penalty_list.sort()
        penalty = sum(penalty_list[:-PENALTY_EXCLUDE])*1.0 / len(penalty_list) / len(mynd)
        found_ratio = bonus/len(hs_bigram_list)
        if found_ratio > 0.9 or \
                found_ratio > 0.5 and penalty < 0.3:
            return max(0, lastindex - len(mynd) * 2)
        elif found_ratio > 0.5:
            print found_ratio, penalty
            print '>>> SEARCH <<<'
            print mynd
            print '>>>   IN   <<<'
            print myhs[lastindex-2*len(mynd):lastindex+len(mynd)]
            print penalty_list
        return -1


    found_list = []

    doc_key_list = sorted(mydc.keys(), lambda a, b: forceint(a) > forceint(b) and 1 or -1)
    doc_txt_list = [mydc[k] for k in doc_key_list]
    for doc_idx, doc_key in enumerate(doc_key_list):

        xml = mydc[doc_key]
        # skip xml without a html tree
        if '</html>' not in xml:
            # print doc_key, 'has no html tree'
            continue
        nidx = 0
        while nidx < len(note_list):
            note = note_list[nidx]
            lossy_idx = find_lossy_needle_in_xmlhaystack(note.content, xml)
            if lossy_idx >= 0:
                print "FOUND in doc", doc_idx, ":", note
                del note_list[nidx]
                spl = note.content.split()

                ## TODO
                # apply bigram check. we're failing on 'Does' as check_first
                # and 'him' as check_last.  that's obviously too easy
                check_first, check_last = spl[0], spl[-1]

                # lossy_idx is a bit too lossy: since it strips out xml it is
                # expected to be less than the actual index.  but even using
                # approximate indexes, it turns out there are often matching
                # tokens between lossy_idx and the real index (even bigrams,
                # like 'He wondered...' that occured in 2 consecutive
                # paragraphs). So we will use lossy_idx to re-center within
                # the xml before deriving the anchors.
                doc_txt = doc_txt_list[doc_idx]
                beg_idx = lossy_idx

                # process check_first index
                beg_idx_list = []
                while True:
                    idx = doc_txt[beg_idx:].find(check_first)
                    if idx == -1:
                        break
                    beg_idx_list.append(beg_idx+idx)
                    beg_idx += idx+len(check_first)

                candidate_list = []
                # process check_last index
                for beg_idx in beg_idx_list:
                    end_idx = beg_idx
                    while True:
                        idx = doc_txt[end_idx:].find(check_last)
                        if idx == -1:
                            break
                        end_idx += idx+len(check_last)
                        candidate_list.append(IndexRange( abs(end_idx+len(check_last)-beg_idx - len(note.content)), beg_idx, end_idx ))

                # so we will select the candidate index range that results in
                # the smallest difference in length vs. the actual desired
                # note.content
                candidate_list.sort()
                best_range = candidate_list[0]

                ra0, ra1 = make_anchor_range(note.content, best_range.beg, doc_idx, doc_txt_list)
                found_list.append((note, ra0, ra1, doc_idx))
            else:
                nidx += 1

    for note, anc0, anc1, doc_idx in found_list:
        print "-"*40
        print "EXPECTED:", note.content
        try:
            idx0, idx1 = apply_anchor_range(anc0, anc1, doc_txt_list[doc_idx])
            print " DERIVED:", doc_txt_list[doc_idx][idx0:idx1]
        except Exception, e:
            print "BAD", e
            print anc0
            print anc1
        print "."*40, idx0, idx1

