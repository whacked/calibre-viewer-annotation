from collections import namedtuple
import yaml
import re

class Rec:
    def __init__(self, beg, end, txt):
        self.beg = beg
        self.end = end
        self.txt = txt

p_tag = re.compile('<[^>]*>')

p_stripspace = re.compile(r'\s+')
def cleanstring(s):
    return p_stripspace.sub(' ', s.replace('\n', '%%%NEWLINE%%%')).replace('%%%NEWLINE%%%', '\n').replace('\n ', '\n').replace(' \n', '\n')

tagged = '''<span style="background-color: yellow;">%s</span>'''

note = yaml.load(open("note.yml"))

html = open("/tmp/epubtest/kindle_split_011.html").read().decode('utf-8')

def process_html(note, html_orig):
    html = cleanstring(html_orig)

    # preprocess html since we don't care about whitespace

    lsmatchidx = []

    nextbeg, stop = 0, len(html)
    lastend = 0
    while nextbeg < stop:
        match = p_tag.search(html, nextbeg)
        if match is None: break
        lsmatchidx.append(Rec(nextbeg, match.start(), html[nextbeg:match.start()]))
        nextbeg = match.end()

    fulltext = ("".join([cleanstring(rec.txt) for rec in lsmatchidx])).replace('\n', ' ')

    lsmatcher = [cleanstring(entry['highlight'].strip()) for entry in note]

    for matcher in lsmatcher:
        idxmatchbeg = fulltext.find(matcher.replace('\n', ' '))
        if idxmatchbeg > -1:
            # find the real offset
            contentlen = 0

            lenremain = None
            for irec, rec in enumerate(lsmatchidx):

                if lenremain is not None:
                    if lenremain > 0:

                        grabtxt = rec.txt[:lenremain]
                        # print "SECOND GO: >>>>>>>>>> ", grabtxt
                        # print "LEN", lenremain
                        # print "ORIG:", rec.txt
                        rec.txt = tagged % (html[rec.beg:rec.beg+len(grabtxt)])
                        # print rec.txt
                        lenremain -= len(grabtxt)
                    if lenremain is 0:
                        break

                lastcontentlen = contentlen
                contentlen += rec.end - rec.beg
                # print contentlen, idxmatchbeg
                if lenremain is None and idxmatchbeg <= contentlen:
                    # offset localized to the current
                    # rec object
                    reclen = len(rec.txt)
                    recoffsetbeg = idxmatchbeg - lastcontentlen
                    recoffsetend = recoffsetbeg + min(reclen, len(matcher))

                    modbeg = rec.beg + recoffsetbeg
                    # modend = modbeg + len(rec.txt[]) len(matcher)
                    # print "the rec txt >>>>>>>>>>>>>>>", rec.txt
                    grabtxt = rec.txt[recoffsetbeg:recoffsetend]
                    rec.txt = rec.txt[:recoffsetbeg] + (tagged % grabtxt) + rec.txt[recoffsetend:]
                    # print irec, (tagged % (html[modbeg:modend]))

                    # hit a tag boundary, slurp the rest in next iter
                    if len(matcher) > reclen:
                        lenremain = len(matcher) - len(grabtxt)
                        continue
                    else:
                        break

    lsout = []
    lastend = 0
    for rec in lsmatchidx:
        lsout.append(html[lastend:rec.beg])
        lsout.append(rec.txt)
        lastend = rec.end
    lsout.append(html[lastend:])
    return "\n".join(lsout)

if __name__ == "__main__":
    with open("/tmp/testout.html", "w") as ofile:
        ofile.write(process_html(note, html).encode('utf-8'))

