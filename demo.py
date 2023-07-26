from flask import Flask, redirect
from md_html import md_html
from format_html import Formatter
from jinja2 import FileSystemLoader
from glob import glob

app = Flask(__name__)
app.config["FORMATTER_BLOCK_LOADER"] = FileSystemLoader("html")
formatter = Formatter(app)

@app.route("/")
def index():
    page = formatter.create_page("index.html")

    page.add_block("b1", "1.html")
    page.add_block("b2", "2.html")
    return page.render(b1_name="1.html", b2_name="2.html")

@app.route("/reload_md")
def reload():
    files = glob("./md/*.md")
    files.sort(key=str.lower)
    list(map(md_html, files))

    return redirect("/")

if __name__ == "__main__":
    app.run()