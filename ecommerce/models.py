from django.db import models

class BusinessUser(models.Model):
    company_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    uploaded_file = models.FileField(upload_to='business_user_files/', blank=True, null=True)

    def __str__(self):
        return self.company_name

class Offer(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.FloatField()
    applicable_minimum_quantity = models.IntegerField()
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)  # Add image field

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=255)

class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    product_details = models.TextField()
    image = models.ImageField(upload_to="products/images/")  # Upload folder for product images
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_quantity = models.IntegerField()

    def __str__(self):
        return self.product_name

class Order(models.Model):
    business_user = models.ForeignKey(BusinessUser, related_name="orders", on_delete=models.CASCADE)
    order_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    status = models.CharField(max_length=50)
    payment_terms = models.CharField(max_length=50)
    order_type = models.CharField(max_length=50)

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, related_name="products", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

