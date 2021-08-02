import csv
import io
import string
import re
from counts.models import Share, Menu, Product
from .functional import dict_filter, group_dictionaries, pipe, mapp 

DISPLAY_ORDER = ['Dry Rack 1',
            'Dry Rack 2',
            'Cooler Rack',
            'Produce Rack',
            'Bakery Trays',
            'Dock']

EXCHANGES_DICT = {'peanutfree': [('MG1018', 'MG1006', 1)],
                 'dairyfree':  [('MG1186', 'MG1187', 1),
                                ('MG1063', 'MG1187', 2)]}

ADDITIONS_DICT = {
    'AddTurkey': ('MG1024', 1),
    'AddChickenBreast': ('MG1380', 1),
    'AddChickenHalal': ('MG1241', 1),
    'AddChickenQuarters': ('MG1048', 1),
    'AddHalalQuarters': ('MG1385P', 1),
    'AddCheese': ('MG1056', 1),
    'AddBananas': ('MG0030', 1),
}

def get_additions_from(notes: str) -> list:
    """
    Returned hash-tagged phrases from delivery notes.
    """
    return re.findall(r'#([A-Za-z]+)', notes)

def build_addition_func(to_add: str, quantity: int):
    """
    Returns a function that adds a given quantity to a given product.
    """
    def add_to(indexed_menu):

        if not indexed_menu.get(to_add):
            indexed_menu[to_add] = plug_share(to_add)

        # See note above
        
        indexed_menu[to_add]['quantity'] = indexed_menu[to_add]['quantity'] + quantity
        return indexed_menu
    return add_to

def build_adders(stop, additions_dict:dict):
    """
    Finds necessary additions from hash tags in notes,
    returns a list of add functions
    """
    additions = get_additions_from(stop['delivery_notes'])
    adders =  [build_addition_func(*additions_dict[product]) 
              for product in additions]
    return adders

def plug_share(item_code):
    """
    Creates a share dictionary for a given item_code.
    """
    return dump_product(Share(product=Product.objects.get(item_code=item_code), 
                 menu=Menu(description='dummy_menu'),
                 quantity=0))

def make_exchange_func(to_remove: str, to_add: str, ratio: int):
    """
    Builds a function that exchanges two products at a specific ratio.
    """
    def exchange(indexed_menu):
        
        if not indexed_menu.get(to_add):
            indexed_menu[to_add] = plug_share(to_add)
        if not indexed_menu.get(to_remove):
            indexed_menu[to_remove] = plug_share(to_remove)
        
        # This nested assignment is causing the above problems
        
        original_quantity = indexed_menu[to_remove]['quantity']
        indexed_menu[to_remove]['quantity'] = 0
        indexed_menu[to_add]['quantity'] = ( indexed_menu[to_add]['quantity'] 
                                   + original_quantity * ratio)
        return indexed_menu
    return exchange

def build_exchangers(stop, exchanges_dict:dict) -> list:
    """
    Builds and applies the appropriate series of exchanges to the menu.
    """
    exchanges = get_exchanges(stop, exchanges_dict)
    return [make_exchange_func(*exchange) for exchange in exchanges]

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

def change_keys(dictionary:dict) -> dict:
    return{key.lower().replace('#', 'num').replace(' ', '_'): dictionary[key] 
           for key in dictionary.keys()}

def load_csv(file):
    data = file.read().decode('UTF-8')
    io_string = io.StringIO(data)
    return csv.DictReader(io_string)

def dump_product(share):
    """
    Makes a dictionary out of a share object.
    """
    return {'item_code': share.product.item_code,
            'description': share.product.description,
            'storage': share.product.storage,
            'quantity': share.quantity}

def dump_menu(menu_name: str) -> dict:
    """
    Finds the menu_obj from database and dumps the key info into a dict. 
    """
    menu = Menu.objects.get(description=menu_name)
    shares = menu.share_set.prefetch_related()
    return {share.product.item_code: dump_product(share) for share in shares}

def group_racks(menu: dict, display_order:list) -> list:
    """
    Takes a menu dictionary and returns a dictionary of rack keys to 
    product lists.
    """
    groups = group_dictionaries(menu.values(), 'storage')
    active_racks = list(filter(lambda x: x in groups, display_order))
    return [{'rack_name': rack, 'products': groups[rack]} for rack in active_racks]

def string_box(stop:dict) -> str:
    """
    A hack...
    """
    return  stop['box_type'] + ' ' + stop['box_menu'] + ' ' + stop['box_size']

def fill_racks(stop: dict) -> list:
    """
    Takes stop data and returns menu.
    """
    exchangers = build_exchangers(stop, EXCHANGES_DICT)
    adders = build_adders(stop, ADDITIONS_DICT)

    return pipe(
        stop,
        string_box,
        dump_menu,
        *exchangers, # applies all product exchanges
        *adders, # applies all product additions
        dict_filter('quantity', lambda x: x != 0),
        lambda x: group_racks(x, DISPLAY_ORDER),
    )

def attach_menus_to_stops(stops:list) -> list:
    """
    Iterates over every stop and attaches the menu.
    """
    for stop in stops:
        if not stop:
            continue
        stop['racks'] = fill_racks(stop)
    
    return stops

def route_num_to_letter(name):
    _, num = name.split()
    index = int(num) - 1
    return string.ascii_uppercase[index]

def change_route_name(stop):
    stop['route_num'] = route_num_to_letter(stop['route_num'])
    return stop

def build_fulfillment_context(order):
    """
    The main builder that delivers the data tree.
    """
    return pipe(order,
        mapp(change_keys), # Mapp is curried unlike map.
        lambda lst: list(filter(
            lambda stop: stop['route_num'] != 'DISMISSED REQUEST', lst)),
        mapp(change_route_name), 
        attach_menus_to_stops)

