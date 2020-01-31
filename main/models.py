from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    def __str__(self):
        return self.name

class AttributeCategory(models.Model):
    name = models.CharField(max_length=200)
    displaying_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name='a_categories', on_delete=models.CASCADE)
    sorting_key = models.IntegerField()
    def __str__(self):
        return self.name

class AttributeType(models.Model):
    name = models.CharField(max_length=200)
    displaying_name = models.CharField(max_length=200)
    a_category = models.ForeignKey(AttributeCategory, related_name='attributes', on_delete=models.CASCADE)
    sorting_key = models.IntegerField()
    type_name = models.CharField(max_length=200) # Int | Float | Char
    data_format = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    product = models.ForeignKey(Product, related_name='attributes', on_delete=models.CASCADE)
    a_type = models.ForeignKey(AttributeType, related_name='a_values', on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
