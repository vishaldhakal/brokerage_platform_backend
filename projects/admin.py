from django.contrib import admin
from unfold.admin import ModelAdmin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import (   
    State, City, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project, Contact
)

# Inline Admin Classes
class RenderingInline(admin.TabularInline):
    model = Rendering
    extra = 1
    fields = ['title', 'image']

class LotInline(admin.TabularInline):
    model = Lot
    extra = 1
    fields = ['lot_number', 'availability_status', 'lot_size', 'price', 'description', 'lot_rendering', 'floor_plans']

class FloorPlanInline(admin.TabularInline):
    model = FloorPlan
    extra = 1
    fields = ['name', 'house_type', 'square_footage', 'bedrooms', 'bathrooms', 'garage_spaces', 'availability_status', 'plan_file']

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    fields = ['title', 'document_type', 'document', 'description']

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1
    fields = ['name', 'email', 'phone', 'order']

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

@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['name', 'project_type', 'status', 'city', 'price_starting_from', 'is_featured', 'is_active']
    list_filter = ['project_type', 'status', 'city', 'is_featured', 'is_active']
    search_fields = ['name', 'project_address', 'city__name']
    ordering = ['-id']
    readonly_fields = ['slug', 'total_lots', 'available_lots', 'total_floor_plans']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'project_type', 'status', 'project_address', 'city')
        }),
        ('Description', {
            'fields': ('project_description', 'project_video_url')
        }),
        ('Pricing', {
            'fields': ('price_starting_from', 'price_ending_at', 'pricing_details')
        }),
        ('Property Details', {
            'fields': (),
            'description': 'Property details are now managed at lot and floor plan level'
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
        ContactInline,
    ]
    
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Rendering)
class RenderingAdmin(ModelAdmin):
    list_display = ['title', 'project']
    list_filter = ['project']
    search_fields = ['title', 'project__name']
    ordering = ['project__name', 'title']

@admin.register(SitePlan)
class SitePlanAdmin(ModelAdmin):
    list_display = ['project', 'has_file']
    search_fields = ['project__name']
    ordering = ['project__name']
    
    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    has_file.short_description = 'Has File'

@admin.register(Lot)
class LotAdmin(ModelAdmin):
    list_display = ['lot_number', 'project', 'availability_status', 'lot_size', 'price', 'has_rendering']
    list_filter = ['availability_status', 'project']
    search_fields = ['lot_number', 'project__name']
    ordering = ['project__name', 'lot_number']
    filter_horizontal = ['floor_plans']
    
    def has_rendering(self, obj):
        return bool(obj.lot_rendering)
    has_rendering.boolean = True
    has_rendering.short_description = 'Has Rendering'

@admin.register(FloorPlan)
class FloorPlanAdmin(ModelAdmin):
    list_display = ['name', 'project', 'house_type', 'square_footage', 'bedrooms', 'bathrooms', 'availability_status', 'has_plan_file']
    list_filter = ['house_type', 'availability_status', 'project']
    search_fields = ['name', 'project__name']
    ordering = ['project__name', 'name']
    
    def has_plan_file(self, obj):
        return bool(obj.plan_file)
    has_plan_file.boolean = True
    has_plan_file.short_description = 'Has Plan File'

@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ['title', 'document_type', 'project']
    list_filter = ['document_type', 'project']
    search_fields = ['title', 'project__name']
    ordering = ['-id']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Contact)
class ContactAdmin(ModelAdmin):
    list_display = ['name', 'project', 'email', 'phone']
    list_filter = ['project']
    search_fields = ['name', 'email', 'project__name']
    ordering = ['project__name', 'order', 'name']

# Admin site customization
admin.site.site_header = "Brokerage Platform Administration"
admin.site.site_title = "Brokerage Admin"
admin.site.index_title = "Welcome to Brokerage Platform Administration"
