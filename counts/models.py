from django.db import models

class Menu(models.Model):
    description = models.CharField(max_length=50)
    products = models.ManyToManyField("Product", through='Share')

    def __str__(self):
        return self.description

class Product(models.Model):
    item_code = models.CharField(max_length = 8)
    description = models.CharField(max_length = 50)
    storage = models.CharField(max_length=32)
    def __str__(self):
        return f"{self.item_code} - {self.description}"

class Share(models.Model):
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default=1, null=False)

    def __str__(self):
        return f'{str(self.quantity)} {self.product.description}'