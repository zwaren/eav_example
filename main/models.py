from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()

class AttributeType(models.Model):
    name = models.CharField(max_length=200)
    type_name = models.CharField(max_length=200) # Int | Float | Char

class Attribute(models.Model):
    product = models.ForeignKey(Category, on_delete=models.CASCADE)
    a_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class AttributeInt(Attribute):
    value = models.IntegerField()

class AttributeFloat(Attribute):
    value = models.FloatField()

class AttributeChar(Attribute):
    value = models.CharField(max_length=200)