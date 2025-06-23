from django.db import models
from product.models import Product
from django.contrib.auth.models import User
from profile1.models import Customer
from product.models import Product





class cart(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class Payment(models.Model):
        STRIPE_STATUS_CHOICES = [
            ('pending', 'Pending'),
            ('succeeded', 'Succeeded'),
            ('failed', 'Failed'),
        ]
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        amount = models.DecimalField(max_digits=10, decimal_places=2)
        stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
        stripe_product_id = models.CharField(max_length=255, blank=True, null=True)
        stripe_payment_status = models.CharField(max_length=50, choices=STRIPE_STATUS_CHOICES, null=True, blank=True)
        stripe_checkout_id = models.CharField(max_length=255, null=True, blank=True)
        paid = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"Payment {self.id} by {self.user.username}"
        
ORDER_STATUS_CHOICES = [
    ('Placed', 'Placed'),
    ('Packed', 'Packed'),
    ('Shipped', 'Shipped'),
    ('On the way', 'On the way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
]



class Order(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        product = models.ForeignKey(Product, on_delete=models.CASCADE)
        customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
        quantity = models.IntegerField(default=1)
        address = models.CharField(max_length=100, default='', blank=True)
        phone = models.CharField(max_length=20, default='', blank=True)
        date = models.DateTimeField(auto_now_add=True)
        order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='pending')
        cancellation_requested = models.BooleanField(default=False)
        payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True)
        total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

        def request_cancellation(self):
            self.cancellation_requested = True
            self.save()

        def __str__(self):
            return f"Order #{self.id} by {self.user.username}"
        
        
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')

