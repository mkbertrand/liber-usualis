# Liber Usualis Project

A project dedicated to making the Mass, Hours, and Rites of various editions of the Roman Rite easily accessible and beautifully formatted with or without their chants.

## Program Design

The Liber Usualis codebase is primarily data-driven, with very few hard-coded elements, opting instead to have a tag-lookup system for constructing Rites.

## Usage

### Installation

```bash
git clone https://github.com/mkbertrand/liber-usualis
git clone https://github.com/mkbertrand/franciscan-chant-closet
cd liber-usualis
pip install bottle pytest diff-match-patch waitress wsgi-request-logger
```

Note: diff-match-patch is only necessary for test_breviarium.
### Running

To run the server (by default on localhost:8080, frontend.py is run as follows:

```bash
./frontend.py
```
Note: for full functionality, franciscan-chant-closet must be run at the same time and must be able to bind to port 40081.
## Author

Miles Bertrand

## Contributors

Albert-Emanuel Milani

Jacob Heilman

## Additional Credit

Benjamin Bloomfield (whose Javascript code I 'borrowed' and whose Compline project initially inspired this project)

## License

All files within this project are released under the GNU Affero General Public License (AGPL-3.0 or later) unless otherwise indicated in the file.
