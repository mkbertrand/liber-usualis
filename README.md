# Liber Usualis Project

A project dedicated to making the Mass, Hours, and Ritual of various editions of the Roman Rite available and easily accessible.

The currently existing Divine Office websites tend to only maintain specific preferred recensions of the Office, often either completely ignoring or putting little development effort into alternative versions of the Office. Additionally, no existing websites attempt to generate completed liturgies with their chants, leaving the difficult task of finding the correct chants to the cleric or choir. Finally, there are issues with customization which is required for local & regional feasts.

## Historical Overview

The Roman Breviary as a book was promulgated in its entirety after the Council of Trent in 1568 and subsequently received revisions referring to that original version: added, subtracted, and moved feast days, modifications to rubrics, a new hymnal, and ultimately a radically novel Psalter and rubrics. These last two changes, unlike the others, very much changed the Hours at their core and defined an altogether different "logic" than the original Hours followed.

To understand the pre-Pian Breviary in the context of the post-Pian Breviary is impossible, since the Pius X Breviary is dependent on the Tridentine original, and not vice-versa. To address this problem, the traditional Breviary program is designed _specifically_ for the pre-Pius X Breviary, but will include the relevant data for the Divino Afflatu reforms for those who wish to use the reformed Breviary from before 1971. After 1971, however, the Liturgia Horarum was promulgated as an entirely new book, and is a self-contained book which does not require reference to previous editions of the Roman Breviary.

The Roman Missal, similarly, underwent revisions after its initial promulgation in 1570 (albeit those of a more straightforward nature). Similarly to the Breviary, these changes were not in the form of an entirely new Missal, but were revisions on existing Missals until the promulgation of St. Paul VI's Missal in 1969.

## Program Design

The Liber Usualis project is designed to allow the data (which is stored in json files) to almost entirely define the behavior of the program. The data is stored as lists of json objects which have tagsets which uniquely identify them by their occasion, function, tone, &c. These objects, in turn, can include other objects (with no intended depth limit) by calling for a tagset. To match a query, an object's tagset must be a **subset** of the query. The tags provided by hard-coded queries are, in almost all cases, are supplemented by auxiliary tagsets called cascades which, as their name suggests, are applied also to further requests. The tags of an existing object are also added to the cascades of its own lower-layer searches. There exists another method of searching called forwards-to, which allows cascade-independent searches to semantically-unrelated objects.

### Kalendar

If tagsets and objects are the language of the actual data, there needs to be a method of deciding _which_ tagsets to look for. This is the job of the kalendar (as well as directly from user input). The kalendar's job is accomplished by the initial setting of series of entries (defined and distinguished only by their tagsets) according to their cycles, but also by the subsequent translation, modification, and removal of tagsets according to their coincidence with other tagsets.

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

To run the standalone frontend, frontend.py is run as follows:

```bash
./frontend.py
```

## Author

Miles Bertrand

## Contributors

Albert-Emanuel Milani

Jacob Heilman

## Additional Credit

Benjamin Bloomfield (whose Javascript code I blatantly plagiarized and whose Compline project initially inspired this project)
