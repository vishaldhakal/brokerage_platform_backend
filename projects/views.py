from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json
from .models import (
    State, City, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project
)
from .serializers import (
    StateSerializer, CitySerializer,
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

# Project Views
class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.filter(is_active=True)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'project_type', 'project_address', 'city__name']
    filterset_fields = {
        'project_type': ['exact'],
        'status': ['exact'],
        'city': ['exact'],
        'price_starting_from': ['gte', 'lte'],
        'price_ending_at': ['gte', 'lte'],
        'is_featured': ['exact'],
    }
    ordering_fields = ['price_starting_from', 'price_ending_at', 'name', 'id']

    def get_queryset(self):
        queryset = super().get_queryset()
        # Add prefetch_related for better performance
        return queryset.select_related('city').prefetch_related(
            'renderings', 'lots', 'floor_plans', 'documents'
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectSerializer
        return ProjectListSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Debug: Print received data
            print("Received data:", request.data)
            print("Received files:", request.FILES)
            
            # Parse form data
            data = {}
            
            # Handle basic fields
            for key, value in request.data.items():
                if key.startswith('uploaded_') or key.startswith('existing_'):
                    continue
                if key == 'city_id':
                    data['city_id'] = int(value)
                else:
                    data[key] = value
            
            # Handle lots (both existing and new)
            lots_data = []
            for key, value in request.data.items():
                if key.startswith('lots[') and key.endswith(']'):
                    try:
                        lot_data = json.loads(value)
                        # Handle lot rendering file
                        lot_rendering_key = key.replace(']', '.lot_rendering]')
                        if lot_rendering_key in request.FILES:
                            lot_data['lot_rendering'] = request.FILES[lot_rendering_key]
                        lots_data.append(lot_data)
                    except json.JSONDecodeError:
                        continue
            data['lots'] = lots_data
            
            # Handle floor plans (both existing and new)
            floor_plans_data = []
            for key, value in request.data.items():
                if key.startswith('floor_plans[') and key.endswith(']'):
                    try:
                        plan_data = json.loads(value)
                        # Handle plan file
                        plan_file_key = key.replace(']', '.plan_file]')
                        if plan_file_key in request.FILES:
                            plan_data['plan_file'] = request.FILES[plan_file_key]
                        floor_plans_data.append(plan_data)
                    except json.JSONDecodeError:
                        continue
            data['floor_plans'] = floor_plans_data
            
            # Handle uploaded renderings
            uploaded_renderings = []
            for key, value in request.FILES.items():
                if key == 'uploaded_images':
                    uploaded_renderings.append({'image': value})
            data['uploaded_renderings'] = uploaded_renderings
            
            # Handle uploaded documents
            uploaded_documents = []
            for key, value in request.FILES.items():
                if key == 'uploaded_documents':
                    uploaded_documents.append({'document': value})
            data['uploaded_documents'] = uploaded_documents
            
            # Debug: Print final data
            print("Final data for serializer:", data)
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('city').prefetch_related(
            'renderings', 'lots', 'floor_plans', 'documents'
        )
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def update(self, request, *args, **kwargs):
        try:
            # Debug: Print received data
            print("Update - Received data:", request.data)
            print("Update - Received files:", request.FILES)
            
            # Parse form data
            data = {}
            
            # Handle basic fields
            for key, value in request.data.items():
                if key.startswith('lots[') or key.startswith('floor_plans[') or key.startswith('existing_'):
                    continue
                if key == 'city_id':
                    data['city_id'] = int(value)
                else:
                    data[key] = value
            
            # Handle lots (both existing and new)
            lots_data = []
            if 'lots' in request.data:
                try:
                    lots_data = json.loads(request.data['lots'])
                    # Handle lot rendering files - they should be in request.FILES with keys like 'lots[0].lot_rendering'
                    for i, lot_data in enumerate(lots_data):
                        lot_rendering_key = f'lots[{i}].lot_rendering'
                        if lot_rendering_key in request.FILES:
                            lot_data['lot_rendering'] = request.FILES[lot_rendering_key]
                except json.JSONDecodeError:
                    lots_data = []
            data['lots'] = lots_data
            
            # Handle floor plans (both existing and new)
            floor_plans_data = []
            if 'floor_plans' in request.data:
                try:
                    floor_plans_data = json.loads(request.data['floor_plans'])
                    # Handle plan files - they should be in request.FILES with keys like 'floor_plans[0].plan_file'
                    for i, plan_data in enumerate(floor_plans_data):
                        plan_file_key = f'floor_plans[{i}].plan_file'
                        if plan_file_key in request.FILES:
                            plan_data['plan_file'] = request.FILES[plan_file_key]
                except json.JSONDecodeError:
                    floor_plans_data = []
            data['floor_plans'] = floor_plans_data
            
            # Handle uploaded renderings
            uploaded_renderings = []
            for key, value in request.FILES.items():
                if key == 'uploaded_images':
                    uploaded_renderings.append({'image': value})
            data['uploaded_renderings'] = uploaded_renderings
            
            # Handle uploaded documents
            uploaded_documents = []
            for key, value in request.FILES.items():
                if key == 'uploaded_documents':
                    uploaded_documents.append({'document': value})
            data['uploaded_documents'] = uploaded_documents
            
            # Handle existing files
            existing_images = request.data.get('existing_images', '[]')
            existing_documents = request.data.get('existing_documents', '[]')
            
            try:
                data['existing_images'] = json.loads(existing_images)
                data['existing_documents'] = json.loads(existing_documents)
            except json.JSONDecodeError:
                data['existing_images'] = []
                data['existing_documents'] = []
            
            # Debug: Print final data
            print("Update - Final data for serializer:", data)
            
            serializer = self.get_serializer(self.get_object(), data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
            
        except Exception as e:
            print("Update error:", str(e))
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
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
        return Rendering.objects.filter(project__slug=project_slug).order_by('title')

class ProjectFloorPlansView(generics.ListAPIView):
    serializer_class = FloorPlanSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return FloorPlan.objects.filter(project__slug=project_slug).order_by('name')

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
        return super().get_queryset().select_related('city').prefetch_related(
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
        ).select_related('city').prefetch_related(
            'renderings', 'lots', 'floor_plans'
        )
