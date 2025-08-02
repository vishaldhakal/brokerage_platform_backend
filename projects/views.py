from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import (
    State, City, Developer, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project
)
from .serializers import (
    StateSerializer, CitySerializer, DeveloperSerializer,
    RenderingSerializer, SitePlanSerializer, LotSerializer, FloorPlanSerializer,
    DocumentSerializer, ProjectSerializer,
    ProjectListSerializer, RenderingListSerializer, FloorPlanListSerializer, LotListSerializer
)
import json

# State Views
class StateListCreateView(generics.ListCreateAPIView):
    queryset = State.objects.filter(is_active=True)
    serializer_class = StateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'abbreviation']
    filterset_fields = ['name', 'abbreviation']

class StateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    lookup_field = 'slug'

# City Views
class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'state__name']
    filterset_fields = ['state']

class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = 'slug'

# Developer Views
class DeveloperListCreateView(generics.ListCreateAPIView):
    queryset = Developer.objects.filter(is_active=True)
    serializer_class = DeveloperSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'company_name', 'contact_email']

class DeveloperDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = 'slug'

# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectListSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'project_type', 'project_address', 'city__name', 'developer__name']
    filterset_fields = {
        'project_type': ['exact'],
        'status': ['exact'],
        'city': ['exact'],
        'developer': ['exact'],
        'price_starting_from': ['gte', 'lte'],
        'price_ending_at': ['gte', 'lte'],
        'bedrooms': ['exact', 'gte', 'lte'],
        'bathrooms': ['exact', 'gte', 'lte'],
        'garage_spaces': ['exact', 'gte', 'lte'],
        'is_featured': ['exact'],
    }
    ordering_fields = ['price_starting_from', 'price_ending_at', 'name', 'id']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add prefetch_related for better performance
        return queryset.select_related('city', 'developer').prefetch_related(
            'renderings', 'lots', 'floor_plans', 'documents'
        )

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('city', 'developer').prefetch_related(
            'renderings', 'lots', 'floor_plans', 'documents'
        )

# Rendering Views
class RenderingListCreateView(generics.ListCreateAPIView):
    queryset = Rendering.objects.all()
    serializer_class = RenderingListSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'project__name']
    filterset_fields = ['project']

class RenderingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Rendering.objects.all()
    serializer_class = RenderingSerializer
    parser_classes = (MultiPartParser, FormParser)

# Site Plan Views
class SitePlanListCreateView(generics.ListCreateAPIView):
    queryset = SitePlan.objects.all()
    serializer_class = SitePlanSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project']

class SitePlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SitePlan.objects.all()
    serializer_class = SitePlanSerializer
    parser_classes = (MultiPartParser, FormParser)

# Lot Views
class LotListCreateView(generics.ListCreateAPIView):
    queryset = Lot.objects.all()
    serializer_class = LotListSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['lot_number', 'project__name']
    filterset_fields = ['project', 'availability_status']

class LotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lot.objects.all()
    serializer_class = LotSerializer

# Floor Plan Views
class FloorPlanListCreateView(generics.ListCreateAPIView):
    queryset = FloorPlan.objects.all()
    serializer_class = FloorPlanListSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'project__name']
    filterset_fields = ['project', 'house_type', 'availability_status']

class FloorPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FloorPlan.objects.all()
    serializer_class = FloorPlanSerializer
    parser_classes = (MultiPartParser, FormParser)

# Document Views
class DocumentListCreateView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'project__name']
    filterset_fields = ['project', 'document_type']

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

# Additional API Views for specific functionality
class ProjectRenderingsView(generics.ListAPIView):
    serializer_class = RenderingSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Rendering.objects.filter(project__slug=project_slug).order_by('order')

class ProjectFloorPlansView(generics.ListAPIView):
    serializer_class = FloorPlanSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return FloorPlan.objects.filter(project__slug=project_slug).order_by('order')

class ProjectLotsView(generics.ListAPIView):
    serializer_class = LotSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Lot.objects.filter(project__slug=project_slug).order_by('lot_number')

class ProjectDocumentsView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Document.objects.filter(project__slug=project_slug)

# Featured Projects View
class FeaturedProjectsView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    queryset = Project.objects.filter(is_featured=True, is_active=True)
    
    def get_queryset(self):
        return super().get_queryset().select_related('city', 'developer').prefetch_related(
            'renderings', 'lots', 'floor_plans'
        )

# Developer Projects View
class DeveloperProjectsView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    
    def get_queryset(self):
        developer_slug = self.kwargs.get('developer_slug')
        return Project.objects.filter(
            developer__slug=developer_slug, 
            is_active=True
        ).select_related('city', 'developer').prefetch_related(
            'renderings', 'lots', 'floor_plans'
        )

# City Projects View
class CityProjectsView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    
    def get_queryset(self):
        city_slug = self.kwargs.get('city_slug')
        return Project.objects.filter(
            city__slug=city_slug, 
            is_active=True
        ).select_related('city', 'developer').prefetch_related(
            'renderings', 'lots', 'floor_plans'
        )
