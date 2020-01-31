from django.db.models import FloatField, IntegerField
from django.db.models.functions import Cast
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import (AttributeCategory, AttributeType, AttributeValue,
                     Category, Product)
from .serializers import (
    AttributeCategorySerializer, AttributeTypeSerializer,
    AttributeValueSerializer, CategorySerializer, ProductSerializer)


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
        a_values = AttributeValue.objects.filter(product=instance)

        qs_a_categories = instance.category.a_categories.order_by('sorting_key')
        a_categories = AttributeCategorySerializer(qs_a_categories, many=True).data
        data['a_categories'] = a_categories

        for a_category in a_categories:
            qs_attributes = qs_a_categories.get(id=a_category['id']) \
                .attributes.order_by('sorting_key')
            attributes = AttributeTypeSerializer(qs_attributes, many=True).data
            a_category['attributes'] = attributes

            for attribute in attributes:
                if attribute['data_format'] != "":
                    attribute['value'] = attribute['data_format'] \
                        .format(a_values.get(a_type=attribute['id']).value)
                else:
                    attribute['value'] = a_values.get(a_type=attribute['id']).value
                attribute.pop("id", None)
                attribute.pop("name", None)
                attribute.pop("sorting_key", None)
                attribute.pop("type_name", None)
                attribute.pop("data_format", None)
                attribute.pop("a_category", None)

            a_category.pop("id", None)
            a_category.pop("name", None)
            a_category.pop("sorting_key", None)
            a_category.pop("category", None)
            
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
                    **{"category__%s" % op if op else "category": v})
            elif k == 'price':
                queryset = queryset.filter(
                    **{"price__%s" % op if op else "price": v})
            elif k == 'name':
                queryset = queryset.filter(
                    **{"name__%s" % op if op else "name": v})
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


class AttributeCategoryList(ListCreateAPIView):
    queryset = AttributeCategory.objects.all()
    serializer_class = AttributeCategorySerializer


class AttributeTypeList(ListCreateAPIView):
    queryset = AttributeType.objects.all()
    serializer_class = AttributeTypeSerializer


class AttributeValueList(ListCreateAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
