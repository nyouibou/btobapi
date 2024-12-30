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
    """
    ViewSet for CRUD operations on Orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new Order and associated OrderProducts.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order = serializer.save()
                return Response(
                    {"message": "Order created successfully.", "order": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update an existing Order and its associated OrderProducts.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            try:
                order = serializer.save()
                return Response(
                    {"message": "Order updated successfully.", "order": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an Order and ensure related OrderProducts are removed.
        """
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Order deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )



class OrderProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on OrderProducts.
    """
    queryset = OrderProduct.objects.all()
    serializer_class = OrderProductNestedSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new OrderProduct.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order_product = serializer.save()
                return Response(
                    {"message": "OrderProduct created successfully.", "order_product": serializer.data},
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Update an existing OrderProduct.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            try:
                order_product = serializer.save()
                return Response(
                    {"message": "OrderProduct updated successfully.", "order_product": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an OrderProduct.
        """
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "OrderProduct deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    
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
