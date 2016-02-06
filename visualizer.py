'''

quick and dirty server for browser rendering of processed text

'''


from flask import Flask, render_template_string

import anchortext as anc
from easydict import EasyDict


import textproc as tp
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










if __name__ == '__main__':

    app.run(debug=True)
