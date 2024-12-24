from django.contrib import admin
from unfold.admin import ModelAdmin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import (
    BuilderDetails, State, City, Image, Plan, Document, 
    FAQ, Project, Testimonial
)

@admin.register(BuilderDetails)
class BuilderDetailsAdmin(ModelAdmin):
    list_display = ['name', 'company_name', 'license_number', 'contact_email']
    search_fields = ['name', 'company_name']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(State)
class StateAdmin(ModelAdmin):
    list_display = ['name', 'abbreviation']
    search_fields = ['name', 'abbreviation']

@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ['name', 'state']
    list_filter = ['state']
    search_fields = ['name']


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ['name', 'project_type', 'status']
    list_filter = ['project_type', 'status']
    search_fields = ['name', 'project_address']
    filter_horizontal = ['plans', 'images', 'documents']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ['plan_name', 'plan_type', 'availability_status']
    list_filter = ['availability_status', 'plan_type']
    search_fields = ['plan_name']

@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = ['image']

@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title']

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ['question']
    search_fields = ['question']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Testimonial)
class TestimonialAdmin(ModelAdmin):
    list_display = ['name', 'source']
    list_filter = ['source']
    search_fields = ['name']
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
