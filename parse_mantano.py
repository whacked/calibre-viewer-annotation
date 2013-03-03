import sys, re, yaml
import xerox

import BeautifulSoup
import dateutil.parser as dateparser

STYLE_NOTEBLOCK = u"margin-left:10px;margin-top:20px;padding-bottom:20px;"

STYLE_NOTEENTRY = u"padding-top: 10px;margin-left:20px;padding-bottom:20px;border-bottom: #AAA dashed 1px;"
STYLE_NOTETEXT = u"border-left-color: #999;border-left-style: solid;border-left-width: 4px;padding-bottom: 2px;padding-left: 10px;padding-right: 5px;padding-top: 2px;"
STYLE_LOOKUP = u"margin-top:10px;margin-top:0px;vertical-align: middle;padding-top:10px;padding-left: 40px;margin-bottom: 10px;border-bottom-color: #DDD;border-bottom-style: dotted;border-bottom-width: 1px;"
STYLE_PAGENUM = u"float:right;text-align:right;margin-top: 12px;"
STYLE_RE_HIGHLIGHT = re.compile(r"margin-bottom: 10px;padding-bottom: 2px;padding-left: 10px;padding-right: 5px;padding-top: 2px;background-color:#.+")


if __name__ == "__main__":
    html = open(sys.argv[-1]).read()
    soup = BeautifulSoup.BeautifulSoup(html)

    lsout = []
    lsvocab = []

    for noteblock in soup.findAll(style = STYLE_NOTEBLOCK):
        for noteentry in noteblock.findAll(style = STYLE_NOTEENTRY):
            # assume there are only 1 per note entry
            find_lookup  = noteentry.find(style = STYLE_LOOKUP)
            
            find_pagenum = noteentry.find(style = STYLE_PAGENUM)
            find_highlight = noteentry.find(style = STYLE_RE_HIGHLIGHT)
            pagenum, datestr = find_pagenum.text.split(' - ', 1)

            colorstr = find_highlight['style'].split('background-color:')[-1].strip(';')
            # vocab
            if colorstr == "#d4ebc4;":
                lsvocab.append(find_highlight.text)
                continue

            myd = dict(
                lookup = "%s... (%s)" % (find_lookup.text, pagenum),
                highlight = find_highlight.text,
                color = colorstr,
                time = str(dateparser.parse(datestr)),
                )

            find_notetext = noteentry.find(style = STYLE_NOTETEXT)
            if find_notetext:
                myd['note'] = find_notetext.text
            
            lsout.append(myd)

    xerox.copy(yaml.safe_dump(lsout, default_flow_style = False))
    print lsvocab
