from django.db import models

class Menu(models.Model):
    description = models.CharField(max_length=50)
    products = models.ManyToManyField("Product", through='Share')

    def __str__(self):
        return f"{str(self.box_type)} {self.get_menu_option_display()} {self.get_size_display()}"

class Product(models.Model):
    item_code = models.CharField(max_length = 8)
    description = models.CharField(max_length = 50)
    storage = models.CharField(max_length=32)
    def __str__(self):
        return f"{self.MNMG_ref} - {self.description}"

class Share(models.Model):
    menu = models.ForeignKey(Menu, on_delete = models.CASCADE)
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.IntegerField(default=1, null=False)