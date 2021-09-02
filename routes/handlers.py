
import csv
import io
import string

from counts.models import Share, Menu, Product
from .functional import (DefaultArgDict, dict_filter, 
    groupby, pipe, mapp, stapler, dict_sort_keys, dict_sort_values)

from .menu_modifiers import get_magic_words_from, build_exchangers, build_adders
from .clean_up import extract_date_and_time, try_parsing_date

NAMING_SCHEMES = {
        'AM': [letter + " Blue" for letter in string.ascii_uppercase],
        'PM': [letter + " Green" for letter in string.ascii_uppercase],
        '10-2': ['Kansas', 'Iowa', 'Nevada', 'Oregon', 'Wisconsin', 'New York', 'South Carolina', 'Colorado']

    }

FROZEN_ITEMS = [
    'MG1024',
    'MG1380', 
    'MG1241',
    'MG1048',
    'MG1385P',
    'MG1178',
    'MG1181',
    'MG1286'
]

DISPLAY_ORDER = ['Dry Rack 1',
            'Dry Rack 2',
            'Cooler Rack',
            'Produce Rack',
            'Bakery Trays',
            'Dock']

def load_csv(file):
    data = file.read().decode('UTF-8')
    io_string = io.StringIO(data)
    return csv.DictReader(io_string)

def share_factory(item_code):
    """Creates a share dictionary for a given item_code."""
    return dump_product(
        Share(product=Product.objects.get(item_code=item_code), 
              menu=Menu(description='dummy_menu'),
              quantity=0))

def bind_share_factory(menu):
    return DefaultArgDict(share_factory, menu)

def dump_product(share):
    """Makes a simple dictionary out of a share object."""
    return {'item_code': share.product.item_code,
            'description': share.product.description,
            'storage': share.product.storage,
            'quantity': share.quantity}

def dump_menu(menu_name: str) -> dict:
    """Finds the menu_obj from database and dumps into a dict."""
    menu = Menu.objects.get(description=menu_name)
    shares = menu.share_set.prefetch_related()
    return {share.product.item_code: dump_product(share) for share in shares}

def group_racks(menu: dict, display_order:list) -> list:
    """Takes a menu dictionary and returns a dictionary of rack keys to 
       product lists."""
    groups = groupby(menu.values(), 'storage')
    active_racks = list(filter(lambda x: x in groups, display_order))
    return [{'rack_name': rack, 'products': groups[rack]} for rack in active_racks]

def collect_products(stop: dict) -> dict:
    """Takes stop data and returns menu with appropriate adjustments."""
    exchangers = build_exchangers(stop)
    adders = build_adders(stop)

    return pipe(
        stop['box'],
        dump_menu,
        bind_share_factory, # adds a factory method if product in exchange stage isn't found.
        *exchangers, # applies all product exchanges
        *adders, # applies all product additions
        dict_filter('quantity', lambda x: x != 0),
    )

def attach_menus_to_stops(stops:list) -> list:
    """Iterates over every stop and attaches the menu."""
    for stop in stops:
        stop['menu'] = collect_products(stop)

    time = stops[0]['deliverytime']

    menu_to_bin, _, _ = create_frozen_maps(stops, NAMING_SCHEMES[time])

    for stop in stops:
        stop['racks'] = group_racks(stop['menu'], DISPLAY_ORDER)
        stop['froz_bin'] = menu_to_bin[keyify(stop['menu'])]
    
    return stops

def build_fulfillment_context(order):
    """Main func delivering full route object."""
    return pipe(order,
        attach_menus_to_stops,
        mapp(stapler('adjustments', get_magic_words_from)), # This is terrible.
        )

def build_route_context(order):
    """
    This builds the data object for the route lists and in the future
    the driver application.
    """
    route_groups = groupby(order, 'route_num')
    
    date, time = extract_date_and_time(order)

    return [{'name': name,
             'date': try_parsing_date(date).strftime('%b %d %Y'),
             'time': time,
             'stops':  stops} for name, stops in route_groups.items()]

def select_frozen(menu: dict) -> dict:
    return {key: val for key, val in menu.items() if val['item_code'] in FROZEN_ITEMS}

def keyify(menu: dict) -> tuple:
    return tuple((key, val['quantity']) for key, val in dict_sort_keys(select_frozen(menu)).items())

def create_frozen_maps(order: list, symbols: str)-> dict:
    """
    Creates a map from an order that takes a menu and returns a bin. 
    """
    index = 0
    menu_to_bin = {}
    bin_to_counts = {}
    bin_to_menu = {}
    for stop in order:
        if not menu_to_bin.get(keyify(stop['menu'])):
            new_label = symbols[index]
            menu_to_bin[keyify(stop['menu'])] = new_label
            bin_to_counts[new_label] = 1
            bin_to_menu[new_label] = select_frozen(stop['menu'])
            index += 1
        else:
            label = menu_to_bin[keyify(stop['menu'])]
            bin_to_counts[label] += 1

    return menu_to_bin, bin_to_counts, bin_to_menu

def build_frozen_context(order):
    for stop in order:
        stop['menu'] = collect_products(stop)

    time = order[0]['deliverytime']

    _, bin_to_counts, bin_to_menu = create_frozen_maps(order, NAMING_SCHEMES[time])

    sorted_bins = dict_sort_values(bin_to_counts)

    date, time = extract_date_and_time(order)

    return {'bins': [{'label': key,
             'count': bin_to_counts[key],
             'menu': bin_to_menu[key]} for key in sorted_bins.keys()],
             'date': date,
             'time': time}