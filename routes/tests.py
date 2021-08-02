from itertools import chain
from routes.functional import group_dictionaries
from django.test import TestCase
from .handlers import dump_menu, group_racks, fill_racks, string_box
from counts.models import Menu, Product, Share

class TestAttachMenu(TestCase):
    def setUp(self):
        menu = Menu.objects.create(description='Standard A Small')
        noodles = Product.objects.create(item_code='010101', description='Noodles', storage='Dry Rack 1')
        eggs = Product.objects.create(item_code='020202', description='Eggs', storage='Cooler Rack')
        tomato_sauce = Product.objects.create(item_code='0000000', description='Tomato Sauce', storage='Dry Rack 1')
        Share.objects.create(menu=menu, product=noodles, quantity=2)
        Share.objects.create(menu=menu, product=eggs, quantity=4)
        Share.objects.create(menu=menu, product=tomato_sauce, quantity=120)
        Product.objects.create(item_code='MG1018', description='Peanut Butter', storage='Dry Rack 2')
        Product.objects.create(item_code='MG1186', description='1/2 Gal', storage='Cooler Rack')
        Product.objects.create(item_code='MG1063', description='Whole Gal', storage='Cooler')
        Product.objects.create(item_code='MG1187', description='Almond', storage='Dry Rack 1')
        Product.objects.create(item_code='MG1006', description='Pinto Beans', storage='Dry Rack 1')
        Product.objects.create(item_code='MG1380', description='Chicken', storage='Frozen Rack')

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

    def test_additions(self):
        pass

    def test_substitutions(self):
        pass