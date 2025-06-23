from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.urls import reverse
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_POST

from product.models import Product
from .models import Payment, Order
from profile1.models import Customer

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required(login_url='signin')
def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, "Product added to Cart")
    return redirect('product')


def view_cart(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        total += product.price * quantity
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity
        })

    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total': total})


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, "Product removed from cart.")
    return redirect('cart')


@login_required(login_url='signin')
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def payment(request):
    user = request.user
    session_cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0

    for product_id, quantity in session_cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_amount += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })

    shipping_cost = 40
    total_with_shipping = total_amount + shipping_cost
    addresses = Customer.objects.filter(user=user)

    if request.method == "POST":
        address_id = request.POST.get('custid')
        payment_method = request.POST.get('payment_method')

        if not address_id:
            messages.error(request, "Please select a shipping address.")
            return redirect('payment')

        try:
            address = Customer.objects.get(id=address_id, user=user)
        except Customer.DoesNotExist:
            messages.error(request, "Invalid address selected.")
            return redirect('payment')

        if payment_method == "cod":
            payment = Payment.objects.create(
                user=user,
                amount=total_with_shipping,
                stripe_payment_status="Pending",
                paid=False
            )

            for item in cart_items:
                Order.objects.create(
                    user=user,
                    product=item['product'],
                    quantity=item['quantity'],
                    customer=address,
                    address=f"{address.location}, {address.city}, {address.pincode}",
                    phone=address.phone,
                    total_amount=item['subtotal'],
                    order_status="Placed (Cash On Delivery)",
                    payment=payment,
                )

            request.session['cart'] = {}
            messages.success(request, "Order placed successfully with Cash on Delivery.")
            return render(request, 'cart/done.html')

        elif payment_method == "online":
            request.session['address_id'] = address.id
            return redirect('stripe_payment')

        messages.error(request, "Invalid payment method selected.")
        return redirect('payment')

    context = {
        'cart_items': cart_items,
        'total_amount': total_with_shipping,
        'add': addresses,
    }
    return render(request, 'cart/payment.html', context)


@login_required
def order_summary(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')
    steps = ['Placed', 'Packed', 'Shipped', 'On the way', 'Delivered']
    status_index = {status: index for index, status in enumerate(steps)}

    context = {
        'orders': orders,
        'steps': steps,
        'status_index': status_index
    }

    return render(request, 'cart/orders.html', context)



@login_required
def request_cancellation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.cancellation_requested:
        order.cancellation_requested = True
        order.save()
        messages.success(request, f"Cancellation request activated for Order ID {order_id}.")
    else:
        messages.warning(request, f"Cancellation request already activated for Order ID {order_id}.")

    return redirect('order_summary')  # ✅ Correct




@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        cart = request.session.get('cart', {})
        prod_id_str = str(prod_id)

        if prod_id_str in cart:
            cart[prod_id_str] += 1
            request.session['cart'] = cart

            product = get_object_or_404(Product, id=prod_id)
            quantity = cart[prod_id_str]
            amount = product.price * quantity

            total = sum(get_object_or_404(Product, id=pid).price * qty for pid, qty in cart.items())
            grand_total = total + 40

            return JsonResponse({
                'quantity': quantity,
                'amount': amount,
                'totalamount': grand_total
            })
        return JsonResponse({'error': 'Product not in cart'}, status=404)


@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        cart = request.session.get('cart', {})
        prod_id_str = str(prod_id)

        if prod_id_str in cart:
            if cart[prod_id_str] > 1:
                cart[prod_id_str] -= 1
            request.session['cart'] = cart

            product = get_object_or_404(Product, id=prod_id)
            quantity = cart.get(prod_id_str, 1)
            amount = product.price * quantity

            total = sum(get_object_or_404(Product, id=pid).price * qty for pid, qty in cart.items())
            shipping_cost = 40 if cart else 0
            grand_total = total + shipping_cost

            return JsonResponse({
                'quantity': quantity,
                'amount': amount,
                'totalamount': grand_total
            })
        return JsonResponse({'error': 'Product not in cart'}, status=404)


@login_required
def stripe_payment(request):
    cart = request.session.get('cart', {})
    line_items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        price = int(product.price * 100)
        total += price * quantity
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'unit_amount': price,
                'product_data': {'name': product.name},
            },
            'quantity': quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('done')),
        cancel_url=request.build_absolute_uri(reverse('payment')),
        customer_email=request.user.email,
    )

    payment = Payment.objects.create(
        user=request.user,
        amount=total / 100,
        stripe_checkout_id=session.id,
        stripe_payment_status='pending',
        paid=False,
    )

    request.session['payment_id'] = payment.id
    return redirect(session.url, code=303)


def done(request):
    payment_id = request.session.get('payment_id')
    if not payment_id:
        return redirect('cart')

    payment = get_object_or_404(Payment, id=payment_id)
    payment.paid = True
    payment.stripe_payment_status = "succeeded"
    payment.save()

    address = get_object_or_404(Customer, id=request.session.get('address_id'))
    cart = request.session.get('cart', {})

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            customer=address,
            address=f"{address.location}, {address.city}, {address.pincode}",
            phone=address.phone,
            total_amount=product.price * quantity,
            order_status="Paid (Stripe)",
            payment=payment,
        )

    request.session['cart'] = {}
    request.session.pop('address_id', None)
    request.session.pop('payment_id', None)

    messages.success(request, "Payment successful and order placed.")
    return render(request, 'cart/done.html')

@login_required
@require_POST
def update_order_status_user(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    new_status = request.POST.get('order_status')
    

    allowed_statuses = ['Delivered', 'Cancelled']
    if new_status not in allowed_statuses:
        messages.error(request, "Invalid status.")
        return redirect('order_summary')

    order.order_status = new_status
    order.save()
    messages.success(request, f"Order #{order.id} status updated to '{new_status}'.")
    return redirect('order_summary')
