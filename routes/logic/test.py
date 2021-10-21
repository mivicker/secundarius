"""Creates boxes using the simplest framework."""

import string
import datetime
from tinydb import TinyDB

from tinydb.queries import Query
from box import (build_box_from_order, BoxOrder, Warehouse, Item)

import pprint as pp


if __name__ == '__main__':
    db = TinyDB('db.json', default=str)
    product_table = db.table('products')
    menus_table = db.table('menus')

    warehouse_table = db.table('warehouse')
    warehouse_table.truncate()

    product_cache = {product['item_code']: Item(**product) 
                     for product in product_table.all()}
    menu_cache = {menu['name']: menu['products'] 
                  for menu in menus_table.all()}

    order_date = datetime.datetime.strptime('2021-09-09', '%Y-%m-%d')
    order_window = 'AM'

    warehouse = Warehouse(date=order_date,
                          window=order_window,
                          items=product_cache, 
                          menus=menu_cache, 
                          substitutions=[('exchange', 'MG1186', 'MG1187', 3),
                                         ('change', 'MG0030', 3),
                                         ('exchange', "MG1212", 'MG0000', 12032)],
                          label_pool=list(string.ascii_uppercase),
                          bin_listen_to=('rack', 'Frozen'))
    
    Warehouses = Query()
    
    if not warehouse_table.search((Warehouses.date == str(order_date)) 
                                   & (Warehouses.order_window == order_window)):
        warehouse_table.insert(warehouse.asdict())
    else:
        # Issue warning about overwriting this pack time.
        warehouse_table.update(warehouse.asdict(), 
                              ((Warehouse.date == str(order_date))
                               & (Warehouse.window == order_window)))
    

    orders = [BoxOrder(menu_name="Standard A Small",
                       changes=[('change', 'MG0030', 10),
                                ('exchange', 'MG0037', 'MG1136', 3)]),
              BoxOrder(menu_name="Standard B Small"),
              BoxOrder(menu_name="Halal B Small"),
              BoxOrder(menu_name="Kidney Friendly A Small")]

    boxes = [build_box_from_order(order)(warehouse) for order in orders]

    pp.pprint(warehouse.bin_labels)
    pp.pprint(warehouse.bin_quantities)

    for box in boxes: print(box.bin_label)
    