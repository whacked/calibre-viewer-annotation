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

<style>
.approx {
    color:purple;
}
.applied {
    color:red;
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

span.marker {
    font-size: x-small;
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


    def render_anchor(anc):
        rtn = [
        '<div class="anchor-info">']
        rtn.append('''\
        <span class="approx-offset">%(approximate_offset)s</span>
        <span class="relative-offset">%(relative_offset)s</span>
        <div class="anchor-token">
        %(token)s
        </div>
        ''' % anc.__dict__)
        if anc.support_anchor_list:
            rtn.append('<div>supported by:</div>')
            for support in anc.support_anchor_list:
                rtn.append(render_anchor(support))

        rtn.append('</div>')
        return ''.join(rtn)

    # demo 1
    import random

    offset_begin = 310
    testtxt = document_text_list[2]
    ra0, ra1 = at.make_anchor_range(highlighted_text, offset_begin, 2, document_text_list)

    anc = at.make_anchor(highlighted_text, offset_begin, 2, document_text_list)
    out.append(render_anchor(anc))

    anc.support_anchor_list = []
    ## screw up the offset; this should break the quick and dirty version
    out.append(run_apply_demo(anc, ("blah " * 40) + "bleh bleh bleh this is the real target text 1 " + testtxt))

    testtxt = testtxt.replace(random.choice(ra0.support_anchor_list).token, '')
    idx0, idx1 = at.apply_anchor_range(ra0, ra1, testtxt)

    out.append(testtxt[:idx0] + colored(testtxt[idx0:idx1], "orange", attrs=["bold"]) + testtxt[idx1:])

    realtarget = highlighted_text + " 2"
    good0 = testtxt.index(realtarget)
    good1 = testtxt.index(realtarget) + len(realtarget)

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
    dpostproc[anc.approximate_offset] = '<sup class="approx">?</sup>'
    dpostproc[actual_idx] = '<sup class="applied">!</sup>'
    for i in reversed(sorted(dpostproc.keys())):
        marked_text = marked_text[:i] + dpostproc[i] + marked_text[i:]

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
