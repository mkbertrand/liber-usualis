import json
import subprocess
from pathlib import Path

DEST_ROOT = Path('data-chant')

for book in json.load(open('books.json')):
    destination = DEST_ROOT.joinpath(book['loc'])
    if destination.exists():
        subprocess.run(['git', '-C', destination, 'pull'], check=True)
    else:
        subprocess.run(['git', 'clone', book['src'], '--branch', book['branch'], destination])
