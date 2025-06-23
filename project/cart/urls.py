from django.urls import path
from . import views

urlpatterns = [
  
    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='addcart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment/', views.payment, name='payment'),
    path('done/', views.done, name='done'),
    path('orders/', views.order_summary, name='order_summary'),
    path('cancel-order/<int:order_id>/', views.request_cancellation, name='request_cancellation'),
    path('pluscart/', views.plus_cart, name='plus_cart'),
    path('minuscart/', views.minus_cart, name='minus_cart'),
    path('stripe-payment/', views.stripe_payment, name='stripe_payment'),
    





     
    
]