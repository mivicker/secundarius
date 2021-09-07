from collections import UserDict, defaultdict

def pipe(first, *args):
    """
    Apply a list of functions to a value.
    """
    for fn in args:
        first = fn(first)
    return first

def groupby(dictionaries: list, group_key) -> dict:
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
    def filterer(record):
        return {key: val for key, val in record.items() if condition(val[test_key])}
    return filterer

class DefaultArgDict(UserDict):
    """
    Like a usual defaultdict, but it takes the key as a function argument.
    This is starting to feel like anti-patten.
    """
    def __init__(self, factory, initialdata):
        self.factory = factory
        self.data = initialdata

    def __missing__(self, key):
        result = self.factory(key)
        self[key] = result
        return result

def stapler(out_field, func):
    """ Returns a function that applies another function 
        to an object and saves it in a new field."""
    def staple(stop):
        stop[out_field] = func(stop)
        return stop
    return staple

def dict_sort_keys(dictionary:dict) -> dict:
    sorted_keys = sorted(dictionary)
    return {key: dictionary[key] for key in sorted_keys}

def dict_sort_values(dictionary: dict) -> dict:
    return dict(sorted(dictionary.items(), 
        key=lambda item: item[1], reverse=True))

def index(dictionaries:list, field) -> dict:
    if len(set(item[field] for item in dictionaries)) != len(dictionaries):
        raise ValueError("Field must be unique for each dictionary.")
    return {dictionary[field] for dictionary in dictionaries}

def ungroup(dictionary:dict) -> list:
    """wrapper for  dict.values, but is opposite of groupby"""
    return [value for group in dictionary.values() for value in group]