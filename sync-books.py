import json
import subprocess
from pathlib import Path

from datamanage import DATA_ROOT

if Path('books.json').exists():
    for book in json.load(open('books.json')):
        destination = DATA_ROOT.joinpath('generated').joinpath(book['loc'])
        if destination.exists():
            subprocess.run(['git', '-C', destination, 'pull'], check=True)
        else:
            subprocess.run(['git', 'clone', book['src'], '--branch', book['branch'], destination])
else:
    print('books.json not detected.')
