import os
from datetime import datetime

# -- Project information -----------------------------------------------------

project = 'Check Application'
year = datetime.today().year
copyright = f'{year}, Yaroslav Khoruzhenko'
author = 'Yaroslav Khoruzhenko'

# -- General configuration ---------------------------------------------------

extensions = ['myst_parser']
source_suffix = ['.rst', '.md']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
if on_rtd:
    html_theme = 'default'
else:
    extensions.append('sphinx_rtd_theme')
    html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']
