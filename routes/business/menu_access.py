# Hold the box in a class which can be instantiated with
# the initial menu, but it will handle the additions and 
# exchanges gracefully.

from copy import deepcopy

from counts.models import Share, Menu, Product
from .functional import (DefaultArgDict, dict_filter, groupby, pipe)

from .menu_modifiers import build_exchangers, build_adders

from counts.models import Share, Menu, Product

def copy_cache(function):
    memo = {}
    def wrapper(*args):
        if args in memo:
            return deepcopy(memo[args])
        else:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper

def share_factory(item_code):
    """Creates a share dictionary for a given item_code."""
    return MenuMaker.dump_product(
        Share(product=Product.objects.get(item_code=item_code), 
              menu=Menu(description='dummy_menu'),
              quantity=0))

def bind_share_factory(menu):
    return DefaultArgDict(share_factory, menu)

def group_racks(menu: dict, display_order:list) -> list:
    """Takes a menu dictionary and returns a dictionary of rack keys to 
       product lists."""
    groups = groupby(menu.values(), 'storage')
    active_racks = list(filter(lambda x: x in groups, display_order))
    return [{'rack_name': rack, 'products': groups[rack]} for rack in active_racks]

def collect_products(stop: dict, dumper) -> dict:
    """Takes stop data and returns menu with appropriate adjustments."""

    exchangers = build_exchangers(stop)
    adders = build_adders(stop)

    return pipe(
        stop['box'],
        dumper,
        bind_share_factory, # adds a factory method if product in exchange stage isn't found.
        *exchangers, # applies all product exchanges
        *adders, # applies all product additions
        dict_filter('quantity', lambda x: x != 0),
    )

class MenuMaker:
    def __init__(self, menu_set):
        menu_queryset = Menu.objects.filter(
            description__in=menu_set).prefetch_related('share_set')
        self.menus = {menu.description: self.dump_menu(menu) 
                      for menu in menu_queryset}

    @staticmethod
    def dump_product(product):
        return {'item_code': product.product.item_code,
	        'description': product.product.description,
	        'storage': product.product.storage,
	        'quantity': product.quantity}

    @copy_cache
    def dump_menu(self, menu) -> dict:
        """Finds the menu_obj from database and dumps into a dict."""
        shares = menu.share_set.all()
        return {share.product.item_code: self.dump_product(share) for share in shares}

    def get_menu(self, menu_name):
        return self.menus[menu_name]