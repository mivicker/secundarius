import re

def create_order_dictionary(date, time, routes_df, menu_df, product_df):
    routes = routes_df.groupby('Route #')
    return {
        'date': date,
        'time': time,
        'routes': [create_route_dictionary(
        route_name, routes.get_group(route_name), menu_df, product_df) 
           for route_name in routes.groups]
           }

def create_route_dictionary(route_name, route_df, menu_df, product_df):
    return {
        'name': route_name,
        'stops': [create_stop_dictionary(stop_row[1], menu_df, product_df) 
            for stop_row in route_df.iterrows()]
    }

def create_stop_dictionary(stop_data, menu_df, product_df):
    exchanges = get_exchanges(stop_data, exchange_dict)
    additions = get_additions_from(stop_data)
    
    stop_data["Racks"] = get_racks(
        stop_data['Box'], menu_df, product_df, 
        exchanges=exchanges, additions=additions)
    return stop_data

def get_exchanges(stop_data, exchange_dict):
    #This checks the exchange columns on the sharepoint list.
    exchanges = []
    for exchange in exchange_dict.keys():
        if stop_data[exchange] == 'Yes':
            exchanges += exchange_dict[exchange]
    return exchanges

exchange_dict = {'PeanutFree': [('MG1018', 'MG1006', 1)],
                 'DairyFree':  [('MG1186', 'MG1187', 1),
                                ('MG1063', 'MG1187', 2)]}

def build_exchange_func(product_to_remove, product_to_add, ratio):
    def exchange(menu_series):
        original_quantity = menu_series[product_to_remove]
        menu_series[product_to_remove] = 0
        menu_series[product_to_add] = (menu_series[product_to_add] 
                             + original_quantity * ratio)
        return menu_series
    return exchange

def exchange_products(menu_series, exchanges):
    exchangers = [build_exchange_func(*exchange) for exchange in exchanges]
    for make_exchange in exchangers:
        menu_series = make_exchange(menu_series)
    return menu_series

additions_dict = {
    'AddTurkey': ('MG1024', 1),
    'AddChickenBreast': ('MG1380', 1),
    'AddChickenHalal': ('MG1241', 1),
    'AddChickenQuarters': ('MG1048', 1),
    'AddHalalQuarters': ('MG1385P', 1),
    'AddCheese': ('MG1056', 1),
    'AddBananas': ('MG0030', 1),
}

def get_additions_from(stop_data):
    matches = re.findall(r'#([A-Za-z]+)', stop_data['Delivery Notes'])
    return matches

def build_addition_func_for(product_to_add, quantity):
    def add_to(menu_series):
        menu_series[product_to_add] += quantity
        return menu_series
    return add_to

def add_products_to(menu_series, additions, additions_dict):
    item_adders = [build_addition_func_for(*additions_dict[product]) 
              for product in additions]
    for add_item_to in item_adders:
        menu_series = add_item_to(menu_series)
        
    return menu_series

def filt_menu_series(product_list):
    filt = product_list.astype(bool)
    return product_list[filt]

def get_menu_list(box, menu_df, product_df, exchanges=[], additions=[]):
    menu_series = menu_df[box].copy()
    if exchanges:
        menu_series = exchange_products(menu_series, exchanges)
    if additions:
        menu_series = add_products_to(menu_series, additions, additions_dict)
    item_list = filt_menu_series(menu_series)
    item_df = product_df.join(item_list, how='right')
    item_df.rename(columns={box:"Quantity"}, inplace=True)
    return item_df

def get_racks(box, menu_df, product_df, exchanges=[], additions=[]):
    menu_items = get_menu_list(
        box, menu_df, product_df, exchanges=exchanges, additions=additions)
    
    racks = menu_items.groupby('Storage')
    ordered_racks = sort_racks(racks.groups, display_order)
    return [create_rack_dictionary(group, racks.get_group(group)) 
            for group in ordered_racks]

def create_rack_dictionary(name, rack_df):
    return {
        'name': name,
        'items': rack_df.to_dict(orient='records')
    }

display_order = ['Dry Rack 1',
            'Dry Rack 2',
            'Cooler Rack',
            'Produce Rack',
            'Bakery Trays',
            'Dock']

def sort_racks(rack_groups, display_order):
    active_racks = [group for group in rack_groups]
    return [rack for rack in display_order if rack in active_racks]