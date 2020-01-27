from django.db.models import FloatField, IntegerField
from django.db.models.functions import Cast
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import AttributeType, AttributeValue, Category, Product
from .serializers import (AttributeTypeSerializer, AttributeValueSerializer,
                          CategorySerializer, ProductSerializer)


class CategoryList(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        extra = AttributeValue.objects.filter(product=instance)
        for att in AttributeType.objects.filter(category=instance.category):
            value = None
            if att.type_name == "Int":
                value = extra.annotate(value_as_int=Cast('value', IntegerField())) \
                    .get(a_type=att).value_as_int
            elif att.type_name == "Float":
                value = extra.annotate(value_as_float=Cast('value', FloatField())) \
                    .get(a_type=att).value_as_float
            else:
                value = extra.get(a_type=att).value
            data[att.name] = value
            
        return Response(data)

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        attributes = AttributeType.objects.all()

        for k_op, v in query_params.items():
            k, op = None, None
            if k_op.find("__") > -1:
                k, op = k_op.split("__")
            else:
                k = k_op

            if k == 'category':
                queryset = queryset.filter(
                    **{"category_name__%s" % op if op else "category_name": v})
                
            elif k == 'price':
                queryset = queryset.filter(
                    **{"price__%s" % op if op else "price": v})
            else:
                a = attributes.get(name=k)
                a_values = a.a_values.filter(product__in=queryset)
                if a.type_name == "Int":
                    v = int(v)
                    a_values = a_values.annotate(value_as_int=Cast('value', IntegerField())) \
                        .filter(**{"value_as_int__%s" % op if op else "value_as_int": v})
                elif a.type_name == "Float":
                    v = float(v)
                    a_values = a_values.annotate(value_as_float=Cast('value', FloatField())) \
                        .filter(**{"value_as_float__%s" % op if op else "value_as_float": v})
                else:
                    a_values = a_values.filter(**{"value__%s" % op: v})
                    
                queryset = queryset.filter(pk__in=a_values.values_list('product', flat=True))
                
        return queryset


class AttributeTypeList(ListCreateAPIView):
    queryset = AttributeType.objects.all()
    serializer_class = AttributeTypeSerializer


class AttributeValueList(ListCreateAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
