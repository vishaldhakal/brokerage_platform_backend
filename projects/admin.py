from django.contrib import admin
from unfold.admin import ModelAdmin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import (   
    State, City, Developer, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project
)

# Inline Admin Classes
class RenderingInline(admin.TabularInline):
    model = Rendering
    extra = 1
    fields = ['title', 'image', 'order']

class LotInline(admin.TabularInline):
    model = Lot
    extra = 1
    fields = ['lot_number', 'availability_status', 'lot_size', 'price', 'description']

class FloorPlanInline(admin.TabularInline):
    model = FloorPlan
    extra = 1
    fields = ['name', 'house_type', 'square_footage', 'bedrooms', 'bathrooms', 'garage_spaces', 'availability_status', 'starting_price', 'order']
    filter_horizontal = ['lots']

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    fields = ['title', 'document_type', 'document', 'description']

# Main Admin Classes
@admin.register(State)
class StateAdmin(ModelAdmin):
    list_display = ['name', 'abbreviation', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'abbreviation']
    ordering = ['name']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ['name', 'state', 'is_active']
    list_filter = ['state', 'is_active']
    search_fields = ['name', 'state__name']
    ordering = ['state__name', 'name']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Developer)
class DeveloperAdmin(ModelAdmin):
    list_display = ['name', 'company_name', 'contact_email', 'contact_phone', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'company_name', 'contact_email']
    ordering = ['name']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['name', 'project_type', 'status', 'city', 'developer', 'price_starting_from', 'is_featured', 'is_active']
    list_filter = ['project_type', 'status', 'city', 'developer', 'is_featured', 'is_active']
    search_fields = ['name', 'project_address', 'city__name', 'developer__name']
    ordering = ['-id']
    readonly_fields = ['slug', 'total_lots', 'available_lots', 'total_floor_plans']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'project_type', 'status', 'project_address', 'city', 'developer')
        }),
        ('Description', {
            'fields': ('project_description', 'project_video_url')
        }),
        ('Pricing', {
            'fields': ('price_starting_from', 'price_ending_at', 'pricing_details')
        }),
        ('Property Details', {
            'fields': ('area_square_footage', 'lot_size', 'garage_spaces', 'bedrooms', 'bathrooms')
        }),
        ('Financial Information', {
            'fields': ('deposit_structure', 'commission')
        }),
        ('Timeline Information', {
            'fields': ('occupancy', 'aps')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
        ('Statistics', {
            'fields': ('total_lots', 'available_lots', 'total_floor_plans'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [
        RenderingInline,
        LotInline,
        FloorPlanInline,
        DocumentInline,
    ]
    
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Rendering)
class RenderingAdmin(ModelAdmin):
    list_display = ['title', 'project', 'order']
    list_filter = ['project']
    search_fields = ['title', 'project__name']
    ordering = ['project__name', 'order', 'title']

@admin.register(SitePlan)
class SitePlanAdmin(ModelAdmin):
    list_display = ['project', 'has_image', 'has_pdf']
    search_fields = ['project__name']
    ordering = ['project__name']
    
    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Has Image'
    
    def has_pdf(self, obj):
        return bool(obj.pdf)
    has_pdf.boolean = True
    has_pdf.short_description = 'Has PDF'

@admin.register(Lot)
class LotAdmin(ModelAdmin):
    list_display = ['lot_number', 'project', 'availability_status', 'lot_size', 'price']
    list_filter = ['availability_status', 'project']
    search_fields = ['lot_number', 'project__name']
    ordering = ['project__name', 'lot_number']

@admin.register(FloorPlan)
class FloorPlanAdmin(ModelAdmin):
    list_display = ['name', 'project', 'house_type', 'square_footage', 'bedrooms', 'bathrooms', 'availability_status', 'starting_price', 'order']
    list_filter = ['house_type', 'availability_status', 'project']
    search_fields = ['name', 'project__name']
    ordering = ['project__name', 'order', 'name']
    filter_horizontal = ['lots']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ['title', 'document_type', 'project']
    list_filter = ['document_type', 'project']
    search_fields = ['title', 'project__name']
    ordering = ['-id']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

# Admin site customization
admin.site.site_header = "Brokerage Platform Administration"
admin.site.site_title = "Brokerage Admin"
admin.site.index_title = "Welcome to Brokerage Platform Administration"
