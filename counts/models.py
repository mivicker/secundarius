from typing import Tuple
from django.db import models


# These two functions are directly repeated here and in adapter.
def make_entry(command:str) -> tuple:
    return tuple(item for item in command.split())


def breakout_substitutions(commands:str) -> Tuple:
    return [make_entry(commands.split('\n'))]


class Warehouse(models.Model):
    date = models.DateField()
    time_window = models.CharField(max_length=50)
    substitutions = models.TextField()

    def as_dict(self):
        return {'date': self.date,
                'time_window': self.time_window,
                'substitutions': breakout_substitutions(self.substitutions)}


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


class Item(models.Model):
    item_code = models.CharField(max_length = 8)
    description = models.CharField(max_length = 50)
    rack = models.CharField(max_length=32)
    price = models.FloatField(default=1.00)
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


class Share(models.Model):
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE)
    product = models.ForeignKey(Item, on_delete = models.CASCADE)
    quantity = models.IntegerField(default=1, null=False)

    def __str__(self):
        return f'{str(self.quantity)} {self.product.description}'

    def as_tup(self):
        return (self.product.item_code, self.quantity)
