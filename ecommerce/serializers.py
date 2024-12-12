# from rest_framework import serializers
# from .models import BusinessUser, Offer, Category, Product, Order, OrderProduct


# class BusinessUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BusinessUser
#         fields = [
#             'id',
#             'company_name',
#             'contact_person',
#             'phone',
#             'uploaded_file',
#             'referral_code',
#             'cashback_amount',
#         ]

# class OfferSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Offer
#         fields = '__all__'


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = '__all__'


# class ProductSerializer(serializers.ModelSerializer):
#     category_name = serializers.ReadOnlyField(source='category.name')

#     class Meta:
#         model = Product
#         fields = '__all__'


# class OrderProductNestedSerializer(serializers.ModelSerializer):
#     product_name = serializers.ReadOnlyField(source='product.product_name')

#     class Meta:
#         model = OrderProduct
#         fields = ['id', 'product', 'product_name', 'quantity', 'price']


# class OrderSerializer(serializers.ModelSerializer):
#     business_user_name = serializers.ReadOnlyField(source='business_user.company_name')
#     order_products = OrderProductNestedSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'business_user', 'business_user_name', 'order_date', 'total_price',
#              'billing_address', 'status','order_type', 'order_products'
#         ]

#     def create(self, validated_data):
#         order_products_data = validated_data.pop('order_products', [])
#         business_user = validated_data['business_user']
#         total_price = validated_data['total_price']

#         # Create the Order instance
#         order = Order.objects.create(**validated_data)

#         # Add associated OrderProducts
#         for product_data in order_products_data:
#             product = product_data.get('product')
#             quantity = product_data.get('quantity')
#             price = product_data.get('price')
#             total = price * quantity

#             OrderProduct.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=quantity,
#                 price=price,
#                 total=total
#             )

#         # Apply cashback if the referral code is "leafcoin"
#         cashback = 0
#         if business_user.referral_code == "leafcoin":
#             cashback = total_price * 0.05
#             business_user.cashback_amount += cashback
#             business_user.save()

#         # Track the cashback applied in the order (optional, for auditing)
#         order.cashback_applied = cashback
#         order.save()

#         return order

#     def update(self, instance, validated_data):
#         order_products_data = validated_data.pop('order_products', [])
#         instance.total_price = validated_data.get('total_price', instance.total_price)
#         instance.billing_address = validated_data.get('billing_address', instance.billing_address)
#         instance.status = validated_data.get('status', instance.status)
#         instance.order_type = validated_data.get('order_type', instance.order_type)
#         instance.save()

#         # Update or create OrderProduct entries
#         for product_data in order_products_data:
#             order_product_id = product_data.get('id', None)
#             if order_product_id:
#                 order_product = OrderProduct.objects.get(id=order_product_id, order=instance)
#                 order_product.quantity = product_data.get('quantity', order_product.quantity)
#                 order_product.price = product_data.get('price', order_product.price)
#                 order_product.total = order_product.price * order_product.quantity
#                 order_product.save()
#             else:
#                 product = product_data.get('product')
#                 quantity = product_data.get('quantity')
#                 price = product_data.get('price')
#                 total = price * quantity

#                 OrderProduct.objects.create(
#                     order=instance,
#                     product=product,
#                     quantity=quantity,
#                     price=price,
#                     total=total
#                 )

#         return instance

# class PhoneNumberSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=15)





from rest_framework import serializers
from .models import BusinessUser, Offer, Category, Product, Order, OrderProduct


class BusinessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUser
        fields = [
            'id',
            'company_name',
            'contact_person',
            'phone',
            'uploaded_file',
            'referral_code',
            'cashback_amount',
        ]


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Product
        fields = '__all__'


class OrderProductNestedSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.product_name')

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    business_user_name = serializers.ReadOnlyField(source='business_user.company_name')
    order_products = OrderProductNestedSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'business_user', 'business_user_name', 'order_date', 'total_price',
            'billing_address', 'status', 'order_type', 'order_products'
        ]

    def validate(self, data):
        """
        Ensure total_price matches the calculated total of order_products.
        """
        order_products = data.get('order_products', [])
        calculated_total = sum(
            [item['price'] * item['quantity'] for item in order_products if 'price' in item and 'quantity' in item]
        )
        if 'total_price' in data and data['total_price'] != calculated_total:
            raise serializers.ValidationError("Total price does not match the sum of the order products' totals.")
        return data

    def create(self, validated_data):
        order_products_data = validated_data.pop('order_products', [])
        business_user = validated_data['business_user']

        # Create the Order instance
        order = Order.objects.create(**validated_data)

        # Add associated OrderProducts
        for product_data in order_products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            price = product_data['price']
            total = price * quantity

            # Validate stock before creating OrderProduct
            if product.stock_quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock for product {product.product_name}. Requested: {quantity}, Available: {product.stock_quantity}."
                )

            OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
                total=total
            )

        # Apply cashback if the referral code is "leafcoin"
        cashback = 0
        if business_user.referral_code == "leafcoin":
            cashback = validated_data['total_price'] * 0.05
            business_user.cashback_amount += cashback
            business_user.save()

        # Track the cashback applied in the order
        order.cashback_applied = cashback
        order.save()

        return order

    def update(self, instance, validated_data):
        order_products_data = validated_data.pop('order_products', [])
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.billing_address = validated_data.get('billing_address', instance.billing_address)
        instance.status = validated_data.get('status', instance.status)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.save()

        # Update or create OrderProduct entries
        for product_data in order_products_data:
            order_product_id = product_data.get('id', None)
            if order_product_id:
                try:
                    order_product = OrderProduct.objects.get(id=order_product_id, order=instance)
                    order_product.quantity = product_data.get('quantity', order_product.quantity)
                    order_product.price = product_data.get('price', order_product.price)
                    order_product.total = order_product.price * order_product.quantity

                    # Validate stock adjustments
                    stock_change = product_data['quantity'] - order_product.quantity
                    if order_product.product.stock_quantity < stock_change:
                        raise serializers.ValidationError(
                            f"Insufficient stock for product {order_product.product.product_name}."
                        )
                    order_product.save()
                except OrderProduct.DoesNotExist:
                    raise serializers.ValidationError(f"OrderProduct with ID {order_product_id} does not exist.")
            else:
                product = product_data['product']
                quantity = product_data['quantity']
                price = product_data['price']
                total = price * quantity

                # Validate stock before creating new OrderProduct
                if product.stock_quantity < quantity:
                    raise serializers.ValidationError(
                        f"Insufficient stock for product {product.product_name}. Requested: {quantity}, Available: {product.stock_quantity}."
                    )

                OrderProduct.objects.create(
                    order=instance,
                    product=product,
                    quantity=quantity,
                    price=price,
                    total=total
                )

        return instance


class PhoneNumberSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

    def validate_phone(self, value):
        """
        Validate phone number format to ensure it adheres to international format.
        """
        import re
        phone_regex = re.compile(r'^\+?1?\d{9,15}$')
        if not phone_regex.match(value):
            raise serializers.ValidationError("Phone number must be in the format: '+999999999'. Up to 15 digits allowed.")
        return value
