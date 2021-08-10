import csv
import io
import string
import re
import datetime

from counts.models import Share, Menu, Product
from .functional import DefaultArgDict, dict_filter, group_dictionaries, pipe, mapp, stapler 

FROZEN_ITEMS = [
    'MG1024',
    'MG1380', 
    'MG1241',
    'MG1048',
    'MG1385P',
]

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
    'Turkey': ('MG1024', 1),
    'ChickenBreast': ('MG1380', 1),
    'ChickenHalal': ('MG1241', 1),
    'ChickenQuarters': ('MG1048', 1),
    'HalalQuarters': ('MG1385P', 1),
    'Cheese': ('MG1056', 1),
    'Bananas': ('MG0030', 1),
}

def load_csv(file):
    data = file.read().decode('UTF-8')
    io_string = io.StringIO(data)
    return csv.DictReader(io_string)

def change_keys(dictionary:dict) -> dict:
    return{key.lower().replace('#', 'num').replace(' ', '_'): dictionary[key] 
           for key in dictionary.keys()}

def string_box(stop:dict) -> str:
    """
    A hack...
    """
    return  stop['box_type'] + ' ' + stop['box_menu'] + ' ' + stop['box_size']

def get_magic_words(notes: str) -> list:
    return re.findall(r'#Add([A-Za-z]+)', notes)

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

def build_adders(stop, additions_dict:dict):
    """
    Finds necessary additions from hash tags in notes,
    returns a list of add functions
    """
    additions = get_additions_from(stop['delivery_notes'])
    adders =  [build_addition_func(*additions_dict[product]) 
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

def build_exchangers(stop, exchanges_dict:dict) -> list:
    """
    Builds and applies the appropriate series of exchanges to the menu.
    """
    exchanges = get_exchanges(stop, exchanges_dict)
    return [make_exchange_func(*exchange) for exchange in exchanges]

def share_factory(item_code):
    """
    Creates a share dictionary for a given item_code.
    """
    return dump_product(
        Share(product=Product.objects.get(item_code=item_code), 
              menu=Menu(description='dummy_menu'),
              quantity=0))

def bind_share_factory(menu):
    return DefaultArgDict(share_factory, menu)

def dump_product(share):
    """
    Makes a simple dictionary out of a share object.
    """
    return {'item_code': share.product.item_code,
            'description': share.product.description,
            'storage': share.product.storage,
            'quantity': share.quantity}

def dump_menu(menu_name: str) -> dict:
    """
    Finds the menu_obj from database and dumps into a dict. 
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

def fill_racks(stop: dict) -> list:
    """
    Takes stop data and returns menu with appropriate adjustments.
    """
    exchangers = build_exchangers(stop, EXCHANGES_DICT)
    adders = build_adders(stop, ADDITIONS_DICT)

    return pipe(
        stop,
        string_box,
        dump_menu,
        bind_share_factory, # adds a factory method if product in exchange stage isn't found.
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
        stop['racks'] = fill_racks(stop)
    
    return stops

def route_num_to_letter(name):
    _, num = name.split()
    index = int(num) - 1
    return string.ascii_uppercase[index]

def build_fulfillment_context(order):
    # frozen_map = map_to_letter_name(order)
    """
    The main builder that delivers the data tree.
    """
    return pipe(order,
        mapp(change_keys), # Mapp is curried unlike map.
        lambda lst: list(filter(
            lambda stop: stop['route_num'] != 'DISMISSED REQUEST', lst)),
        mapp(stapler('route_num', 'route_num', route_num_to_letter)), 
        attach_menus_to_stops,
    #    mapp(frozen_letter_stapler(frozen_map)), 
        mapp(stapler('delivery_notes', 'adjustments', get_magic_words))
        )

def prepare_menu(order):
    pass

def extract_date_and_time(order):
    return order[0]['delivery_date'], order[0]['deliverytime']
    
def format_phone(phone_number):
    area_code, first, last = tuple(re.findall(r'\d{4}$|\d{3}', phone_number))
    return f'({area_code}) {first}-{last}'

def fix_phone(stop):
    phone_digits = re.findall('[0-9]{10}', stop['phone']) # attempts to find a coherent phone number.
    if phone_digits:
        stop['phone'] = format_phone(phone_digits[0])
    return stop

def dock_only(menu):
    return dict_filter(menu, lambda x: x['storage'] == 'Dock')

def menu_to_key(menu):
    return ((key, val['quantity']) for key, val in sorted(dock_only(menu)).items())

def count_menus(order):
    return group_dictionaries(order, 'menu', key_transform=menu_to_key, agg=len)

def map_to_letter_name(order):
    index = 0
    result = {}
    for stop in order:
        if not result.get(menu_to_key(stop['menu'])):
            result[menu_to_key(stop['menu'])] = string.ascii_uppercase[index]
            index += 1
        
    return result

def try_parsing_date(text):
    for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def frozen_letter_stapler(frozen_map):
    """Stapler idea could be abstracted."""
    return lambda stop: stop['froz_bin'] == frozen_map[menu_to_key(stop['menu'])]

def build_route_context(order):

    stops = pipe(order,
        mapp(change_keys),
        mapp(fix_phone),
        lambda lst: list(filter(
            lambda stop: stop['route_num'] != 'DISMISSED REQUEST', lst)),
        mapp(stapler('route_num', 'route_num', route_num_to_letter))) 

    route_groups = group_dictionaries(stops, 'route_num')
    
    date, time = extract_date_and_time(stops)

    return [{'name': name,
             'date': try_parsing_date(date).strftime('%b %d %Y'),
             'time': time,
             'stops':  stops} for name, stops in route_groups.items()]

def build_frozen_context(order):
    frozen_map = map_to_letter_name(order)