import datetime
from pathlib import Path
from django.test import TestCase
from tinydb import TinyDB
from .logic.box import (add_prototypes, build_box_from_order, 
                        Warehouse, Item, lookup_record, lookup_share, 
                        make_change, make_changes, modify)
from .logic.adapter import build_box_order, Translator, clean_stop


class Relationships(TestCase):
    def setUp(self):
        db = TinyDB(Path('routes', 'logic', 'db.json'))

        self.menu_cache = {menu['name']: menu['products'] 
                      for menu in db.table('menus').all()}
        self.item_cache = {prod['item_code']: Item(**prod)
                           for prod in db.table('products').all()}

    def test_add_prototypes(self):
        prototype = [('a', 1),
                     ('b', 1),
                     ('c', 1)]

        other = [('a', 5),
                 ('b', -2),
                 ('d', 2)]

        result = add_prototypes(prototype, other)

        self.assertEqual(lookup_record(result, 'b'), ('b', -1))

    def test_lookup_record(self):
        prototype = [('MG0001', 10),
                     ('MG0003', 5)]
        result = lookup_record(prototype, 'MG0003')

        self.assertEqual(result[0], 'MG0003')
        self.assertEqual(result[1], 5)

    def test_make_change(self):
        c_command = ('exchange', 'MG0001', 'MG0002', 2)

        prototype = [('MG0001', 10),
                     ('MG0003', 5)]

        result = make_change(c_command)(prototype)

        self.assertEqual(lookup_record(result, 'MG0002'), ('MG0002', 20))

    def test_make_changes(self):
        c_command = ('exchange', 'MG0001', 'MG0002', 2)

        prototype = [('MG0001', 10),
                     ('MG0003', 5)]

        result = make_changes([c_command])(prototype)

        self.assertEqual(lookup_record(result, 'MG0002'), ('MG0002', 20))

    def test_modify(self):
        c_command = ('exchange', 'MG0001', 'MG0002', 2)

        prototype = [('MG0001', 10),
                     ('MG0003', 5)]

        result = modify(prototype, [c_command])

        self.assertEqual(lookup_record(result, 'MG0002'), ('MG0002', 20))

    def test_build_box_order(self):
        stop = {
            "Box Type": "Standard",
            "Box Menu": "B",
            "Box Size": "Small",
            "PeanutFree": "No",
            "DairyFree": "Yes",
            "Delivery Notes": "",
            "Phone": "3132000000"
        }

        translator = Translator()

        warehouse =  Warehouse(
        date=datetime.datetime.today().date(),
        window='AM',
        substitutions=[('exchange', 'MG0024C', 'MG0040', 20)],
        menus=self.menu_cache,
        items=self.item_cache
        )

        box = build_box_from_order(build_box_order(clean_stop(stop), translator))(warehouse)

        self.assertEqual(lookup_share(box, 'MG1187').quantity, 1)
        self.assertEqual(lookup_share(box, 'MG0040').quantity, 20)
        self.assertEqual(lookup_share(box, 'MG0024C'), None)