# markdown-generator

A simple markdown generator for jinja2.

Contains a markdown to html converter `md_html.py` based on the python `markdown2` module
that additionally escapes both HTML characters and jinja2 template characters. It also
contains a module called `format_html.py` which allows multiple HTML files to be embedded
within one template.
