from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()

class AttributeType(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type_name = models.CharField(max_length=200) # Int | Float | Char

class AttributeValue(models.Model):
    product = models.ForeignKey(Product, related_name='attributes', on_delete=models.CASCADE)
    a_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
