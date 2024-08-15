from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, Profile, AnimalProfile, AnimalUser

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_admin', 'is_superuser', 'is_staff', 'is_active','id', 'is_animal')
    list_filter = ('is_admin', 'is_superuser', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_superuser', 'is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_admin', 'is_superuser', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Profile)
admin.site.register(AnimalProfile)
admin.site.register(AnimalUser)

admin.site.unregister(Group)