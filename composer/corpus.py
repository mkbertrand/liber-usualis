# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

import copy
import warnings

from bookshelf import Bookshelf

import composer.psalms as psalms
from composer.util import transform_search
from composer.rite import Rite

DEFAULT_PILE = {'officium', 'formulae', 'litaniae-sanctorum','absolutiones-benedictiones', 'dies-lunae', 'nomen-temporis', 'benedictio-mensae'}

def anysearch(query, pile):
    for i in pile:
        if type(i['tags']) is list:
            for j in i['tags']:
                if j.issubset(query):
                    ret = copy.copy(i)
                    ret['tags'] = j
                    yield ret
        elif i['tags'].issubset(query):
            yield copy.copy(i)

class Corpus(Bookshelf):
    def __init__(self, *books):
        booklist = []
        for i in books:
            if type(i) is list:
                booklist.extend(i)
            else:
                booklist.append(i)
        self.books = booklist

    def book_srcs(self):
        return [book.src for book in self.books]

    def getcategory(self, category):
        finds = [book.getcategory(category) for book in self.books if book.hascategory(category)]
        if all(type(cat) is frozenset for cat in finds):
            return set().union(*finds)
        else:
            ret = []
            for i in finds:
                ret.extend(i)
            return ret

    def getdiscrimen(self, discrimen):
        finds = [book.getdiscrimen(discrimen) for book in self.books if book.hasdiscrimen(discrimen)]
        ret = []
        for i in finds:
            ret.extend(i)
        for tag in self.get_book_tags():
            ret.append(frozenset({tag}))
        return ret

    def get_pile(self, pilequery):
        ret = []
        for book in self.books:
            ret.extend(book.get_pile(pilequery | DEFAULT_PILE))
        return ret

    def get_untagged(self, query):
        for book in self.books:
            try:
                return psalms.get(book, query)
            except:
                pass

    def get_book_tags(self):
        for book in self.books:
            yield book.title

    def expand_cat(self, category):
        def expandopenedcat(category):
            if type(category) is set or type(category) is frozenset:
                ret = set()
                for i in category:
                    if i.startswith('/'):
                        ret |= self.expand_cat(i[1:])
                    else:
                        ret.add(i)
                return ret
            elif type(category) is list:
                return expandopenedcat(set().union(*category))
            else:
                raise RuntimeError(str(category))

        def expandnamedcat(category):
            return expandopenedcat(self.getcategory(category))

        return expandnamedcat(category) if type(category) is str else expandopenedcat(category)

    def contradicted_cats(self, category, tags):
        category = self.getcategory(category)
        if type(category) is set or type(category) is frozenset:
            return []
        elif type(category) is list:
            for subcat in category:
                subcat = self.expand_cat(subcat)
                if sum([tag in tags for tag in subcat]) > 1:
                    yield subcat
        else:
            return RuntimeError()

    # Numerical rank of query tagset according to a table of tagsets. Outputs a binary number with 1 in positions where the tagset at that table position was a subset of the query.
    def discriminate(self, table: str, tags: set):
        table = self.getdiscrimen(table)
        val = 0
        for i in range(0, len(table)):
            if len(table[i]) == 1 and list(table[i])[0].startswith('/'):
                val |= (not tags.isdisjoint(self.expand_cat(list(table[i])[0]))) << (len(table) - i - 1)
            else:
                include = set(filter(lambda a: a[0] != '!', table[i]))
                exclude = {a[1:] for a in table[i] - include}
                # Adds 1 or 0 lower on the number as the position in the table increases using binary operators. The higher the position in the table (IE the farther down in the table), the lower precedence something is.
                val |= include.issubset(tags) and exclude.isdisjoint(tags) << (len(table) - i - 1)
        return val

    def search(self, query, multipleresults = False, multipleresultssort = None, pilemod = []):
        for i in query:
            if i.startswith('/'):
                try:
                    return {'tags': {i}, 'datum':self.get_untagged(i), 'quaesitum': query}
                except FileNotFoundError:
                    return None

        pile = self.get_pile(query) + pilemod
        query |= set(self.get_book_tags())
        result = list(anysearch(query, pile))

        # If there is a non-zero amount of results discrimination is guaranteed to yield at least one result
        if len(result) == 0:
            warnings.warn(f'0 tags found for queries {list(query)} when searching {query}')
            return None

        for rule in self.getdiscrimen('general'):
            def discrim(item):
                tags = item['tags']
                if len(rule) == 1 and list(rule)[0].startswith('/'):
                    return not tags.isdisjoint(self.expand_cat(list(rule)[0]))
                else:
                    include = set(filter(lambda a: a[0] != '!', rule))
                    exclude = {a[1:] for a in rule - include}
                    return include.issubset(tags) and exclude.isdisjoint(tags)
            resultvalues = list(map(discrim, result))
            if any(resultvalues):
                result = [v for i, v in enumerate(result) if resultvalues[i]]
            if len(result) == 1:
                return transform_search(query, result[0])

        result = list(sorted(result, key=lambda a: len(a['tags']), reverse=True))
        if len(result[0]['tags']) != len(result[1]['tags']):
            return transform_search(query, result[0])
        elif not multipleresults:
            raise RuntimeError(f'Multiple equiprobable results for queries {query}:\n{result[0]}\n{result[1]}')
        else:
            return list([transform_search(query, i) for i in sorted(filter(lambda a : len(a['tags']) == len(result[-1]['tags']), result), multipleresultssort)])

# Special commemoration handling. Commemorations are hard because they rely on eachother and differ in number by day.
    def handlecommemorations(self, item, selected, alternates):
            ret = []
            commemorations = sorted(list(filter(lambda a : 'commemoratio' in a, alternates)), key=lambda a:self.discriminate('rank', a), reverse=True)
            for i in commemorations:
                ret.append(self._process({'formula','formula-commemorationis'}, i | (item - {'commemorationes'}), alternates))
            if len(commemorations) != 0:
                ret.append(self._process({'collecta','terminatio','commemoratio'}, commemorations[-1] | (item - {'commemorationes'}), alternates))
            return {'tags':{'commemorationes'}, 'datum':ret}

    def _process(self, item, selected, alternates, pilemod = [], permit_empty = True):
        if item is None:
            return 'Absens'
        if selected is None:
            selected = frozenset()
        if alternates is None:
            alternates = []

        if type(item) is dict and 'quaere' in item:
            item['quaere'] = frozenset(item['quaere'])
            pilemod = [{'tags': item['quaere'], 'datum': item['datum']}]
            item = item['quaere']

        # An entry within an item that is a tagset is calling to search further for sub-items.
        if type(item) is set or type(item) is frozenset:
            selected = copy.deepcopy(selected)
            # Only remove positional tags when they are contradicted (for example, when the nona reading is requested by officium-capituli, remove officium-capituli)
            contras = set().union(*self.contradicted_cats('positionales', item | selected))
            selected -= contras

            result = None
            if not any('/' in i for i in item):
                for i in range(len(alternates)):
                    # Basically if the tagset is explicitly calling for some day's propers, remove the other day self to facilitate this
                    if 'occurrens' in item and item & self.expand_cat('temporale') <= alternates[i]:
                        item -= {'occurrens'}
                        alternates = copy.copy(alternates)
                        alternates.append(selected - self.expand_cat('positionales'))
                        selected = alternates.pop(i) | (selected & self.expand_cat('positionales'))
                        item -= self.expand_cat('temporale')
                        break

                    # If there is an alternate with a specific object and position, it should be imposed on this tagset even if the tagset doesn't otherwise want a different day's item
                    # Sometimes there are explicit tagsets in alternates that specify certain things (as oppo/sed to above when the data itself requests something)
                    elif item | (selected & self.expand_cat('positionales')) <= alternates[i]:
                        alternates = copy.copy(alternates)
                        alternates.append(selected)

                        if len(list(self.contradicted_cats('positionales', item | alternates[i] | selected))):
                            selected = alternates.pop(i)
                        else:
                            selected = alternates.pop(i) | (selected & self.expand_cat('positionales'))
                        result = self.search(item | selected, pilemod=pilemod)
                        break

            if result is None:
                # Only remove tags referring to propers and commons and whatnot if a different set is suggested
                # This is different than the occurrens system because we're not asking about something on the specific day (for example, we want the ferial readings of the day)
                # but rather we may want the readings for the Common of the Blessed Virgin which isn't specific day-to-day
                if len(item & self.expand_cat('temporale')) != 0:
                    selected -= set().union(*self.contradicted_cats('temporale', item | selected))
                    selected |= item & self.expand_cat('temporale')

                result = self.search(item | selected, pilemod=pilemod)

            if result is None and 'commemorationes' in item:
                return self.handlecommemorations(item, selected, alternates)

            # If result is still None at this point, just tell user what was searched for
            if result is None and permit_empty:
                # It has to be sorted for testing purposes
                return str(sorted(list(item | selected)))
            elif result is None:
                return None
            selected |= item
            response = self._process(result, selected, alternates)

            return response

        elif type(item['datum']) is list:
            ret = []
            for i in item['datum']:
                if type(i) is str:
                    if 'N.' in i:
                        i = i.replace('N. et N.', 'N.').replace('N.', self.search(item['tags'] | {'n'} | selected)['datum'])
                    ret.append(i)
                elif i is None:
                    ret.append(None)
                else:
                    iprocessed = self._process(i, selected, alternates)
                    if iprocessed is None:
                        ret.append('Absens')
                    elif type(iprocessed) is list:
                        ret.extend(iprocessed)
                    else:
                        ret.append(iprocessed)
            item['datum'] = ret if len(ret) != 1 else ret[0]
            return item

        # Often in the text there will be an N. replaced with the celebrated Saint's name.
        if type(item) is dict and item['datum'] and 'N.' in item['datum']:
            item['datum'] = item['datum'].replace('N. et N.', 'N.').replace('N.', self.search(item['tags'] | {'n'} | selected)['datum'])
        return item

    def compose(self, query, selected, alternates) -> Rite:
        return Rite(self._process(query, selected, alternates))

    def get_name(self, tagset):
        resp = self._process({'nomen'}, tagset, [])
        name = resp['datum'] if 'datum' in resp else '+'.join(tagset)
        if type(name) is list:
            name = (name[0] + name[1]['datum']) if 'datum' in name[1] else '+'.join(tagset)
        return name

class CaputCorpus(Corpus):
    # Searches only entries tagged 'caput' within the primary corpus's own books.
    # This lets section headers ('caput' entries) live alongside the body content they
    # head, in the same tagged/ files, while still being resolvable independently
    # for attachment via Rite.superimpose() rather than composed into 'datum'.

    # The full vocabulary of header-level tags. An entry always carries 'caput' and may
    # additionally carry one of the other two to select its render level; because
    # search() injects all three into every query unconditionally (below), any entry can
    # freely require one as part of its own tags without that tag ever needing to already
    # be part of a node's real liturgical context.
    LEVELS = frozenset({'caput', 'sectio', 'annotatio'})

    def get_pile(self, pilequery):
        def has_caput(entry):
            tags = entry['tags']
            if type(tags) is list:
                return any({'caput', 'nomen', 'basis-nominis'} & t for t in tags)
            return {'caput', 'nomen', 'basis-nominis'} & tags
        return [entry for entry in super().get_pile(pilequery) if has_caput(entry)]

    def search(self, query, multipleresults = False, multipleresultssort = None, pilemod = []):
        # Header lookups never resolve untagged resources (e.g. /psalmi/... references);
        # only tagged 'caput' entries are relevant here.
        if any(i.startswith('/') for i in query):
            return None
        return super().search(query | self.LEVELS, multipleresults, multipleresultssort, pilemod)

class ContingentCorpus(Corpus):
    def __init__(self, books, content_books):
        super().__init__(books)
        self.content_books = content_books

    def get_pile(self, pilequery):
        ret = []
        for book in self.content_books:
            ret.extend(book.get_pile(pilequery | DEFAULT_PILE))
        return ret

    def get_untagged(self, query):
        if query.startswith('/psalmi'):
            return {'tags': {query}, 'datum':psalms.get(self.content_books[0], query)}
        else:
            for book in self.content_books:
                untagged = book.has_untagged(query)
                if untagged:
                    return book.retrieve_untagged_file(untagged)
            raise Exception(f'No file found for {query}')

    def get_book_tags(self):
        for book in self.content_books:
            yield book.title
