import functools
import json

tagselections = {'tags', 'implies', 'quaesitum'}

@functools.lru_cache(maxsize=32)
def load_data(p: str, src):
    data = json.loads(src.joinpath(p).read_text(encoding='utf-8'))

    # JSON doesn't support sets. Recursively find and replace anything that
    # looks like a list of tags with a set of tags.
    def recurse(obj, key=None):
        match obj:
            case dict():
                return {k: recurse(v, key=k) for k, v in obj.items()}
            case list():
                if all(type(x) is str for x in obj) and (key is None or key in tagselections):
                    return frozenset(obj)
                return [recurse(v) for v in obj]
            case _:
                return obj

    return recurse(data)
