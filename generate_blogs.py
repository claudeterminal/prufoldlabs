#!/usr/bin/env python3
# Generates black-background / modern-white-font blog pages from verbatim article text.
import os, re, html

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blog")
os.makedirs(OUT, exist_ok=True)

PAGE = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Prufold Labs</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{background:#000;color:#ededed;font-family:'Geist',system-ui,sans-serif;line-height:1.7;-webkit-font-smoothing:antialiased;letter-spacing:-.011em}}
.top{{position:sticky;top:0;background:rgba(0,0,0,.7);backdrop-filter:blur(10px);border-bottom:1px solid #161616;padding:18px 28px;z-index:5}}
.top a{{color:#bdbdbd;text-decoration:none;font-size:14px;font-weight:500;letter-spacing:.02em}}
.top a:hover{{color:#fff}}
.wrap{{max-width:720px;margin:0 auto;padding:70px 24px 120px}}
h1.title{{font-size:clamp(30px,4.6vw,50px);font-weight:600;line-height:1.08;letter-spacing:-.03em;color:#fff;margin-bottom:18px}}
.byline{{color:#7d7d7d;font-size:14px;margin-bottom:34px}}
.rule{{height:1px;background:#1c1c1c;margin-bottom:40px}}
article{{font-size:17px;color:#cfcfcf}}
article p{{margin:0 0 22px}}
article h2{{font-size:26px;font-weight:600;color:#fff;letter-spacing:-.02em;margin:46px 0 16px;line-height:1.2}}
article h3{{font-size:20px;font-weight:600;color:#fff;letter-spacing:-.01em;margin:34px 0 12px}}
article strong{{color:#fff;font-weight:600}}
article a{{color:#fff;text-decoration:underline;text-underline-offset:3px;text-decoration-color:#555}}
article a:hover{{text-decoration-color:#fff}}
article ul,article ol{{margin:0 0 22px 22px}}
article li{{margin:0 0 9px}}
article blockquote{{border-left:2px solid #3a3a3a;padding:2px 0 2px 20px;margin:0 0 24px;color:#fff;font-size:19px;font-style:normal}}
article pre{{background:#0c0c0c;border:1px solid #1c1c1c;border-radius:10px;padding:18px;overflow-x:auto;margin:0 0 24px}}
article pre code{{font-family:'Geist Mono',monospace;font-size:13px;color:#cfcfcf;line-height:1.55;white-space:pre}}
.backbtn{{display:inline-block;margin-top:60px;color:#8a8a8a;text-decoration:none;font-size:14px}}
.backbtn:hover{{color:#fff}}
</style></head>
<body>
<div class="top"><a href="../index.html">← Prufold Labs</a></div>
<div class="wrap">
  <h1 class="title">{title}</h1>
  <div class="byline">{byline}</div>
  <div class="rule"></div>
  <article>{body}</article>
  <a class="backbtn" href="index.html">← All posts</a>
</div>
</body></html>"""

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    return s

def md_to_html(md):
    lines = md.split('\n')
    out=[]; i=0; n=len(lines)
    para=[];
    def flush_para():
        if para:
            out.append('<p>'+inline(' '.join(para).strip())+'</p>'); para.clear()
    while i < n:
        ln = lines[i]
        st = ln.strip()
        if st.startswith('```'):
            flush_para(); i+=1; code=[]
            while i<n and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i+=1
            i+=1
            out.append('<pre><code>'+html.escape('\n'.join(code))+'</code></pre>'); continue
        if st in ('---',''):
            flush_para(); i+=1; continue
        if st.startswith('### '):
            flush_para(); out.append('<h3>'+inline(st[4:])+'</h3>'); i+=1; continue
        if st.startswith('## '):
            flush_para(); out.append('<h2>'+inline(st[3:])+'</h2>'); i+=1; continue
        if st.startswith('# '):
            i+=1; continue
        if st.startswith('> '):
            flush_para(); q=[]
            while i<n and lines[i].strip().startswith('> '):
                q.append(lines[i].strip()[2:]); i+=1
            out.append('<blockquote>'+inline(' '.join(q))+'</blockquote>'); continue
        if re.match(r'^[-*] ', st):
            flush_para(); items=[]
            while i<n and re.match(r'^[-*] ', lines[i].strip()):
                items.append('<li>'+inline(lines[i].strip()[2:])+'</li>'); i+=1
            out.append('<ul>'+''.join(items)+'</ul>'); continue
        if re.match(r'^\d+\. ', st):
            flush_para(); items=[]
            while i<n and re.match(r'^\d+\. ', lines[i].strip()):
                items.append('<li>'+inline(re.sub(r'^\d+\. ','',lines[i].strip()))+'</li>'); i+=1
            out.append('<ol>'+''.join(items)+'</ol>'); continue
        para.append(st); i+=1
    flush_para()
    return '\n'.join(out)

from blog_data import ARTICLES

def esc(s): return html.escape(s)

# individual posts
for slug, title, byline, body in ARTICLES:
    page = PAGE.format(title=esc(title), byline=esc(byline), body=md_to_html(body))
    with open(os.path.join(OUT, slug + ".html"), "w") as f:
        f.write(page)

# blog index (black list of all posts)
rows = "".join(
    f'<a class="post" href="{slug}.html"><span class="pt">{esc(t)}</span><span class="pm">{esc(b.split(" • ",1)[1] if " • " in b else b)}</span></a>'
    for slug, t, b, _ in ARTICLES
)
INDEX = """<!DOCTYPE html><html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog — Prufold Labs</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000;color:#ededed;font-family:'Geist',system-ui,sans-serif;-webkit-font-smoothing:antialiased;letter-spacing:-.011em}
.top{position:sticky;top:0;background:rgba(0,0,0,.7);backdrop-filter:blur(10px);border-bottom:1px solid #161616;padding:18px 28px}
.top a{color:#bdbdbd;text-decoration:none;font-size:14px;font-weight:500}
.top a:hover{color:#fff}
.wrap{max-width:820px;margin:0 auto;padding:80px 24px 120px}
h1{font-size:clamp(34px,5vw,56px);font-weight:600;letter-spacing:-.03em;color:#fff;margin-bottom:44px}
.post{display:flex;justify-content:space-between;align-items:baseline;gap:24px;padding:26px 0;border-top:1px solid #1c1c1c;text-decoration:none}
.post:last-child{border-bottom:1px solid #1c1c1c}
.post:hover .pt{color:#fff}
.pt{font-size:21px;font-weight:500;color:#dcdcdc;letter-spacing:-.02em;line-height:1.25;transition:color .2s}
.pm{font-size:13px;color:#6c6c6c;white-space:nowrap;flex:0 0 auto}
@media(max-width:640px){.post{flex-direction:column;gap:6px}.pm{white-space:normal}}
</style></head>
<body>
<div class="top"><a href="../index.html">← Prufold Labs</a></div>
<div class="wrap"><h1>Blog</h1>__ROWS__</div>
</body></html>""".replace("__ROWS__", rows)
with open(os.path.join(OUT, "index.html"), "w") as f:
    f.write(INDEX)

print("generated", len(ARTICLES), "posts + index in", OUT)
