# -*- coding: utf-8 -*-


import json
from tfidf import *

# FIXME
# these are multiplied with the target token's length.  right now i don't see
# why that is a good idea. not that it makes very much of a difference between
# having a hard-coded look-before and look-ahead value.  the immediate impact
# is that short tokens are more restricted than long tokens.
PRE_MULTIPLIER = 10
POST_MULTIPLIER = 10

class Anchor:

    def __init__(self):
        self.token = None
        self.approximate_offset = None
        self.relative_offset = None
        self.support_anchor_list = []

    def __repr__(self):
        rtn = "[%s]\t~\t%s (%s)" % (self.token, self.approximate_offset, self.relative_offset)
        if self.support_anchor_list:
            rtn += "\n    supported by:\n        " + "\n        ".join(map(str, self.support_anchor_list))
        return rtn

    def to_dict(self):
        return dict(
            token = self.token,
            aoffset = self.approximate_offset,
            roffset = self.relative_offset,
            support = [anc.to_dict() for anc in self.support_anchor_list],
            )

    def to_json(self):
        return json.dumps(self.to_dict())

class AnchorDoesNotExistException(Exception):
    pass


def apply_insertion(base_text, insertion_list):
    """
    `insertion_list`: [(index:int, text:string)]: inserts text at index
    """
    insertion_list.sort()
    for index, text in sorted(insertion_list, reverse = True):
        base_text = base_text[:index] + text + base_text[index:]
    return base_text

def apply_highlight(base_text, insertion_list):
    insertion_list.sort()
    rtn = []
    last_index = 0
    for index, text in sorted(insertion_list):
        rtn.append(base_text[last_index:index] + colored(base_text[index:index+len(text)], "yellow", attrs=["bold"]))
        last_index = index+len(text)
    rtn.append(base_text[index+len(text):])
    return "".join(rtn)

def apply_anchor_range(anchor0, anchor1, base_text):
    idx0 = apply_anchor(anchor0, base_text)
    # later anchor must be after early anchor
    idx1 = apply_anchor(anchor1, base_text, idx0) +len(anchor1.token)
    return idx0, idx1

def apply_anchor(anc, base_text, force_start_index = 0):
    """
    returns exact begin and end offset
    based on `anchor`
    """
    idx_start = max(force_start_index, anc.approximate_offset - len(anc.token) * PRE_MULTIPLIER)
    idx_end   = min(len(base_text),    max(idx_start, anc.approximate_offset) + len(anc.token) * POST_MULTIPLIER)

    match_list = []
    idx_current = idx_start
    while idx_current < idx_end:
        idx_match = base_text[idx_current:].find(anc.token)
        if idx_match == -1:
            break
        match_list.append(idx_current+idx_match)
        idx_current = idx_current + idx_match + len(anc.token)

    if len(match_list) is 1:
        return match_list[0]
    elif len(match_list) is 0:
        raise AnchorDoesNotExistException("inexistent")
    else:

        if anc.support_anchor_list:

            danchormap = {}
            for sanc in anc.support_anchor_list:
                # i.e. (absolute, relative)
                try:
                    danchormap[sanc.token] = (apply_anchor(sanc, base_text), sanc.relative_offset)
                    ## print "        [%s]\t~      %s (%s)" % tuple([sanc.token] + list(danchormap[sanc.token]))
                except AnchorDoesNotExistException, e:
                    ## hopefully the text isn't so decayed so all our cues are gone
                    pass

            rank_list = []
            for idx in match_list:
                sumdiff = 0
                for sanc_token, (sanc_abs_offset, sanc_rel_offset) in danchormap.iteritems():
                    actual_rel_offset = idx - sanc_abs_offset
                    sumdiff += abs(actual_rel_offset - sanc_rel_offset)
                rank_list.append((sumdiff, idx))

        else:
            ## quick and dirty method

            # find the closest to approximate_offset and return that
            rank_list = [(abs(idx - anc.approximate_offset), idx) for idx in match_list]

        rank_list.sort()
        return rank_list[0][1]

def make_anchor(desired_token, approximate_offset, current_document_index, base_document_list):

    idx_start = approximate_offset - len(desired_token) * PRE_MULTIPLIER
    idx_end   = approximate_offset + len(desired_token) * (POST_MULTIPLIER+1)

    anc = Anchor()
    anc.token = desired_token
    anc.approximate_offset = approximate_offset

    tfidfer = TFIDF(base_document_list)

    ## TODO
    ## consider implementing weighting by distance, closer is better
    ## though, as currently by tfidf, our support anchors should be
    ## within the same "page" at least
    for score, firstidx, token in tfidfer.bestn(current_document_index, N = 20):
        if len(anc.support_anchor_list) > 5: break
        if token == desired_token: continue
        ## this is going to store a DELTA offset
        support_anchor = Anchor()
        support_anchor.token = token
        support_anchor.approximate_offset = firstidx
        support_anchor.relative_offset = anc.approximate_offset - firstidx
        anc.support_anchor_list.append(support_anchor)

    return anc

def make_anchor_range(desired_text, approximate_offset, current_document_index, base_document_list):
    spl = filter(lambda (offset, token): len(token) > 0, tokenize(desired_text))
    token0 = spl[0][1]
    token1 = spl[-1][1]
    offset0 = approximate_offset
    offset1 = approximate_offset + len(desired_text) - len(token1)

    anchor0 = make_anchor(token0, offset0, current_document_index, base_document_list)
    anchor1 = make_anchor(token1, offset1, current_document_index, base_document_list)

    return anchor0, anchor1


if __name__ == "__main__":


    try:
        from termcolor import colored
        def run_apply_demo(anchor, text):
            idx = apply_anchor(anchor, text)
            print text[:idx] + colored(text[idx:idx+len(anchor.token)], "yellow", attrs=["bold"]) + text[idx+len(anchor.token):]
    except Exception, e:
        def run_apply_demo(anchor, text):
            idx = apply_anchor(anchor, text)
            print apply_insertion(text, [(idx, "***"), (idx+len(anchor.token), "***")])

    document_text_list = [
            """
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam. Sed nisi. Nulla quis sem at nibh elementum imperdiet. Duis sagittis ipsum. Praesent mauris. Fusce nec tellus sed augue semper porta. Mauris massa. Vestibulum lacinia arcu eget nulla. 
            """,
            """
Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur sodales ligula in libero. Sed dignissim lacinia nunc. Curabitur tortor. Pellentesque nibh. Aenean quam. In scelerisque sem at dolor. Maecenas mattis. Sed convallis tristique sem. Proin ut ligula vel nunc egestas porttitor. Morbi lectus risus, iaculis vel, suscipit quis, luctus non, massa. 
            """,
            """
Fusce ac turpis quis ligula lacinia aliquet. Mauris ipsum. Nulla metus metus, ullamcorper vel, tincidunt sed, euismod in, nibh. Quisque volutpat condimentum velit. this particular one is not the target is this the real no it is not but this target no also a fake this is the is it real not really no so actually this is the real target text 2 but there is other text the rest is just there to confuse you but this is also real is this real the target is real this is but is that real this real there Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam nec ante. Sed lacinia, urna non tincidunt mattis, tortor neque adipiscing diam, a cursus ipsum ante quis turpis. Nulla facilisi. Ut fringilla. Suspendisse potenti. Nunc feugiat mi this is the real target text 3 a tellus consequat imperdiet. 

            """,
            """
Vestibulum sapien. Proin quam. Etiam ultrices. Suspendisse in justo eu magna luctus suscipit. Sed lectus. Integer euismod lacus luctus magna. Quisque cursus, metus vitae pharetra auctor, sem massa mattis sem, at interdum magna augue eget diam. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Morbi lacinia molestie dui. Praesent blandit dolor. Sed non quam. In vel mi sit amet augue congue elementum. Morbi in ipsum sit amet pede facilisis laoreet. 
            """,
            """
Donec lacus nunc, viverra nec, blandit vel, egestas et, augue. Vestibulum tincidunt malesuada tellus. Ut ultrices ultrices enim. Curabitur sit amet mauris. Morbi in dui quis est pulvinar ullamcorper. Nulla facilisi. Integer lacinia sollicitudin massa. Cras metus. Sed aliquet risus a tortor. Integer id quam. Morbi mi. 
            """,
            ]
    document_text_list = map(str.strip, document_text_list)
    highlighted_text = "this is the real target text" # we want 2

    if True:
        import random

        offset_begin = 310
        testtxt = document_text_list[2]
        ra0, ra1 = make_anchor_range(highlighted_text, offset_begin, 2, document_text_list)

        anc = make_anchor(highlighted_text, offset_begin, 2, document_text_list)
        print anc
        anc.support_anchor_list = []
        ## screw up the offset; this should break the quick and dirty version
        run_apply_demo(anc, ("blah " * 40) + "bleh bleh bleh this is the real target text 1 " + testtxt)

        print
        print "=== === ==="
        print

        testtxt = testtxt.replace(random.choice(ra0.support_anchor_list).token, '')
        idx0, idx1 = apply_anchor_range(ra0, ra1, testtxt)
        print testtxt[:idx0] + colored(testtxt[idx0:idx1], "yellow", attrs=["bold"]) + testtxt[idx1:]

        realtarget = highlighted_text + " 2"
        good0 = testtxt.index(realtarget)
        good1 = testtxt.index(realtarget) + len(realtarget)

    if False:
        testtxt = """
        we are the best the best, the the the best!
        """.strip()
        anc = Anchor()
        anc.token = "the"
        anc.approximate_offset = 18
        idx = apply_anchor(anc, testtxt)

        run_apply_demo(anc, testtxt)

    ## test word scoring method
    if False:
        for word in """
        test
        easy
        think
        quartz
        abc123fourvi
        queen
        zenith
        the
        """.strip().split():
            print word, get_word_score(word)
