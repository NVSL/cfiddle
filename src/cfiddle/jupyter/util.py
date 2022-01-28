import time
from IPython.display import clear_output, HTML

def html_parameters(parameter_set):
    return "<br/>".join([f"{p} = {v}" for p,v in parameter_set.items()])

def changes_in(filename):
    old_last_change = None
    while True:
        try:
            current_last_change = os.path.getmtime(filename)
            if current_last_change != old_last_change:
                old_last_change = current_last_change
                clear_output(wait=True)
                yield None
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            return

def _render_hack(c):
    if isinstance(c, str):
        return f"""<pre>{c}</pre>"""
    
    try:
        return c._repr_html_()
    except:
        try:
            return c._repr_svg_()
        except:
            return f'<img src="data:image/png;base64,{c._repr_png_()}">'

def compare(content, headings=None):
    if headings is None:
        headings = [""] * len(content)
        
    return HTML("""
            <style>
        .side-by-side {
            display: flex;
            align-items: stretch;
        }
        .side-by-side-pane {
            margin-right:1em;
            border-right-style: solid;
            border-right-color: black;
            border-right-width: 1px;
            flex: 1;
        }
        .side-by-side-pane .heading{
            font-size: 1.5;
            font-weight: bold;
            text-align:center;
            border-bottom-style: dotted;
            border-bottom-width: 1px;
            border-bottom-color: gray;
            margin-left: 1em;
            margin-right: 1em;

        }
        </style>
        <div class="side-by-side"> """ +
                 
                 "".join([f"<div class='side-by-side-pane'><div class='heading'>{headings[i]}</div><div>{_render_hack(c)}</div></div>" for (i,c) in enumerate(content)]) +


                 """
        </div>
    """)

