
from django.shortcuts import render,get_object_or_404,redirect
from .models import Customer
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login,logout
from django.views.generic import View
from django.db.models import Q


@login_required(login_url='signin')
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def profileview(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        location = request.POST.get('location')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')
        phone = request.POST.get('phone')

        
        if user and first_name and last_name and location and city and pincode and phone:
           
            if not pincode.isdigit():
                messages.error(request, "Invalid pincode: must be numeric.")
                return render(request, "profile1/profile.html")

           
            if not phone.isdigit() or len(phone) != 10:
                messages.error(request, "Invalid phone number and must be 10-digit ")
                return render(request, "profile1/profile.html")

            
            reg = Customer(
                user=user,
                first_name=first_name,
                last_name=last_name,
                location=location,
                city=city,
                phone=phone,
                pincode=int(pincode)  
            )
            reg.save()
            messages.success(request, "Profile updated Successfully...!!")
        else:
            messages.error(request, "All fields are required.")
    else:
        messages.warning(request, "Please Set Your Profile")
    
    return render(request, "profile1/profile.html")




@login_required(login_url='signin')
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def address(request):
    add=Customer.objects.filter(user=request.user)
    return render(request,"profile1/addadre.html",{'add':add})




@login_required(login_url='sginin')
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def updateaddress(request,pk):
    add = Customer.objects.get(pk=pk)

    if request.method == "POST":
      
        add.first_name = request.POST.get('first_name', add.first_name)
        add.last_name = request.POST.get('last_name', add.last_name)
        add.location = request.POST.get('location', add.location)
        add.city = request.POST.get('city', add.city)
        add.pincode = request.POST.get('pincode', add.pincode)
        add.phone = request.POST.get('phone', add.phone)

       
        add.save()
        messages.success(request, "Congratulations! Profile updated successfully.")
        return redirect('address')  

   
    return render(request, "profile1/upadd.html", {"add": add})
    


def deleteaddress(request, pk):
    add = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        add.delete()
        messages.success(request, "Address deleted successfully.")
        return redirect('address')  
    return redirect('address')


def about(request):
    return render(request, 'about.html')








    