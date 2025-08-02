from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = [
        'profile_image', 'address', 'city', 'state', 'zip_code', 'country',
        'business_description', 'years_in_business', 'linkedin_url',
        'facebook_url', 'twitter_url', 'instagram_url', 'email_notifications',
        'sms_notifications'
    ]

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    list_display = [
        'username', 'email', 'company_name',
        'is_verified', 'is_active', 'is_staff', 'created_at'
    ]
    list_filter = [
        'is_verified', 'is_active', 'is_staff', 'is_superuser',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'username', 'email', 'company_name',
        'license_number'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Business Information', {
            'fields': ('company_name', 'license_number', 'website')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Business Information', {
            'fields': ('company_name', 'license_number', 'website')
        }),
    )
    
    inlines = [UserProfileInline]
    
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'first_name'

@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    list_display = [
        'user', 'city', 'state', 'country', 'years_in_business',
        'email_notifications', 'sms_notifications', 'created_at'
    ]
    list_filter = [
        'country', 'state', 'email_notifications', 'sms_notifications',
        'created_at', 'updated_at'
    ]
    search_fields = [
        'user__username', 'user__email', 'user__first_name', 'user__last_name',
        'city', 'state', 'address'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Image', {
            'fields': ('profile_image',)
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Business Information', {
            'fields': ('business_description', 'years_in_business')
        }),
        ('Social Media', {
            'fields': ('linkedin_url', 'facebook_url', 'twitter_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

# Admin site customization
admin.site.site_header = "Brokerage Platform Administration"
admin.site.site_title = "Brokerage Admin"
admin.site.index_title = "Welcome to Brokerage Platform Administration"
