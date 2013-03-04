from collections import namedtuple
from glob import glob
import os
from os.path import join as pjoin
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

def make_tagged(**attr):
    import uuid
    myattr = attr.copy()
    myattr['borderstr'] = 'note' in attr and "border: 2px dashed red;" or ""
    myattr['uuid'] = str(uuid.uuid4())
    span = '''<span style="background-color: %(background_color)s; %(borderstr)s" onmouseout="document.getElementById('%(uuid)s').style.display='none';" onmouseover="document.getElementById('%(uuid)s').style.display='';">%(innerhtml)s</span>''' % myattr
    notebox = '''<div id="%s" style="font-family:Courier New, Mono; font-size: 12pt; position:absolute;width:50%%;border:2px solid gray;background-color:white;box-shadow: 0px 0px 10px black;display:none;">
    %s
    </div>''' % (myattr['uuid'], "<hr/>".join([
        "%s" % (attr[k])
        for k in ["lookup", "time", "highlight"]
        ]))
    return span + notebox

dnotecache = {}

NOTE_DIR = os.path.expanduser("~/note/org/book")

def process_html(viewer, html_orig):
    book_title = None
    
    # hackery: parse the content.opf that calibre (hopefully) generates to get the right title
    tmp_opf_filepath = os.path.join(os.path.dirname(viewer.path()), "content.opf")
    if os.path.exists(tmp_opf_filepath):
        xml = open(tmp_opf_filepath).read()
        flt_xml = [line for line in xml.split("\n") if "title>" in line]
        if len(flt_xml) is 1:
            book_title = p_tag.sub("", flt_xml[0]).strip()
        print("BOOK TITLE from %s: %s" % (tmp_opf_filepath, book_title))

    if book_title is None:
        # not reliable method to get book title!
        book_title = unicode(viewer.title())
        print("BOOK TITLE from viewer: %s" % (book_title))
    
    if book_title not in dnotecache:
        dnotecache[book_title] = {}
        
        note_yml_filename = book_title + ".yml"
        note_yml_filepath = pjoin(NOTE_DIR, note_yml_filename)
        find_yml_file = glob(note_yml_filepath)
        if find_yml_file:
            dnotecache[book_title] = yaml.load(open(note_yml_filepath))
            print("found yml: %s" % note_yml_filepath)
        print("search yml: %s" % note_yml_filepath)

    dnote = dnotecache[book_title]

    # preprocess html since we don't care about whitespace
    html = cleanstring(html_orig)

    lsmatchidx = []

    nextbeg, stop = 0, len(html)
    while nextbeg < stop:
        match = p_tag.search(html, nextbeg)
        if match is None: break
        lsmatchidx.append(Rec(nextbeg, match.start(), html[nextbeg:match.start()]))
        nextbeg = match.end()

    fulltext = ("".join([cleanstring(rec.txt) for rec in lsmatchidx])).replace('\n', ' ')
    
    lsmatcher = [cleanstring(entry['highlight'].strip()) for entry in dnote]
    
    for matcher, entry in zip(lsmatcher, dnote):
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
                        rec.txt = make_tagged(
                            background_color = entry.get('color', 'yellow'),
                            innerhtml = html[rec.beg:rec.beg+len(grabtxt)],
                            **entry
                            )
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
                    rec.txt = rec.txt[:recoffsetbeg] + (make_tagged(
                         background_color = entry.get('color', 'yellow'),
                         innerhtml = grabtxt,
                         **entry
                         )) + rec.txt[recoffsetend:]
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
    html = open("/tmp/epubtest/kindle_split_011.html").read().decode('utf-8')
    with open("/tmp/testout.html", "w") as ofile:
        ofile.write(process_html(note, html).encode('utf-8'))

