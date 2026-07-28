import composer.psalms as psalms

DEFAULT_PILE = {'formulae', 'litaniae-sanctorum','absolutiones-benedictiones', 'dies-lunae', 'nomen-temporis', 'benedictio-mensae'}

class Thesaurus:
    def __init__(self, *books):
        booklist = []
        for i in books:
            if type(i) is list:
                booklist.extend(i)
            else:
                booklist.append(i)
        self.books = booklist

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
                return {'tags': {query}, 'datum':psalms.get(book, query)}
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

class ContingentThesaurus(Thesaurus):
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
                    return {'tags': {query}, 'datum': book.retrieve_untagged_file(untagged)}
            raise Exception(f'No file found for {query}')

    def get_book_tags(self):
        for book in self.content_books:
            yield book.title
