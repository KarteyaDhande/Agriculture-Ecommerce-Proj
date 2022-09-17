from django.urls import path

from . import views

urlpatterns = [
#Leave as empty string for base url
	path('', views.store, name="store"),
	path('login/', views.loginUser, name="login"),
	path('logout/', views.logoutUser, name="logout"),
	path('register/', views.registerUser, name="register"),
	path('search/', views.search, name="search"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path('blog/', views.blog, name="blog"),
]