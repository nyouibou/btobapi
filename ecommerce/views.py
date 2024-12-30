from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import BusinessUser, Offer, Category, Product, Order, OrderProduct
from .serializers import (
    BusinessUserSerializer, OfferSerializer, CategorySerializer,
    ProductSerializer, OrderSerializer, OrderProductNestedSerializer,PhoneNumberSerializer
)

class BusinessUserDetailView(APIView):
    """
    Retrieve, update, or delete a BusinessUser by their phone number.
    """
    
    def get(self, request, phone):
        # Retrieve BusinessUser by phone
        business_user = BusinessUser.get_user_by_phone(phone)
        if business_user:
            serializer = BusinessUserSerializer(business_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "BusinessUser not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, phone):
        # Delete BusinessUser by phone number
        try:
            business_user = BusinessUser.get_user_by_phone(phone)
            if business_user:
                business_user.delete()
                return Response({"message": "BusinessUser deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "BusinessUser not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        

    
class BusinessUserViewSet(viewsets.ModelViewSet):
    queryset = BusinessUser.objects.all()
    serializer_class = BusinessUserSerializer


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderProductViewSet(viewsets.ModelViewSet):
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductNestedSerializer

    
class GetUserByPhoneView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PhoneNumberSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data.get('phone')
            user = BusinessUser.get_user_by_phone(phone)
            if user:
                # Respond with user details
                user_data = {
                    "company_name": user.company_name,
                    "contact_person": user.contact_person,
                    "phone": user.phone,
                    "referral_code": user.referral_code,
                    "cashback_amount": user.cashback_amount,
                }
                return Response(user_data, status=status.HTTP_200_OK)
            else:
                # User not found
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FetchOrdersByCustomerNameView(APIView):
    def get(self, request, company_name):
        orders = Order.get_orders_by_company_name(company_name)
        if not orders.exists():
            return Response({"detail": "No orders found for this company name."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
