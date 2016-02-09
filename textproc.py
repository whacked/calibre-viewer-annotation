import copy
import toolz as z
import math
import faker
import random
import string
from easydict import EasyDict

def generate_paragraph(N=10):
    f = faker.Factory.create()
    slist = f.sentences(N)
    return ' '.join(slist)


def degrade_latin(para,
        om_frac   = 0.1,
        com_frac  = 0.1,
        max_N_om  = 5,
        max_N_com = 5,
        ):
    '''
    'latin' because this tokenizes using str.split

    takes a (str)paragraph
    returns a (str)paragraph'
    with possible degradations (errors):
    - omissions (deletions)
    - commissions (alterations)

    arguments:
    om_ratio, com_ratio:
        fraction of items to alter,
        where the basis is the number of TOKENS
                        
    max_N_om, max_N_com:
        maximum whole number count of
        tokens to alter
    '''

    buf = para.split()
    ntoken_ = len(buf)

    # a convenience rendered version
    html_rep = copy.copy(buf)
    result = EasyDict(
        omission_index_list = [],
        commission_index_list = [],
    )

    OM_LIMIT = int(math.ceil(om_frac*ntoken_))
    COM_LIMIT = int(math.ceil(com_frac*ntoken_))

    # run omissions first
    ilist = range(ntoken_)
    random.shuffle(ilist)
    result.omission_index_list = list(z.take(min(OM_LIMIT, max_N_om), ilist))
    result.omission_index_list.sort()

    for i in reversed(result.omission_index_list):
        del buf[i]
        html_rep[i] = '<span class="deleted">%s</span>'%html_rep[i]

    # THIS HAS CHANGED!
    ntoken_ = len(buf)

    # create new index -> original index mapping
    imapping = dict((i,i) for i in range(ntoken_))
    for i_deleted in result.omission_index_list:
        for i_inc in range(i_deleted, ntoken_):
            imapping[i_inc] += 1

    # then run commissions
    ilist = range(ntoken_)
    random.shuffle(ilist)
    com_idx_list = z.take(min(COM_LIMIT, max_N_com), ilist)
    for i in reversed(sorted(com_idx_list)):
        token = buf[i]
        j_degrade = random.randint(0, len(token)-1)
        while True:
            ch = random.choice(string.ascii_lowercase)
            if ch != token[j_degrade]:
                break
        buf[i] = token[:j_degrade]+ch+token[j_degrade+1:]
        original_index = imapping[i]
        #result.commission_index_list.append(original_index)
        html_rep[original_index] = \
                token[:j_degrade] + \
                '<span class="altered">%s</span>'%ch + \
                token[j_degrade+1:]

    result.text = ' '.join(buf)
    result.html_representation = ' '.join(html_rep)
    return result



