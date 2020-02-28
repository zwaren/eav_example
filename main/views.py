from django.db.models import FloatField, IntegerField, Prefetch
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
        category = instance.category
        data = {
            'id': instance.id, 
            'name': instance.name, 
            'price': instance.price,
            'category': category.id,
            'a_categories': []
            }
        a_values = instance.attributes.values('a_type', 'value').all()

        qs_a_categories = category.a_categories.order_by('sorting_key') \
            .prefetch_related(Prefetch('attributes', queryset=AttributeType.objects.order_by('sorting_key')))

        for a_category_inst in qs_a_categories:
            qs_attributes = a_category_inst.attributes.all()
            a_category = {
                'displaying_name': a_category_inst.displaying_name, 
                'attributes': []
            }
            data['a_categories'].append(a_category)

            for attribute_inst in qs_attributes:
                a_value = a_values.get(a_type=attribute_inst.id)
                value = a_value['value']
                if attribute_inst.data_format != "":
                    value = attribute_inst.data_format.format(value)
                attribute = {
                    'displaying_name': attribute_inst.displaying_name, 
                    'value': value,
                }
                a_category['attributes'].append(attribute)
                
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
