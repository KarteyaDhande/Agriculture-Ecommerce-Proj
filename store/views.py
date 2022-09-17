from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
from .models import *
from .utils import cookieCart,cartData, guestOrder
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
# Create your views here.

def store(request):
	data = cartData(request)
	cartItems = data['cartItems']

	products = Product.objects.all()
	context = {'products':products ,'cartItems' : cartItems}
	return render(request, 'store/store.html', context)

def search(request):
	data = cartData(request)
	cartItems = data['cartItems']
	q = request.GET['q']
	#add more filters by filter(name__icontains=q,a,b,c)
	products = Product.objects.filter(name__icontains=q).order_by('-id')
	context = {'cartItems' : cartItems, 'products':products}
	return render(request, 'store/search.html', context)

def cart(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'store/checkout.html', context)


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse ('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)



	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment complete!', safe=False)

def blog(request):
	data = cartData(request)
	cartItems = data['cartItems']
	context = {'cartItems': cartItems}
	return render(request, 'store/blog.html', context)

def loginUser(request):
	page = 'login'
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('store')

	return render(request, 'store/login_register.html', {'page':page})

def logoutUser(request):
	logout(request)
	return redirect('login')

def registerUser(request):
	page = 'register'
	form = CustomUserCreationForm()

	if request.method == 'POST':
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.save()

			user = authenticate(request, username=user.username, email=user.email, password=request.POST['password1'])

			if user is not None:
				login(request, user)
				return redirect('store')

	context = {'form':form, 'page':page}
	return render(request, 'store/login_register.html', context)