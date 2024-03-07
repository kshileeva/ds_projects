from bokeh.io import output_file, show
from bokeh.embed import file_html
from bokeh.layouts import column
import os

def open_files(directory):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            filepath = os.path.join(directory, filename)
            opened = open(filepath).read()
            files.append(opened)
    return files


directory = '/Users/kshileeva/repo/ds_projects'
bokeh_layout = column([file_html(file) for file in open_files(directory)])

output_file("combined_layout.html")
show(bokeh_layout)
