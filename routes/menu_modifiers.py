import re

ADDITIONS_DICT = {
    'Turkey': ('MG1024', 1),
    'ChickenBreast': ('MG1380', 1),
    'ChickenHalal': ('MG1241', 1),
    'ChickenQuarters': ('MG1048', 1),
    'HalalQuarters': ('MG1385P', 1),
    'Cheese': ('MG1056', 1),
    'Bananas': ('MG0030', 1),
}

EXCHANGES_DICT = {'peanutfree': [('MG1018', 'MG1006', 1)],
                 'dairyfree':  [('MG1186', 'MG1187', 1),
                                ('MG1063', 'MG1187', 2)]}


def get_magic_words(notes: str) -> list:
    return re.findall(r'#Add([A-Za-z]+)', notes)

def get_magic_words_from(stop):
    return get_magic_words(stop['delivery_notes'])

def get_additions_from(notes: str) -> list:
    """
    Returned hash-tagged phrases from delivery notes.
    """
    return [addition for addition in get_magic_words(notes) if addition in ADDITIONS_DICT]

def build_addition_func(to_add: str, quantity: int):
    """
    Returns a function that adds a given quantity to a given product.
    """
    def add_to(indexed_menu):
        indexed_menu[to_add]['quantity'] = indexed_menu[to_add]['quantity'] + quantity
        return indexed_menu
    return add_to

def build_adders(stop):
    """
    Finds necessary additions from hash tags in notes,
    returns a list of add functions
    """
    additions = get_additions_from(stop['delivery_notes'])
    adders =  [build_addition_func(*ADDITIONS_DICT[product]) 
              for product in additions]
    return adders

def get_exchanges(stop_data:dict, exchange_dict:dict) -> list:
    """
    Check the stop data for a yes value in the exchange column,
    and adds the tuple representing the exchange to a list of
    valid exchanges for that stop.
    """
    exchanges = []
    for exchange in exchange_dict.keys():
        if stop_data[exchange] == 'Yes':
            exchanges += exchange_dict[exchange]
    return exchanges

def make_exchange_func(to_remove: str, to_add: str, ratio: int):
    """
    Builds a function that exchanges two products at a specific ratio.
    """
    def exchange(indexed_menu):
        original_quantity = indexed_menu[to_remove]['quantity']
        indexed_menu[to_remove]['quantity'] = 0
        indexed_menu[to_add]['quantity'] = ( indexed_menu[to_add]['quantity'] 
                                   + original_quantity * ratio)
        return indexed_menu
    return exchange

def build_exchangers(stop) -> list:
    """
    Builds and applies the appropriate series of exchanges to the menu.
    """
    exchanges = get_exchanges(stop, EXCHANGES_DICT)
    return [make_exchange_func(*exchange) for exchange in exchanges]