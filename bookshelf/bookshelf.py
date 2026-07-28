# Copyright 2026 (AGPL-3.0-or-later), Miles K. Bertrand et al.

from abc import ABC, abstractmethod

# Base class inherited by composer.Corpus which contains book list, and by kalendar.KalendarCorpus. Avoids Kalendar depending on composer.
class Bookshelf:
    @abstractmethod
    def book_srcs():
        return book_srcs
