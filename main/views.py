from rest_framework.generics import ListCreateAPIView
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
            value = extra.get(a_type=att).value
            if att.type_name == "Int":
                value = int(value)
            elif att.type_name == "Float":
                value = float(value)
            data[att.name] = value
            
        return Response(data)

    def get_queryset(self):
        queryset = super().get_queryset()
        query_params = self.request.query_params
        attributes = AttributeType.objects.all()

        category = query_params.pop('category', None)
        if category:
            queryset = queryset.filter(category_name=category)

        for k, v in query_params.items():
            op = None
            if k.find("__") > -1:
                k, op = k.split("__")
            a = attributes.get(name=k, None)
            if a:
                if a.type_name == "Int":
                    value = int(value)
                elif att.type_name == "Float":
                    value = float(value)
                queryset = queryset.filter(category_name=category)
                
        return queryset


class AttributeTypeList(ListCreateAPIView):
    queryset = AttributeType.objects.all()
    serializer_class = AttributeTypeSerializer


class AttributeValueList(ListCreateAPIView):
    queryset = AttributeValue.objects.all()
    serializer_class = AttributeValueSerializer
