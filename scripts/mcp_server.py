# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2", "python-pptx>=0.6", "pillow"]   # mcp 2.x 把 FastMCP 改名为 MCPServer，先固定 1.x
# ///
"""Beamer 幻灯片的 MCP server：新建、编译、逐页检查（图片直接返回给模型看）、导出 .pptx / .key。
运行：uv run --script scripts/mcp_server.py     （依赖由 uv 按上面的内联声明自动安装）
注册到 Claude Code：claude mcp add beamer -- uv run --script /绝对路径/scripts/mcp_server.py
外部依赖：TeX Live（latexmk、pdflatex、bibtex）、poppler（pdftoppm、pdfinfo）。"""
import glob, os, re, shutil, subprocess, sys, tempfile

from mcp.server.fastmcp import FastMCP, Image

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template")
mcp = FastMCP("beamer")


def _run(cmd, cwd=None, timeout=600):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def _pages(pdf):
    _, out = _run(["pdfinfo", pdf])
    m = re.search(r"Pages:\s+(\d+)", out)
    return int(m.group(1)) if m else 0


@mcp.tool()
def new_deck(dest: str) -> str:
    """把模板（presentation.tex、components.tex 组件库、refs.bib、.latexmkrc、fig/）复制到新目录 dest。"""
    if os.path.exists(dest) and os.listdir(dest):
        return f"{dest} 已存在且非空，没有覆盖"
    shutil.copytree(TEMPLATE, dest, dirs_exist_ok=True)
    return f"已复制模板到 {dest}：改 presentation.tex；需要的元素从 components.tex 复制"


@mcp.tool()
def compile_deck(directory: str, tex: str = "presentation.tex") -> str:
    """在 directory 里用 latexmk 编译 tex（读 .latexmkrc，中间文件在 build/），返回页数和错误 / 溢出警告。
    不要在同一目录有 latexmk -pvc 运行时调用：两个进程同时写 PDF 会把它写坏。"""
    code, out = _run(["latexmk", "-interaction=nonstopmode", "-halt-on-error", tex], cwd=directory)
    stem = os.path.splitext(tex)[0]
    log = os.path.join(directory, "build", stem + ".log")
    warn = [l.strip() for l in open(log, errors="ignore") if re.match(r"(Overfull|!)", l.strip())] if os.path.exists(log) else []
    pdf = os.path.join(directory, stem + ".pdf")
    head = f"latexmk 退出码 {code}；{_pages(pdf) if os.path.exists(pdf) else 0} 页；{len(warn)} 处错误 / 溢出"
    return head + "".join(f"\n  {w}" for w in warn[:30]) + ("" if code == 0 else "\n--- 输出末尾 ---\n" + out[-2000:])


@mcp.tool()
def contact_sheet(pdf: str, cols: int = 4, dpi: int = 45) -> Image:
    """把 PDF 所有页渲染成一张缩略图拼图并返回图片，用来一次检查所有页的版式。"""
    from PIL import Image as PILImage
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf, f"{d}/p"], check=True)
        ims = [PILImage.open(f) for f in sorted(glob.glob(f"{d}/p-*.png"))]
        w, h = ims[0].size
        sheet = PILImage.new("RGB", (w * cols, h * ((len(ims) + cols - 1) // cols)), "white")
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        out = os.path.splitext(pdf)[0] + "_contact.png"
        sheet.save(out)
    return Image(path=out)


@mcp.tool()
def render_page(pdf: str, page: int, dpi: int = 90) -> Image:
    """把 PDF 第 page 页（从 1 开始）渲染成图片返回，用来放大看细节。"""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile", pdf, f"{d}/p"], check=True)
        out = os.path.join(tempfile.gettempdir(), f"beamer_page_{os.getpid()}_{page}.png")
        shutil.copy(f"{d}/p.png", out)
    return Image(path=out)


@mcp.tool()
def export_pptx(pdf: str, dpi: int = 200, keynote: bool = False) -> str:
    """从最终 PDF 导出 .pptx（每页一张高清图铺满 16:9，和 PDF 视觉一致）；keynote=True 时在 macOS 上再转 .key。"""
    cmd = [sys.executable, os.path.join(HERE, "pdf2pptx.py"), pdf, "--dpi", str(dpi)] + (["--key"] if keynote else [])
    code, out = _run(cmd)
    return out.strip() if code == 0 else f"导出失败（退出码 {code}）：\n{out[-2000:]}"


if __name__ == "__main__":
    mcp.run()
