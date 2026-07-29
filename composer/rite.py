from __future__ import annotations
import copy
import functools
import warnings

class Rite:
    def __init__(self, rite: dict):
        self.rite = rite

    def superimpose(self, corpus, tag: str) -> Rite:
        @functools.lru_cache(maxsize=64)
        def get_relevant(tagset: frozenset):
            warnings.simplefilter('ignore')
            return corpus.process(tagset, None, None, permit_empty = False)

        def traverse_rite(obj):
            if type(obj) is dict and 'quaesitum' in obj:
                tran = get_relevant(frozenset(obj['quaesitum']))
                if tran:
                    obj[tag] = tran
            if type(obj) is dict:
                traverse_rite(obj['datum'])
            elif type(obj) is list:
                for v in obj:
                    traverse_rite(v)
        rite = copy.deepcopy(self.rite)
        traverse_rite(rite)

        return Rite(rite)
