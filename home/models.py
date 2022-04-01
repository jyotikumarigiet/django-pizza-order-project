from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models import Sum
import razorpay
# Create your models here.


class BaseModel(models.Model):
    uid = models.UUIDField(
        default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class PizzaCategory(BaseModel):
    category_name = models.CharField(max_length=100)


class Pizza(BaseModel):
    category = models.ForeignKey(
        PizzaCategory, on_delete=models.CASCADE, related_name="pizzas")
    pizza_name = models.CharField(max_length=100)
    price = models.IntegerField(default=100)
    image = models.ImageField(upload_to='pizza')


class Cart(BaseModel):
    user = models.ForeignKey(User, null=True, blank=True,on_delete=models.SET_NULL, related_name="carts")
    is_paid = models.BooleanField(default=False)
    instamojo_id = models.CharField(max_length=1000)
    # razorpay_id = models.CharField(max_length=1000)

    def get_cart_total(self ):
        sum = CartItems.objects.filter(cart=self).aggregate(Sum('pizza__price'))['pizza__price__sum']
        return sum

# sum = Sale.objects.filter(type='Flour').aggregate(Sum('column'))['column__sum']
class CartItems(BaseModel):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="cart_items")
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE)

