from markdown2 import markdown
from io import TextIOWrapper
import hashlib
import re

ESCAPE = {
    "{{": "&#123;&#123;",
    "}}": "&#125;&#125;",
    "{%": "&#123;&#37;",
    "%}": "&#37;&#125;",
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;"
}

ESCAPE_PATTERN = re.compile('|'.join(re.escape(k) for k in ESCAPE.keys()))

def replace_filename(md_file: str) -> str:
    """
    Creates an html filename from a markdown filename.
    Extracted from md_html to allow cloud storage to be used instead of traditional storage.
    """

    return md_file.replace("./md/", "./html/").replace(".md", ".html")

def open_file(file:str, method: str) -> TextIOWrapper:
    """
    Opens a file similar to python's open() method.
    Extracted from md_html to allow cloud storage to be used instead of traditional storage.
    """

    return open(file, method)

def calculate_hash(md_file: str) -> str:
    """
    Calculates a hash for a markdown file. Used to identify versions and avoid recompiling identical code.
    Extracted from md_html to allow cloud storage to be used instead of traditional storage.
    """

    with open_file(md_file, "rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def escape(md: str) -> str:
    """
    Escapes character sequences that may have malicious uses, eg. < > tags used by HTML, or {{ }} and {% %} tags used by server-side rendering engines. 
    Uses the 'ESCAPE' dictionary to find sequences and replace them with escaped code.
    """

    return ESCAPE_PATTERN.sub(lambda x: ESCAPE[x.group()], md)

def md_html(md_file: str):
    """
    Converts a markdown file to html.
    IO-based functions are extracted to separate functions to allow overrides for cloud storage solutions instead of traditional storage media.
    """

    html_file = replace_filename(md_file)
    md_hash = calculate_hash(md_file)

    with open_file(html_file, "r") as f:
        if f.readline().strip() == md_hash:
            print(f"Skipping {md_file}@{md_hash[:8]}; {html_file} is already the latest version")
            return

    print(f"Compiling {md_file}@{md_hash[:8]} at {html_file}")

    with open_file(md_file, "r") as f:
        md = escape(f.read())

    with open_file(html_file, "w") as f:
        f.write(md_hash + "\n")
        f.write(markdown(md))


if __name__ == "__main__":
    from multiprocessing import Pool, cpu_count
    from glob import glob
    
    PARALLEL = False

    files = glob("./md/*.md")
    files.sort(key=str.lower)

    if PARALLEL:
        processes = cpu_count()
        print(f"Launching {processes} processes")

        with Pool(processes) as pool:
            pool.map(md_html, files)
    else:
        list(map(md_html, files))