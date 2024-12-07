from django.db import models


class BusinessUser(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    uploaded_file = models.FileField(upload_to='business_user_files/', blank=True, null=True)
    referral_code = models.CharField(max_length=50, blank=True, null=True)  # Optional referral code
    cashback_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Cashback amount

    def __str__(self):
        return self.company_name

    def apply_referral_cashback(self, total_order_amount):
        """
        Apply a 5% cashback if the referral code is "leafcoin".
        """
        if self.referral_code == "leafcoin":
            cashback = total_order_amount * 0.05
            self.cashback_amount = ('cashback_amount') + cashback
            self.save()
            return cashback
        return 0


class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.FloatField()
    applicable_minimum_quantity = models.IntegerField()
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="categories/images/", blank=True, null=True)  # New image field

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_details = models.TextField()
    image = models.ImageField(upload_to="products/images/")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_quantity = models.IntegerField()
    stock_quantity = models.IntegerField(default=0)  # New field for available stock
    is_in_stock = models.BooleanField(default=True)  # New field for stock status

    def save(self, *args, **kwargs):
        # Automatically set `is_in_stock` based on `stock_quantity`
        self.is_in_stock = self.stock_quantity > 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    ORDER_TYPE_CHOICES = [
        ('Online', 'Online'),
        ('Offline', 'Offline'),
    ]
    business_user = models.ForeignKey(BusinessUser, related_name="orders", on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    payment_terms = models.CharField(max_length=50)
    order_type = models.CharField(max_length=50, choices=ORDER_TYPE_CHOICES)
    cashback_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Track cashback applied

    def save(self, *args, **kwargs):
        # Apply referral cashback for orders
        if not self.pk:  # Only apply on creation, not updates
            cashback = self.business_user.apply_referral_cashback(self.total_price)
            self.cashback_applied = cashback
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.business_user.company_name}"



class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name="order_products", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Ensure enough stock is available
        if self.product.stock_quantity < self.quantity:
            raise ValueError(f"Not enough stock available for {self.product.product_name}.")

        # Deduct stock on save
        self.product.stock_quantity -= self.quantity
        self.product.save()

        # Calculate the total
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} for Order {self.order.id}"

