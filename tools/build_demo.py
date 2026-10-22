# -*- coding: utf-8 -*-
"""由 demo/demo.md 生成单文件自包含 demo/demo.html。

为什么要自包含：demo.html 若外链 ../paper-typewriter.css 与字体，在预览面板、
别人的浏览器里一旦相对路径失效就整页白屏。这里把 CSS、字体、纸纹图像全部
内嵌成 data URI，产出一个可以直接双击 / 发人 / 挂 Pages 的单文件。

字体按 demo 实际用到的字符二次子集，体积从 9MB 压到 ~1MB。

用法：python tools/build_demo.py
"""
import base64
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent   # paper-typewriter-package/
CSS = ROOT / "paper-typewriter.css"
FONTS = ROOT / "paper-typewriter" / "fonts"
IMG = ROOT / "paper-typewriter" / "img"
DEMO_MD = ROOT / "demo" / "demo.md"
DEMO_HTML = ROOT / "demo" / "demo.html"
PYFTSUBSET = Path(shutil.which("pyftsubset") or "")

# 1) 读 md、去 front matter
raw = DEMO_MD.read_text(encoding="utf-8")
m_fm = re.match(r"^---\n(.*?)\n---\n", raw, flags=re.S)
front_matter = m_fm.group(1) if m_fm else ""
body = raw[m_fm.end():] if m_fm else raw

# 2) md → html（pymdown：~~删除线~~、==高亮==、任务列表都按 Typora 的 GFM 语义）
md = markdown.Markdown(extensions=[
    "tables", "fenced_code", "footnotes", "sane_lists", "attr_list",
    "pymdownx.tilde", "pymdownx.mark", "pymdownx.tasklist",
], extension_configs={"pymdownx.tasklist": {"custom_checkbox": False, "clickable_checkbox": False}})
html = md.convert(body)

# 3) front matter → Typora 风格的 meta 块
if front_matter:
    html = '<pre class="md-meta-block">' + front_matter + "</pre>\n" + html

# 4) 公式：块级 $$…$$ → 居中 mono 块，行内 $…$ → mono span（Typora 里由 MathJax 渲染，静态页降级为等宽显示）
html = re.sub(r"\$\$(.+?)\$\$", lambda m: '<div class="math-block">' + m.group(1).strip() + "</div>", html, flags=re.S)
html = re.sub(r"(?<!\$)\$([^$\n]+?)\$(?!\$)", lambda m: '<span class="math-inline">' + m.group(1) + "</span>", html)

# 3.5) 脚注标记 → Typora 类名（让主题的 .md-def-footnote / .md-footnote 规则命中）
html = re.sub(r'<li id="fn:', '<li class="md-def-footnote" id="fn:', html)
html = re.sub(r'<sup id="fnref', '<sup class="md-footnote" id="fnref', html)

# 4) 图片 → base64
def img_uri(p: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

prev = ROOT / "demo" / "preview-light.png"
if prev.exists():
    html = html.replace('src="preview-light.png"', f'src="{img_uri(prev, "image/png")}"')

# 5) 字体二次子集：只保留 demo 用到的字符
charset = set(re.sub(r"<[^>]+>", "", html))
charset |= set(" 0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
               "，。、；：？！“”‘’（）【】《》…—·~@#$%&*+-=<>/\\|_^`")
charset = {c for c in charset if c.strip()}
tmp = Path(tempfile.mkdtemp())
chars_file = tmp / "chars.txt"
chars_file.write_text("".join(sorted(charset)), encoding="utf-8")

subset_map = {}
for f in sorted(FONTS.glob("*.woff2")):
    out = tmp / f.name
    try:
        subprocess.run([str(PYFTSUBSET), str(f), f"--text-file={chars_file}",
                        "--flavor=woff2", f"--output-file={out}"],
                       check=True, capture_output=True)
        subset_map[f.name] = out
    except Exception as e:
        print("  子集失败，改用原文件:", f.name, e)
        subset_map[f.name] = f

# 6) 内嵌 CSS：url(...) → data URI
css = CSS.read_text(encoding="utf-8")

def repl_url(m):
    rel = m.group(1)          # ./paper-typewriter/fonts/xxx.woff2
    name = Path(rel).name
    if name in subset_map:
        return f'url("data:font/woff2;base64,{base64.b64encode(subset_map[name].read_bytes()).decode()}")'
    p = ROOT / rel.lstrip("./")
    if p.exists():
        ext = p.suffix.lower()
        mime = {".svg": "image/svg+xml", ".png": "image/png", ".woff2": "font/woff2"}.get(ext, "application/octet-stream")
        return f'url("data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}")'
    print("  跳过未找到的资源:", rel)
    return m.group(0)

css = re.sub(r'url\(["\']?(\./paper-typewriter/[^"\')]+)["\']?\)', repl_url, css)

# 7) 组装
SHIM = """
/* 模拟 Typora 的基础环境（真实 Typora 由 base.css 提供） */
html, body { margin: 0; padding: 0; }
#write { position: relative; }
body { min-height: 100vh; }
.math-inline { font-family: var(--font-code); font-size: .95em; color: var(--ink); }
.math-block { font-family: var(--font-code); text-align: center; margin: 1em 0;
              color: var(--ink); font-size: .95em; white-space: pre-wrap; }
.demo-note { margin: 3rem 0 2rem; padding-top: 1rem; font-size: .82rem;
             color: var(--ink-meta); border-top: 1px dashed var(--line); }
"""

out = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Paper Typewriter — 主题预览</title>
<style>
{css}
{SHIM}
</style>
</head>
<body>
<div id="write">
{html}
<div class="demo-note">本页由 <code>demo/demo.md</code> 渲染生成（<code>tools/build_demo.py</code>），CSS 与字体均已内嵌，可单文件分发。
在 Typora 中打开 <code>demo/demo.md</code> 并选择 Paper Typewriter 主题，可看到打字机模式、专注模式、光标视差等完整效果。</div>
</div>
</body>
</html>
"""
DEMO_HTML.write_text(out, encoding="utf-8")
print(f"已生成 {DEMO_HTML}")
print(f"大小: {DEMO_HTML.stat().st_size/1024/1024:.2f} MB（含 {len(subset_map)} 个内嵌字体子集）")
shutil.rmtree(tmp, ignore_errors=True)
