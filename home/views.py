from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from home.models import *
from instamojo_wrapper import Instamojo
from django.conf import settings

# Create your views here.

# create payment 
# import razorpay
# from pizza.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY

# client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET_KEY))

# @login_required(login_url='/login/')
# def cart(request):
#     if request.method == 'POST':
#         try:
#             cart = Cart.objects.get(user = request.user)
#             cart_items = CartItems.objects.filter(cart=cart)
#             final_price = 0
#             if(len(cart_items)>0):
#                 order = orders.objects.create(user=request.user, total_amount=0)
#                 order.save()
#                 for pizza in cart_items:
#                     # pizza_order = orders.objects.create(order=order,pizza=pizza.pizza,final_price=final_price+(pizza.pizza.price)) 
#                     pizza_order = cart.get_cart_total()
#         payment = client.orders.create({'amount':amount,'payment_capture': '1' })
#     cart.save()
#     return render(request, 'index.html')

api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN, endpoint="https://test.instamojo.com/api/1.1/")



def home(request):
    pizzas = Pizza.objects.all()
    context = {'pizzas': pizzas}
    return render(request, 'homepage.html', context)

def login_page(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
    
            user_obj = User.objects.filter(username=username)
            if not user_obj.exists():
                messages.warning(request, 'User not found.')
                return redirect('/login/')

            if user_obj :=  authenticate(username=username, password=password):
                login(request, user_obj)
                return redirect('/')
    
            messages.error(request, 'wrong password')

            return redirect('/login/')

        except Exception as e:
            messages.error(request, 'Something went wrong.')
            return redirect('/register/')
    return render(request, 'login.html')

def register_page(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
    
            user_obj = User.objects.filter(username=username)
            if user_obj.exists():
                messages.error(request, 'Username is taken.')
                return redirect('/register/')

            user_obj = User.objects.create(username=username)
            user_obj.set_password(password)
            user_obj.save()
    
            messages.success(request, 'Account Created.')

            return redirect('/login/')

        except Exception as e:
            messages.error(request, 'Something went wrong.')
            return redirect('/register/')
    return render(request, 'register.html')

@login_required(login_url='/login/')
def add_cart(request, pizza_uid):
    user = request.user
    pizza_obj = Pizza.objects.get(uid=pizza_uid)
    cart , _ = Cart.objects.get_or_create(user=user, is_paid = False)
    cart_items = CartItems.objects.create(cart=cart,pizza = pizza_obj)
    return redirect('/')


@login_required(login_url='/login/')
def cart(request):
    cart = Cart.objects.get(is_paid = False , user = request.user)
    response = api.payment_request_create(
        amount = cart.get_cart_total(),
        purpose = "Order",
        buyer_name = request.user.username,
        # email = "jyoti.kumarigiet@gmail.com",
        redirect_url = "http://127.0.0.1:8000/success/"
    )
    cart.instamojo_id = response['payment_request']['id']
    cart.save()
    context = {'carts' : cart, 'payment_url' : response['payment_request']['longurl']}
    # print(response)
    return render(request, 'cart.html', context)

# def cart(request):
#     # cart = Cart.objects.get(user = request.user)
#     price = 5000 
#     order_currency = 'INR'
#     # order_receipt = 'order_reptid_11'
#     # notes = {'Shipping address': 'Bommanahalli, Bangalore'} # OPtional
#     payment = client.order.create(dict(amount=price, currency=order_currency, payment_capture=1))
#     payment_id = payment['id']
#     context = {'amount': 500, 'api_key': RAZORPAY_API_KEY,'payment_id' : payment_id
#     }
#     return render(request, 'index.html', context)

@login_required(login_url='/login/')
def remove_cart_items(request, cart_item_uid):
    try:
        CartItems.objects.get(uid=cart_item_uid).delete()
        return redirect('/cart/')
    except Exception as e:
        print(e)

@login_required(login_url='/login/')
def orders(request):
    orders= Cart.objects.filter(is_paid = False, user=request.user)
    context = {'orders' : orders}
    return render(request, 'orders.html', context)

@login_required(login_url='/login/')
def success(request):
    payment_request = request.GET.get('payment_request_id')
    cart = Cart.objects.get(instamojo_id = payment_request)
    cart.is_paid = True
    cart.save()
    return redirect('/orders/')
# def process_payment(request):
# http://127.0.0.1:8000/success/?payment_id=MOJO2309H05A66574015&payment_status=Credit&payment_request_id=3d0f3de58d00422f97493283a00dc9c1
# L9Q6BG.GVL@Ea@B