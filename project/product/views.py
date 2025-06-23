
from django.shortcuts import redirect, render , get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Member
from .models import Product
from .models import Wishlist
from .models import Brand
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import Product, Category
from cart.models import Order
from django.views.decorators.http import require_POST
from .models import Product, Category

from .models import Product, Category, Brand







@never_cache
def oderde(request):
    pro=Product.objects.all()
    print(pro)
    return render(request,'product/oderde.html',{'pro' :pro})

@never_cache

def product(request):
    products = Product.objects.all()
    category_name = request.GET.get('category', '') 

    if category_name:
        
        products = products.filter(category__name__icontains=category_name)

    categories = Category.objects.all()

    print("inside product view")
    print(products)
    return render(request, 'product.html', {
        'products': products,
        'categories': categories, 
        'selected_category': category_name 
    })

def search(request):
    query = request.GET.get('q', '')
    category_name = request.GET.get('category', '') # Renamed for consistency

    products = Product.objects.filter(name__icontains=query)

    if category_name:
        products = products.filter(category__name__icontains=category_name)

    categories = Category.objects.all()
    return render(request, 'product.html', {
        'products': products,
        'query': query,
        'categories': categories,
        'selected_category': category_name 
    })





def addpro(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        
        category_id = request.POST.get('category')
        new_category_name = request.POST.get('new_category')
        if new_category_name:
            category, _ = Category.objects.get_or_create(name=new_category_name)
        elif category_id:
            category = Category.objects.get(id=category_id)
        else:
            category = None

        
        brand_id = request.POST.get('brand')
        new_brand_name = request.POST.get('new_brand')
        if new_brand_name:
            brand, _ = Brand.objects.get_or_create(name=new_brand_name)
        elif brand_id:
            brand = Brand.objects.get(id=brand_id)
        else:
            brand = None

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            image=image,
            category=category,
            brand=brand
        )

        return redirect('oderde')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'product/addpro.html', {'categories': categories, 'brands': brands})




  

def delete(request,id):
    product=Product.objects.get(id=id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("oderde")


def view(request,id):
    products = Product.objects.get(id=id);
    return render(request,'view.html',{'products': products})

def wishlist(request):
    return render(request, 'wishlist.html')

@login_required(login_url='signin') 
def add_to_wish(request, product_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    
    product = get_object_or_404(Product, id=product_id)

    if Wishlist.objects.filter(user=request.user, product=product).exists():
        messages.info(request,"already in your wishlist!!!")
        return redirect('product')
    
    Wishlist.objects.create(user=request.user, product=product)
    messages.success(request, "added to your wishlist")

    return redirect('product')

@login_required(login_url='signin') 
def wishlist(request):
    if not request.user.is_authenticated:
        return redirect('signin')

    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


def remove_from_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('signin')
    
    product = get_object_or_404(Product,id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()

    if wishlist_item:
        wishlist_item.delete()
    return redirect('wishlist')


def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    products = Product.objects.filter(name__icontains=query)

    if category:
        products = products.filter(category__name__icontains=category)

    categories = Category.objects.all()
    return render(request, 'product.html', {'products': products, 'query': query, 'categories': categories})






@login_required(login_url='sginin')
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        product.is_sale = request.POST.get('is_sale') == 'on'
        product.sale_price = request.POST.get('sale_price') or None

        
        new_category_name = request.POST.get('new_category', '').strip()
        category_id = request.POST.get('category')
        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
        else:
            category = get_object_or_404(Category, id=category_id)
        product.category = category

       
        new_brand_name = request.POST.get('new_brand', '').strip()
        brand_id = request.POST.get('brand')
        if new_brand_name:
            brand, created = Brand.objects.get_or_create(name=new_brand_name)
        else:
            brand = get_object_or_404(Brand, id=brand_id)
        product.brand = brand

        
        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect('oderde')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    return render(request, 'product/proedit.html', {'product': product, 'categories': categories, 'brands': brands})

def category_filter(request, category_name):
    products = Product.objects.filter(category__name=category_name)
    categories = Category.objects.all() 

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_name  
    }

    return render(request, 'product.html', context)


@login_required(login_url='signin')  
def oddlist(request):
  
    orders = Order.objects.all() 

    STATUS_CHOICES = Order._meta.get_field('order_status').choices

    context = {
        'orders': orders,
        'STATUS_CHOICES': STATUS_CHOICES,
    }
    return render(request, 'product/oddlist.html', context)




def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('order_status')
        if new_status:
            order.order_status = new_status
            order.save()
        return redirect('oddlist')


@login_required(login_url='sginin')
def resolve_cancellation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.cancellation_requested:
        order.cancellation_requested = False  
        order.save()
        messages.success(request, f"Cancellation request for Order ID {order_id} has been resolved.")
    else:
        messages.error(request, f"No active cancellation request for Order ID {order_id}.")
    return redirect('oddlist')

def brand(request, ab):
    ab = ab.replace('-', ' ')
    try:
        brand = Brand.objects.get(name__iexact=ab)
        products = Product.objects.filter(brand=brand)
        return render(request, 'product.html', {'products': products, 'brand': brand})
    except Brand.DoesNotExist:
        messages.error(request, "That brand doesn't exist...")
        return redirect('product')


