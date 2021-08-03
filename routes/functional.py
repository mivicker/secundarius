
from collections import UserDict, defaultdict

def safe_dictionary_lookup(questionable:dict):
    pass

def pipe(first, *args):
    """
    Apply a list of functions to a value.
    """
    for fn in args:
        first = fn(first)
    return first

def group_dictionaries(dictionaries: list, group_key: str) -> dict:
    """
    Group a list of dictionaries by the values of a given key.
    """
    result = defaultdict(lambda: [])
    for dictionary in dictionaries:
        result[dictionary[group_key]].append(dictionary.copy())
        
    return dict(result)

def lookup_record(records:list, key, value) -> dict:
    """Returns first dictionary in a list where the key equals value"""
    for record in records:
        if record[key] == value:
            return record

def mapp(func, *args):
    def apply_over(iterable):
        return [func(item, *args) for item in iterable]
    return apply_over

def dict_map(func, *args):
    def apply_over(dictionary):
        return {key: func(val, *args) for key, val in dictionary.items()}
    return apply_over

def dict_filter(test_key, condition):
    """This abstraction is off."""
    def filterer(record):
        return {key: val for key, val in record.items() if condition(val[test_key])}
    return filterer

class DefaultArgDict(UserDict):
    def __init__(self, factory, initialdata):
        self.factory = factory
        self.data = initialdata

    def __missing__(self, key):
        return self.factory(key)