from rest_framework.viewsets import ModelViewSet
from .models import *
from .serializers import *

class BusinessUserViewSet(ModelViewSet):
    queryset = BusinessUser.objects.all()
    serializer_class = BusinessUserSerializer

class OfferViewSet(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

