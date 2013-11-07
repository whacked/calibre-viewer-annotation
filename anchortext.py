# -*- coding: utf-8 -*-


import json
from tfidf import *


PRE_MULTIPLIER = 10
POST_MULTIPLIER = 10

class Anchor:

    def __init__(self):
        self.token = None
        self.approximate_offset = None
        self.support_anchor_list = []

    def __repr__(self):
        rtn = "[%s] ~ %s" % (self.token, self.approximate_offset)
        if self.support_anchor_list:
            rtn += "\n    supported by:\n        " + "\n        ".join(map(str, self.support_anchor_list))
        return rtn

    def to_json(self):
        return json.dumps(dict(
            token = self.token,
            aoffset = self.approximate_offset,
            support = [anc.to_json() for anc in self.support_anchor_list],
            ))


def apply_insertion(base_text, insertion_list):
    """
    `insertion_list`: [(index:int, text:string)]: inserts text at index
    """
    insertion_list.sort()
    for index, text in sorted(insertion_list, reverse = True):
        base_text = base_text[:index] + text + base_text[index:]
    return base_text

def apply_anchor_range(anchor0, anchor1, base_text):
    return apply_anchor(anchor0, base_text), apply_anchor(anchor1, base_text)+len(anchor1.token)

def apply_anchor(anc, base_text):
    """
    returns exact begin and end offset
    based on `anchor`
    """

    idx_start = max(0,              anc.approximate_offset - len(anc.token) * PRE_MULTIPLIER)
    idx_end   = min(len(base_text), anc.approximate_offset + len(anc.token) * POST_MULTIPLIER) - len(anc.token)

    match_list = []
    idx_current = idx_start
    while idx_current < idx_end:
        idx_match = base_text[idx_current:].find(anc.token)
        if idx_match == -1:
            break
        match_list.append(idx_current+idx_match)
        idx_current = idx_current + idx_match + len(anc.token)

    print "LENGHT OF MATCH LIST", len(match_list)
    print match_list
    if len(match_list) is 1:
        return match_list[0]
    elif len(match_list) is 0:
        raise Exception("inexistent")
    else:
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

    for score, firstidx, token in tfidfer.bestn(current_document_index, N = 20):
        if len(anc.support_anchor_list) > 5: break
        if token == desired_token: continue
        support_anchor = Anchor()
        support_anchor.token = token
        support_anchor.approximate_offset = firstidx
        anc.support_anchor_list.append(support_anchor)

    return anc

def make_anchor_range(desired_text, approximate_offset, current_document_index, base_document_list):
    spl = tokenize(desired_text)
    token0 = spl[0]
    token1 = spl[-1]
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
Fusce ac turpis quis ligula lacinia aliquet. Mauris ipsum. Nulla metus metus, ullamcorper vel, tincidunt sed, euismod in, nibh. Quisque volutpat condimentum velit. this particular one is not the target is this the real no it is not but this target no also a fake this is the is it real not really no so actually this is the real target text but there is other text the rest is just there to confuse you but this is also real is this real the target is real this is but is that real this real there Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Nam nec ante. Sed lacinia, urna non tincidunt mattis, tortor neque adipiscing diam, a cursus ipsum ante quis turpis. Nulla facilisi. Ut fringilla. Suspendisse potenti. Nunc feugiat mi a tellus consequat imperdiet. 

            """,
            """
Vestibulum sapien. Proin quam. Etiam ultrices. Suspendisse in justo eu magna luctus suscipit. Sed lectus. Integer euismod lacus luctus magna. Quisque cursus, metus vitae pharetra auctor, sem massa mattis sem, at interdum magna augue eget diam. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Morbi lacinia molestie dui. Praesent blandit dolor. Sed non quam. In vel mi sit amet augue congue elementum. Morbi in ipsum sit amet pede facilisis laoreet. 
            """,
            """
Donec lacus nunc, viverra nec, blandit vel, egestas et, augue. Vestibulum tincidunt malesuada tellus. Ut ultrices ultrices enim. Curabitur sit amet mauris. Morbi in dui quis est pulvinar ullamcorper. Nulla facilisi. Integer lacinia sollicitudin massa. Cras metus. Sed aliquet risus a tortor. Integer id quam. Morbi mi. 
            """,
            ]
    highlighted_text = "this is the real target text"

    if True:
        offset_begin = 19
        testtxt = document_text_list[2]
        anc = make_anchor(highlighted_text, offset_begin, 2, document_text_list)
        ra0, ra1 = make_anchor_range(highlighted_text, offset_begin, 2, document_text_list)
        idx0, idx1 = apply_anchor_range(ra0, ra1, testtxt)
        print testtxt[:idx0] + colored(testtxt[idx0:idx1], "yellow", attrs=["bold"]) + testtxt[idx1:]

        run_apply_demo(anc, testtxt)

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
