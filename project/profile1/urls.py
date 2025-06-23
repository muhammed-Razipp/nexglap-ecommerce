from django.urls import path
from . import views
  # Make sure this points to the right app

urlpatterns = [
path('profile/', views.profileview, name='profileview'),
path('addadre/',views.address,name='address'),
path('deleteaddress/<int:pk>/',views.deleteaddress,name='deleteaddress'),
path('upadd/<int:pk>',views.updateaddress,name='upadd'),
path('about/',views.about,name='about')


]
