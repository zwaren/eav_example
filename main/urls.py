from django.urls import path

from .views import (AttributeTypeList, AttributeValueList, CategoryList,
                    ProductViewSet)

product_list = ProductViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
product_detail = ProductViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('category/', CategoryList.as_view()),
    path('product/', product_list),
    path('product/<int:pk>', product_detail),
    path('attribute/', AttributeTypeList.as_view()),
    path('value/', AttributeValueList.as_view()),
]
