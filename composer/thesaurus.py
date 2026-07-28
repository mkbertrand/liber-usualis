import composer.psalms as psalms

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
            ret.extend(book.get_pile(pilequery))
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

class ContingentThesaurus(Thesaurus):
    def __init__(self, books, content_books):
        super().__init__(books)
        self.content_books = content_books

    def get_pile(self, pilequery):
        ret = []
        for book in self.content_books:
            ret.extend(book.get_pile(pilequery))
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
