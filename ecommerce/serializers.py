from rest_framework import serializers
from .models import BusinessUser, Offer, Category, Product, Order, OrderProduct


class BusinessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessUser
        fields = '__all__'


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
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'wholesale_price', 'total']


class OrderSerializer(serializers.ModelSerializer):
    business_user_name = serializers.ReadOnlyField(source='business_user.company_name')
    order_products = OrderProductNestedSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'business_user', 'business_user_name', 'order_date', 'total_price',
            'shipping_address', 'billing_address', 'status', 'payment_terms',
            'order_type', 'order_products'
        ]

    def create(self, validated_data):
        order_products_data = validated_data.pop('order_products', [])
        business_user = validated_data['business_user']
        total_price = validated_data['total_price']

        # Create the Order instance
        order = Order.objects.create(**validated_data)

        # Add associated OrderProducts
        for product_data in order_products_data:
            product = product_data.get('product')
            quantity = product_data.get('quantity')
            price = product_data.get('price')
            wholesale_price = product_data.get('wholesale_price')
            total = price * quantity

            OrderProduct.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price,
                wholesale_price=wholesale_price,
                total=total
            )

        # Apply cashback if the referral code is "leafcoin"
        cashback = 0
        if business_user.referral_code == "leafcoin":
            cashback = total_price * 0.05
            business_user.cashback_amount += cashback
            business_user.save()

        # Track the cashback applied in the order (optional, for auditing)
        order.cashback_applied = cashback
        order.save()

        return order

    def update(self, instance, validated_data):
        order_products_data = validated_data.pop('order_products', [])
        instance.total_price = validated_data.get('total_price', instance.total_price)
        instance.shipping_address = validated_data.get('shipping_address', instance.shipping_address)
        instance.billing_address = validated_data.get('billing_address', instance.billing_address)
        instance.status = validated_data.get('status', instance.status)
        instance.payment_terms = validated_data.get('payment_terms', instance.payment_terms)
        instance.order_type = validated_data.get('order_type', instance.order_type)
        instance.save()

        # Update or create OrderProduct entries
        for product_data in order_products_data:
            order_product_id = product_data.get('id', None)
            if order_product_id:
                order_product = OrderProduct.objects.get(id=order_product_id, order=instance)
                order_product.quantity = product_data.get('quantity', order_product.quantity)
                order_product.price = product_data.get('price', order_product.price)
                order_product.wholesale_price = product_data.get('wholesale_price', order_product.wholesale_price)
                order_product.total = order_product.price * order_product.quantity
                order_product.save()
            else:
                product = product_data.get('product')
                quantity = product_data.get('quantity')
                price = product_data.get('price')
                wholesale_price = product_data.get('wholesale_price')
                total = price * quantity

                OrderProduct.objects.create(
                    order=instance,
                    product=product,
                    quantity=quantity,
                    price=price,
                    wholesale_price=wholesale_price,
                    total=total
                )

        return instance
