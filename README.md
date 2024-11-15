# Liber Usualis Project

A project dedicated to making the Mass, Hours, and Rites of various editions of the Roman Rite easily accessible and beautifully formatted with or without their chants.

## Program Design

The Liber Usualis codebase is primarily data-driven, with very few hard-coded elements, opting instead to have a tag-lookup system for constructing Rites.

## Usage

### Installation

```bash
git clone https://github.com/mkbertrand/liber-usualis
cd liber-usualis
pip install bottle pytest
```

### Running

To run only the backend, backend.py is run as follows:

```bash
./backend.py
```

To run the frontend server (by default on localhost:8080, frontend.py is run as follows:

```bash
./frontend.py
```

## Author

Miles Bertrand

## Contributors

Albert-Emanuel Milani

Jacob Heilman

## Additional Credit

Benjamin Bloomfield (whose Javascript code I 'borrowed' and whose Compline project initially inspired this project)

## License

All files within this project are released under the GNU Affero General Public License (AGPL-3.0 or later) regardless of whether this is indicated within the file. All files only have the name Miles K. Bertrand explicitly listed (with exception to frontend/resources/js/gabc-chant.js . This does not imply that Miles K. Bertrand is the exclusive contributor to these files.
