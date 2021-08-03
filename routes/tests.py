from itertools import chain
from .functional import group_dictionaries, lookup_record, mapp, DefaultArgDict
from django.test import TestCase
from .handlers import (dump_menu, get_additions_from, get_magic_words, group_racks, 
    fill_racks, string_box, change_keys)
from counts.models import Menu, Product, Share


class TestFunctional(TestCase):
    
    def test_group_dictionaries(self):
        dicts = [
            {'A': 254, 'B': 360, 'C': 5777},
            {'A': 254, 'B': 360, 'C': 5777},
            {'A': 254, 'B': 0, 'C': 0},
            {'A': 253, 'B': 361, 'C': 5777},
        ]

        grouped = group_dictionaries(dicts, 'A')

        self.assertEqual(len(grouped[254]), 3)
        self.assertEqual(grouped[254][0]['B'], grouped[254][1]['B'])
        self.assertNotEqual(grouped[254][0]['B'], grouped[253][0]['B'])

    def test_lookup_record(self):
        dicts = [
            {'A': 254, 'B': 360, 'C': 5777},
            {'A': 254, 'B': 360, 'C': 5777},
            {'A': 254, 'B': 0, 'C': 0},
            {'A': 253, 'B': 361, 'C': 5777},
        ]

        record = lookup_record(dicts, 'B', 361)

        self.assertDictEqual(record, dicts[-1])
    
    def test_mapp_no_args(self):
        func = lambda x: x + 2
        iterable = [1,2,3,4,5]

        result = mapp(func)(iterable)

        self.assertEqual(result, [3,4,5,6,7])

    def test_mapp_args(self):
        func = lambda x, y: x + y
        iterable = [1,2,3,4,5]

        result = mapp(func, 2)(iterable)

        self.assertEqual(result, [3,4,5,6,7])

    def test_default_arg_dict(self):
        dict_one = {'A':'a', 'B':'b', 'C':'c'}
        dict_two = {'A':'a'}

        def lookup(key):
            return dict_one[key]

        arg_dict = DefaultArgDict(lookup, dict_two)

        self.assertEqual(arg_dict['B'] == 'b')

class TestAttachMenu(TestCase):
    def setUp(self):
        menu = Menu.objects.create(description='Standard A Small')
        noodles = Product.objects.create(item_code='010101', description='Noodles', storage='Dry Rack 1')
        eggs = Product.objects.create(item_code='020202', description='Eggs', storage='Cooler Rack')
        tomato_sauce = Product.objects.create(item_code='0000000', description='Tomato Sauce', storage='Dry Rack 1')
        half_gal = Product.objects.create(item_code='MG1186', description='1/2 Gal', storage='Cooler Rack')
        Share.objects.create(menu=menu, product=noodles, quantity=2)
        Share.objects.create(menu=menu, product=eggs, quantity=4)
        Share.objects.create(menu=menu, product=tomato_sauce, quantity=120)
        Share.objects.create(menu=menu, product=half_gal, quantity=2)
        Product.objects.create(item_code='MG1018', description='Peanut Butter', storage='Dry Rack 2')
        Product.objects.create(item_code='MG1063', description='Whole Gal', storage='Cooler')
        Product.objects.create(item_code='MG1187', description='Almond', storage='Dry Rack 1')
        Product.objects.create(item_code='MG1006', description='Pinto Beans', storage='Dry Rack 1')
        Product.objects.create(item_code='MG1380', description='Chicken', storage='Dock')

    def test_string_box(self):
        obj = {'box_type': 'Standard', 'box_size': 'Large', 'box_menu': 'D'}

        string = string_box(obj)
        
        self.assertEqual(string, 'Standard D Large')

    def test_dump_menu(self):
        menu_str = 'Standard A Small'
        
        dump = dump_menu(menu_str)

        self.assertIn('Noodles', [item['description'] for item in dump.values()])

    def test_group_racks(self):
        DISPLAY_ORDER = ['Dry Rack 1', 'Cooler Rack']
        menu_str = 'Standard A Small'
        menu = dump_menu(menu_str) # don't couple this to dump_menu

        sorted_racks = group_racks(menu, DISPLAY_ORDER)

        self.assertListEqual([rack['rack_name'] for rack in sorted_racks], DISPLAY_ORDER)

        all_products = [product['description'] for product in chain.from_iterable([rack['products'] for rack in sorted_racks])]
        self.assertIn('Noodles', all_products)
        self.assertIn('Tomato Sauce', all_products)

    def test_fill_racks(self):
        test_stop = {'box_type':'Standard', 
                     'box_menu': 'A', 
                     'box_size': 'Small', 
                     'delivery_notes': '#AddChickenBreast', 
                     'peanutfree': 'Yes', 
                     'dairyfree': 'Yes'}
        
        racks = fill_racks(test_stop)
        all_products = chain.from_iterable([rack['products'] for rack in racks])

        self.assertIn('Noodles', [product['description'] for product in all_products])

    def test_get_magic_words(self):
        notes = "I love to get taco bell and sometimes #AddCrunchWrapSumpreme."

        words = get_magic_words(notes)

        self.assertIn('CrunchWrapSumpreme', words)

    def test_additions(self):
        test_stop = {'box_type':'Standard', 
                     'box_menu': 'A', 
                     'box_size': 'Small', 
                     'delivery_notes': '#AddChickenBreast', 
                     'peanutfree': 'No', 
                     'dairyfree': 'Yes'}

        racks = fill_racks(test_stop)

        all_products = list(chain.from_iterable([rack['products'] for rack in racks]))
        product = lookup_record(all_products, 'item_code', 'MG1380')
         
        self.assertEqual(product['quantity'], 1)
    
    def test_get_additions(self):
        delivery_notes = "front door. knock on the door #AddChickenBreast #AddCrunchwrapSupreme"

        additions = get_additions_from(delivery_notes)

        self.assertIn('ChickenBreast', additions)

    def test_substitutions(self):
        test_stop = {'box_type':'Standard', 
                     'box_menu': 'A', 
                     'box_size': 'Small', 
                     'delivery_notes': '', 
                     'peanutfree': 'No', 
                     'dairyfree': 'Yes'}

        racks = fill_racks(test_stop)

        all_products = list(chain.from_iterable([rack['products'] for rack in racks]))

        milk = lookup_record(all_products, 'item_code', 'MG1186')
        almond = lookup_record(all_products, 'item_code', 'MG1187')

        self.assertEqual(almond['quantity'], 2)

    def test_change_keys(self):
        test_obj = {'Item': 'gold', 'OBJECT': 'silver'}

        result = change_keys(test_obj)
        
        self.assertEqual(['item', 'object'], list(result.keys()))

    def test_mapp_keys(self):
        test_objs = [{'Rock Salt': 'gold', 'OBJECT': 'silver'},
                     {'Item': 'rock', 'OBJECT': 'diamond'}]

        result = mapp(change_keys)(test_objs)

        self.assertEqual(['rock_salt', 'object'], list(result[0].keys()))
        self.assertEqual(['item', 'object'], list(result[1].keys()))
