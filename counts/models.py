from typing import Tuple
from itertools import chain
from django.db import models


class Item(models.Model):
    item_code = models.CharField(max_length = 8)
    description = models.CharField(max_length = 50)
    rack = models.CharField(max_length=32)
    price = models.FloatField(default=1.00)
    recurrance = models.IntegerField(default=4)
    scale_rule = models.CharField(max_length=3, default='111')
    type = models.CharField(max_length=250, default='Undefined')
    food_group = models.CharField(max_length=150, default='Undefined')

    def __str__(self):
        return f"{self.item_code} - {self.description}"

    def as_dict(self):
        return {
            'item_code': self.item_code,
            'description': self.description,
            'rack': self.rack,
            'price': self.price,
            'type': self.type,
            'food_group': self.food_group
        }


class Menu(models.Model):
    description = models.CharField(max_length=50)
    products = models.ManyToManyField("Item", through='Share')

    def __str__(self):
        return self.description

    def as_dict(self):
        return {'description': self.description,
                'products': [share.as_tup() for share in self.share_set.all()]}

    def as_tup(self) -> Tuple[str, Tuple[str, int]]:
        return (self.description, [share.as_tup() for share in self.share_set.all()])


class Share(models.Model):
    menu: Menu = models.ForeignKey(Menu, on_delete = models.CASCADE)
    product: Item = models.ForeignKey(Item, on_delete = models.CASCADE)
    quantity = models.IntegerField(default=1, null=False)

    def __str__(self):
        return f'{self.quantity} {self.product.description}'

    def as_tup(self):
        return (self.product.item_code, self.quantity)


# These two functions are directly repeated here and in adapter.
def make_entry(command:str) -> tuple:
    return tuple(command.split())


def breakout_substitutions(commands:str) -> Tuple:
    return [make_entry(commands.split('\n'))]


class Substitution(models.Model):
    to_remove = models.ForeignKey(
        Item, 
        blank=False, 
        null=False, 
        related_name='substitution_remove_set', 
        on_delete=models.CASCADE
        )

    to_add = models.ForeignKey(
        Item, 
        blank=False, 
        null=False, 
        related_name='substitution_add_set', 
        on_delete=models.CASCADE
        )

    ratio = models.FloatField()

    def __str__(self):
        return f"Substituting {self.to_remove} with {self.to_add} with ratio {self.ratio}"

    def to_command(self):
        return ('exchange', self.to_remove.item_code, self.to_add.item_code, self.ratio)


class OutOfStock(models.Model):
    to_remove = models.ForeignKey(Item, blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"Currently out of {self.to_remove}"

    def to_command(self):
        return ('remove', self.to_remove.item_code)


class Addition(models.Model):
    to_add = models.ForeignKey(Item, blank=False, null=False, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False, null=False, default=1)

    def __str__(self):
        return f'Add {self.quantity} {self.to_add}'

    def to_command(self):
        print(('change', self.to_add.item_code, self.quantity))
        return ('change', self.to_add.item_code, self.quantity)


class Warehouse(models.Model):
    date = models.DateField(blank=True, editable=False)
    time_choices = [('am', 'AM'), ('pm', 'PM')]
    time_window = models.CharField(choices=time_choices, max_length=50)
    substitutions = models.ManyToManyField(Substitution, blank=True)
    out = models.ManyToManyField(OutOfStock, blank=True)
    additions = models.ManyToManyField(Addition, blank=True)

    def as_dict(self):
        return {'date': self.date,
                'time_window': self.time_window,
                'changes': [change.to_command() 
                            for change in chain(
                                self.substitutions.all(), 
                                self.out.all(), 
                                self.additions.all()
                                )],
                }
    
    def stockouts_list(self):
        return [
            {
                'date': self.date,
                'time_window': self.time_window,
                'item_code': stock_out.to_remove.item_code,
                'description': stock_out.to_remove.description,
            }
            for stock_out in self.out.all()
        ]

    def additions_list(self):
        return [
            {
                'date': self.date,
                'time_window': self.time_window,
                'item_code': addition.to_remove.item_code,
                'description': addition.to_remove.description,
            }
            for addition in self.additions.all()
        ]

    def substitutions_list(self):
        return [
            {
                'date': self.date,
                'time_window': self.time_window,
                'removed': substitution.to_remove.item_code,
                'removed_description': substitution.to_remove.description,
                'replaced': substitution.to_add.item_code,
                'replaced_description': substitution.to_add.description,
                'replacement_ratio': substitution.ratio
            }

            for substitution in self.substitutions.all()
        ]

    def __str__(self) -> str:
        return f'{self.date}, {self.time_window}'


class Invoice(models.Model):
    pulled_date = models.DateField(blank=True, editable=False, auto_now=True)
    start_date = models.DateField(blank=True, editable=False)
    end_date = models.DateField(blank=True, editable=False)
