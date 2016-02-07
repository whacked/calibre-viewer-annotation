'''

quick and dirty server for browser rendering of processed text

'''


from flask import Flask, render_template_string

import anchortext as at
from easydict import EasyDict


import textproc as tp

reload(at)
reload(tp)









app = Flask(__name__)


@app.route('/')
def index():
    ctx = EasyDict()
    ctx.para = tp.generate_paragraph()

    degrade_res = tp.degrade_latin(ctx.para)

    ctx.para_rendered = degrade_res.html_representation

    ctx.para_mod = degrade_res.text

    return render_template_string('''
<style>
/* text diff styling */
div.box {
    width: 600px;
    border: 1px solid gray;
    padding: 0.5em;
}

span.altered {
    background: orange;
    text-decoration: underline;
    color: green;
}

span.deleted {
    text-decoration: line-through;
    color: red;
}

</style>

<table class="box">
<tr>
<td>
{{ para }}

</td>

<td>
{{ para_mod }}

</td>

<td>
{{ para_rendered|safe }}

</td>
</tr>
</table>
    
''', **ctx)





@app.route('/anchortext')
def anchortext():
    ctx = EasyDict()



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

    out = ['''\

<pre>
commentary:

aqua = approx offset
red = relative offset

at the top level we are given an 'anchor' that corresponds to some part of a
document.  in practice, this is a highlight we want to save.

for the highlighted text, there is no other reference to which we can derive
the highlight's location, hence relative offset is None, and absolute offset is
the character-by-character offset from the start of the document where we
assume the highlight is found.

if the highlight is unique, we expect to be able to locate it within the
document even if some parts of the document get degraded. Even if the highlight
itself gets degraded in the original document, it is possible to do a fuzzy
substring search and find it, without the offset recorded.

if the highlight is NOT unique, AND the document AND the highlight are somehow
degraded (within limits), we want to rely on alternative methods to locate the
best guess of where the highlight should be. a real-life use case is if one was
proofreading a document, makes a highlight using an external annotation
storage, and makes corrections to the original text that the highlight
included.

for this use case, we will use text anchors.

general idea for creating anchors:

1. for each document, compile a ranking of words with highest information
value; call these "support words". we assume the high valued words are less
likely to get degraded, or when degraded, will still be sufficiently unique [1]

2. for each word within the highlighted string (or just the entire highlighted
string), find the 6 best support words, where best is a scoring based on
maximizing the support's information value and minimizing the distance between
the highlight's word and the support word.

general idea for applying anchors:

1. when given an anchor and its associated support information, locate the
support words within the document. Support should be deemed located if
sufficiently close to its specified within-document relative offset and
sufficiently similar to the origina support word (also see [1]).

2. locate the most similar word to the word in the highlight, similar based on
string similarity and minimization of both the initial encoded
document-relative offset (approx offset), and the support-relative offset
(relative offset).

3. repeat 1~2 for each of the words in the highlight string; if no hit is
found, use the majority of matches from other words in the highlight string to
make a final decision; for some threshold, we will assume failure, and the
highlight has been deleted.


[1] current implementation does not handle degradataion of support words. but
    one possible implementation is to re-compile the support word ranking list
    for the document every time, and when given a support word, find the most
    similar
</pre>




<style>
.approx {
    color:purple;
}
.applied {
    color:red;
}
.begin {
    color: brown;
}
.end {
    color: darkblue;
}
.attention {
    background-color: lime;
    border: 1px solid green;
}

/* anchor styling */
div.anchor-info * {
    margin-left: 8em;
    padding-left: 0.5em;
    border-left: 1px solid gray;
    border-top: 1px solid gray;
}
span.approx-offset {
    float: left;
    margin: 0;
    background: aqua;
    border: 1px solid blue;
}
span.relative-offset {
    float: left;
    margin: 0;
    background: red;
    border: 1px solid black;
}
span.combined-offset {
    float: left;
    margin: 0;
    background: purple;
    color: white;
    border: 1px solid black;
}

span.marker {
    font-size: x-small;
}

sup {
    background: #EEE;
    border-radius: 3px;
}
</style> 
            
            ''',
            
            ]

    def box(text):
        return '''<div style="border:1px solid black;margin:0.5em;font-family:monospace;">%s</div>''' % text
    def colored(text, color, attrs=None):
        extra_style = attrs and 'font-weight:%s;'%attrs[0] or ''
        return '''<span style="color:%s;%s">%s</span>''' % (color, extra_style, text)
    def run_apply_demo(anchor, text):
        idx = at.apply_anchor(anchor, text)
        return text[:idx] + colored(text[idx:idx+len(anchor.token)], "orange", attrs=["bold"]) + text[idx+len(anchor.token):]

    def apply_dmarker(text, dmarker):
        '''
        take a (str)text and a (dict)dmarker,
        where dmarker is of (int)offset : (str)marker
        where marker the css marker class

        and return a (str) where markers are inserted into the offsets
        '''
        dsymbol = {
            'approx': '?',
            'applied': '!',
            'begin': '&lt;&lt;',
            'end': '&gt;&gt;',
            'attention': '&nbsp;',
        }

        marked_text = text
        for i in reversed(sorted(dmarker.keys())):
            marker_type = dmarker[i]
            marked_text = marked_text[:i] + '<sup class="%s">%s</sup>'%(marker_type, dsymbol.get(marker_type, '#')) + marked_text[i:]
        return marked_text


    def render_anchor(anc):
        rtn = [
        '<div class="anchor-info">']

        d = anc.__dict__.copy()
        d['combined_offset'] = anc.approximate_offset + (anc.relative_offset or 0)
        rtn.append('''\
        <span class="approx-offset">%(approximate_offset)s</span>
        <span class="relative-offset">%(relative_offset)s</span>
        <span class="combined-offset">%(combined_offset)s</span>
        <div class="anchor-token">
        %(token)s
        </div>
        ''' % d)
        if anc.support_anchor_list:
            rtn.append('<div>supported by:</div>')
            for support in anc.support_anchor_list:
                rtn.append(render_anchor(support))

        rtn.append('</div>')
        return ''.join(rtn)

    # demo 1
    import random

    cur_doc_idx = 2

    offset_begin = 310
    testtxt = document_text_list[cur_doc_idx]
    ra0, ra1 = at.make_anchor_range(highlighted_text, offset_begin, cur_doc_idx, document_text_list)

    anc = at.make_anchor(highlighted_text, offset_begin, cur_doc_idx, document_text_list)
    out.append(render_anchor(anc))

    support_dmarker = {}
    for support in anc.support_anchor_list:
        support_dmarker[support.approximate_offset] = 'begin'
        support_dmarker[support.approximate_offset + len(support.token)] = 'end'
        combined_offset = support.approximate_offset + (support.relative_offset or 0)
        support_dmarker[combined_offset] = 'attention'
    out.append('''\
    <h4>mark support anchors</h4>
    %s
    ''' % (apply_dmarker(testtxt, support_dmarker)))


    anc.support_anchor_list = []
    ## screw up the offset; this should break the quick and dirty version
    out.append('''\
    <h4>break offset</h4>
    %s
    ''' % run_apply_demo(anc, ("blah " * 40) + "bleh bleh bleh this is the real target text 1 " + testtxt))

    placeholder = '___'
    to_degrade = random.choice(ra0.support_anchor_list).token
    idx0_degrade = testtxt.index(to_degrade)
    idx1_degrade = idx0_degrade + len(to_degrade)
    testtxt = testtxt.replace(to_degrade, placeholder)
    idx0, idx1 = at.apply_anchor_range(ra0, ra1, testtxt)

    out.append('''\
    <h4>rendered version of anchor applied to text with 1 anchor degradation (%s)</h4>
    %s
    ''' % (
        to_degrade,
        (testtxt[:idx0] + colored(testtxt[idx0:idx1], "orange", attrs=["bold"]) + testtxt[idx1:]).replace(
            placeholder, '<span style="background:red;">&nbsp;</span>'
        ),
    ))

    realtarget = highlighted_text + " 2"
    good0 = testtxt.index(realtarget)
    good1 = testtxt.index(realtarget) + len(realtarget)
    out.append('''\
    <h4>begin and end index markers</h4>
    %s
    ''' % apply_dmarker(testtxt, {
        good0: 'begin', good1: 'end',
    }))

    # demo 2
    testtxt = """
    we are the best the best, the the the best!
    """.strip()
    anc = at.Anchor()
    anc.token = "the"
    anc.approximate_offset = 18
    actual_idx = at.apply_anchor(anc, testtxt)

    marked_text = testtxt.strip()
    dpostproc = {}
    dpostproc[anc.approximate_offset] = 'approx'
    dpostproc[actual_idx] = 'applied'
    marked_text = apply_dmarker(testtxt.strip(), dpostproc)

    out.append('''
    <div>
    <h4>test simple anchor application</h4>

    approximate offset: <span class="approx">%(approx_offset)s</span>
    <br />
    applied offset: <span class="applied">%(applied_offset)s</span>
    <br />

    <div>
        <b>locate attempt:</b>
        <div>%(attempt)s</div>
    </div>
    <div>
        <b>rendered:</b>
        <div>%(rendered)s</div>
    </div>
    </div>
    ''' % dict(
        approx_offset = anc.approximate_offset,
        applied_offset = actual_idx,
        rendered = run_apply_demo(anc, testtxt),
        attempt = marked_text,
    ))


    ## test word scoring method
    out.append('''\
    <div>
    <h4>test word scoring</h4>
    <ul>
    %s
    </ul>
    </div>
    '''%(''.join(
        '<li>%.2f %s</li>' % (at.get_word_score(word), word)
        for word in
        '''
        test
        easy
        think
        quartz
        abc123fourvi
        queen
        zenith
        the
        '''.strip().split()
    )))

    return ''.join(box(text) for text in out)




if __name__ == '__main__':

    app.run(debug=True)
