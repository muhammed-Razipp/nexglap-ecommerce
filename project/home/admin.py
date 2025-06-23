from django.contrib import admin
from . models import Members

class MembersAdmin(admin.ModelAdmin):
    list_display="username","email"



admin.site.register(Members,MembersAdmin)

# Register your models here.
