from django.urls import path
from . import views
from .views import search

urlpatterns = [
    path('addpro/', views.addpro, name='addpro'),
    path('product/oderde/', views.oderde, name='oderde'),
    path('product/', views.product, name='product'), 
    path('products/edit/<int:id>/', views.product_edit, name='product_edit'),
    path('oderde/delete/<int:id>/', views.delete, name='delete'),
    path('product/product/view/<int:id>/', views.view, name='view'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wish, name='addtowishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('remove_from_wishlist/<int:product_id>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('search/', search, name='search'),
    path('category/<str:category_name>/', views.category_filter, name='category_filter'),
    path('orders/', views.oddlist, name='oddlist'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('brand/<str:ab>', views.brand, name='brand'),

    path('resolve-cancellation/<int:order_id>/', views.resolve_cancellation, name='resolve_cancellation'), 
]
