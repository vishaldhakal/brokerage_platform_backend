
from rest_framework import generics, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import json
from .models import (
    State, City, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project, Amenity, Contact, FeatureFinish, ProjectInquires
)
from .serializers import (
    StateSerializer, CitySerializer,
    RenderingSerializer, SitePlanSerializer, LotSerializer, FloorPlanSerializer,
    DocumentSerializer, ProjectSerializer, AmenitySerializer, ContactSerializer,
    ProjectListSerializer, RenderingListSerializer, FloorPlanListSerializer,
    FeatureFinishSerializer, ProjectInquirySerializer
)
from django.shortcuts import get_object_or_404



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
            'renderings', 'lots', 'floor_plans', 'documents', 'contacts', 'features_finishes'
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
            
            # First, try to get lots as a JSON array (new format)
            if 'lots' in request.data:
                try:
                    lots_data = json.loads(request.data['lots'])
                    # Handle lot rendering files for each lot
                    for index, lot_data in enumerate(lots_data):
                        lot_rendering_key = f'lots[{index}].lot_rendering'
                        if lot_rendering_key in request.FILES:
                            lot_data['lot_rendering'] = request.FILES[lot_rendering_key]
                except json.JSONDecodeError:
                    lots_data = []
            
            # If no lots JSON found, fall back to individual lots[index] fields (legacy format)
            if not lots_data:
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
            
            # First, try to get floor_plans as a JSON array (new format)
            if 'floor_plans' in request.data:
                try:
                    floor_plans_data = json.loads(request.data['floor_plans'])
                    # Handle plan files for each floor plan
                    for index, plan_data in enumerate(floor_plans_data):
                        plan_file_key = f'floor_plans[{index}].plan_file'
                        if plan_file_key in request.FILES:
                            plan_data['plan_file'] = request.FILES[plan_file_key]
                except json.JSONDecodeError:
                    floor_plans_data = []
            
            # If no floor_plans JSON found, fall back to individual floor_plans[index] fields (legacy format)
            if not floor_plans_data:
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
            
            # Handle contacts - JSON approach for consistency
            contacts_data = []
            if 'contacts' in request.data:
                try:
                    contacts_data = json.loads(request.data['contacts'])
                except json.JSONDecodeError:
                    contacts_data = []
            data['contacts'] = contacts_data
            
            # Handle amenity_ids
            if 'amenity_ids' in request.data:
                try:
                    amenity_ids = json.loads(request.data['amenity_ids'])
                    data['amenity_ids'] = amenity_ids
                except json.JSONDecodeError:
                    data['amenity_ids'] = []
            
            # Handle Features & Finishes (JSON array)
            if 'features_finishes_write' in request.data:
                try:
                    data['features_finishes_write'] = json.loads(request.data['features_finishes_write'])
                except json.JSONDecodeError:
                    data['features_finishes_write'] = []
            
            # Handle uploaded renderings
            uploaded_renderings = []
            for key, value in request.FILES.items():
                if key == 'uploaded_images':
                    uploaded_renderings.append({'image': value})
            data['uploaded_renderings'] = uploaded_renderings

            # Handle uploaded features & finishes (images)
            uploaded_features_finishes = []
            for key, value in request.FILES.items():
                if key == 'uploaded_features_finishes':
                    uploaded_features_finishes.append({'image': value})
            data['uploaded_features_finishes'] = uploaded_features_finishes
            
            # Handle uploaded legal documents
            uploaded_legal_documents = []
            legal_doc_titles = {}
            for key, value in request.data.items():
                if key.startswith('uploaded_legal_documents_titles['):
                    index = key.split('[')[1].split(']')[0]
                    legal_doc_titles[int(index)] = value
            
            for key, value in request.FILES.items():
                if key == 'uploaded_legal_documents':
                    doc_index = len(uploaded_legal_documents)
                    uploaded_legal_documents.append({
                        'document': value,
                        'title': legal_doc_titles.get(doc_index, ''),
                        'document_type': 'Document'
                    })
            data['uploaded_legal_documents'] = uploaded_legal_documents
            
            # Handle uploaded marketing documents
            uploaded_marketing_documents = []
            marketing_doc_titles = {}
            for key, value in request.data.items():
                if key.startswith('uploaded_marketing_documents_titles['):
                    index = key.split('[')[1].split(']')[0]
                    marketing_doc_titles[int(index)] = value
            
            for key, value in request.FILES.items():
                if key == 'uploaded_marketing_documents':
                    doc_index = len(uploaded_marketing_documents)
                    uploaded_marketing_documents.append({
                        'document': value,
                        'title': marketing_doc_titles.get(doc_index, ''),
                        'document_type': 'Marketing Material'
                    })
            data['uploaded_marketing_documents'] = uploaded_marketing_documents
            
            # Handle existing document IDs
            if 'existing_legal_documents' in request.data:
                try:
                    data['existing_legal_documents'] = json.loads(request.data['existing_legal_documents'])
                except json.JSONDecodeError:
                    data['existing_legal_documents'] = []
            
            if 'existing_marketing_documents' in request.data:
                try:
                    data['existing_marketing_documents'] = json.loads(request.data['existing_marketing_documents'])
                except json.JSONDecodeError:
                    data['existing_marketing_documents'] = []

            if 'existing_features_finishes' in request.data:
                try:
                    data['existing_features_finishes'] = json.loads(request.data['existing_features_finishes'])
                except json.JSONDecodeError:
                    data['existing_features_finishes'] = []
            
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
            'renderings', 'lots', 'floor_plans', 'documents', 'contacts', 'features_finishes'
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
            
            # Handle lots (both existing and new) - similar to create method
            lots_data = []
            
            # First, try to get lots as a JSON array (new format)
            if 'lots' in request.data:
                try:
                    lots_data = json.loads(request.data['lots'])
                    # Handle lot rendering files for each lot
                    for index, lot_data in enumerate(lots_data):
                        lot_rendering_key = f'lots[{index}].lot_rendering'
                        if lot_rendering_key in request.FILES:
                            lot_data['lot_rendering'] = request.FILES[lot_rendering_key]
                except json.JSONDecodeError:
                    lots_data = []
            
            # If no lots JSON found, fall back to individual lots[index] fields (legacy format)
            if not lots_data:
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
            
            # Handle floor plans (both existing and new) - similar to create method
            floor_plans_data = []
            
            # First, try to get floor_plans as a JSON array (new format)
            if 'floor_plans' in request.data:
                try:
                    floor_plans_data = json.loads(request.data['floor_plans'])
                    # Handle plan files for each floor plan
                    for index, plan_data in enumerate(floor_plans_data):
                        plan_file_key = f'floor_plans[{index}].plan_file'
                        if plan_file_key in request.FILES:
                            plan_data['plan_file'] = request.FILES[plan_file_key]
                except json.JSONDecodeError:
                    floor_plans_data = []
            
            # If no floor_plans JSON found, fall back to individual floor_plans[index] fields (legacy format)
            if not floor_plans_data:
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

            # Explicit deletions (optional)
            if 'deleted_floor_plan_ids' in request.data:
                try:
                    data['deleted_floor_plan_ids'] = json.loads(request.data['deleted_floor_plan_ids'])
                except json.JSONDecodeError:
                    data['deleted_floor_plan_ids'] = []
            if 'deleted_lot_ids' in request.data:
                try:
                    data['deleted_lot_ids'] = json.loads(request.data['deleted_lot_ids'])
                except json.JSONDecodeError:
                    data['deleted_lot_ids'] = []
            
            # Handle contacts
            contacts_data = []
            if 'contacts' in request.data:
                try:
                    contacts_data = json.loads(request.data['contacts'])
                except json.JSONDecodeError:
                    contacts_data = []
            data['contacts'] = contacts_data
            
            # Handle amenity_ids
            if 'amenity_ids' in request.data:
                try:
                    amenity_ids = json.loads(request.data['amenity_ids'])
                    data['amenity_ids'] = amenity_ids
                except json.JSONDecodeError:
                    data['amenity_ids'] = []
            
            # Handle Features & Finishes (JSON array)
            if 'features_finishes_write' in request.data:
                try:
                    data['features_finishes_write'] = json.loads(request.data['features_finishes_write'])
                except json.JSONDecodeError:
                    data['features_finishes_write'] = []
            
            # Handle uploaded renderings
            uploaded_renderings = []
            for key, value in request.FILES.items():
                if key == 'uploaded_images':
                    uploaded_renderings.append({'image': value})
            data['uploaded_renderings'] = uploaded_renderings

            # Handle uploaded features & finishes (images)
            uploaded_features_finishes = []
            for key, value in request.FILES.items():
                if key == 'uploaded_features_finishes':
                    uploaded_features_finishes.append({'image': value})
            data['uploaded_features_finishes'] = uploaded_features_finishes
            
            # Handle uploaded legal documents
            uploaded_legal_documents = []
            legal_doc_titles = {}
            for key, value in request.data.items():
                if key.startswith('uploaded_legal_documents_titles['):
                    index = key.split('[')[1].split(']')[0]
                    legal_doc_titles[int(index)] = value
            
            for key, value in request.FILES.items():
                if key == 'uploaded_legal_documents':
                    doc_index = len(uploaded_legal_documents)
                    uploaded_legal_documents.append({
                        'document': value,
                        'title': legal_doc_titles.get(doc_index, ''),
                        'document_type': 'Document'
                    })
            data['uploaded_legal_documents'] = uploaded_legal_documents
            
            # Handle uploaded marketing documents
            uploaded_marketing_documents = []
            marketing_doc_titles = {}
            for key, value in request.data.items():
                if key.startswith('uploaded_marketing_documents_titles['):
                    index = key.split('[')[1].split(']')[0]
                    marketing_doc_titles[int(index)] = value
            
            for key, value in request.FILES.items():
                if key == 'uploaded_marketing_documents':
                    doc_index = len(uploaded_marketing_documents)
                    uploaded_marketing_documents.append({
                        'document': value,
                        'title': marketing_doc_titles.get(doc_index, ''),
                        'document_type': 'Marketing Material'
                    })
            data['uploaded_marketing_documents'] = uploaded_marketing_documents
            
            # Handle existing files
            existing_images = request.data.get('existing_images', '[]')
            existing_legal_documents = request.data.get('existing_legal_documents', '[]')
            existing_marketing_documents = request.data.get('existing_marketing_documents', '[]')
            existing_features_finishes = request.data.get('existing_features_finishes', '[]')
            
            try:
                data['existing_images'] = json.loads(existing_images)
                data['existing_legal_documents'] = json.loads(existing_legal_documents)
                data['existing_marketing_documents'] = json.loads(existing_marketing_documents)
                data['existing_features_finishes'] = json.loads(existing_features_finishes)
            except json.JSONDecodeError:
                data['existing_images'] = []
                data['existing_legal_documents'] = []
                data['existing_marketing_documents'] = []
                data['existing_features_finishes'] = []
            
            # Debug: Print final data
            print("Update - Final data for serializer:", data)
            print("Update - Deleted lot IDs:", data.get('deleted_lot_ids', []))
            print("Update - Deleted floor plan IDs:", data.get('deleted_floor_plan_ids', []))
            
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

class PublicProjectDetailView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return super().get_queryset().select_related('city').prefetch_related(
            'renderings', 'lots', 'floor_plans', 'documents', 'contacts', 'features_finishes'
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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

# Features & Finishes Views (mirror Rendering)
class FeatureFinishListCreateView(generics.ListCreateAPIView):
    queryset = FeatureFinish.objects.all()
    serializer_class = FeatureFinishSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'project__name']
    filterset_fields = ['project']

class FeatureFinishDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FeatureFinish.objects.all()
    serializer_class = FeatureFinishSerializer
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
    serializer_class = LotSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['lot_number', 'project__name']
    filterset_fields = ['project', 'availability_status']
    


    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        if project_slug:
            return Lot.objects.filter(project__slug=project_slug).order_by('lot_number')
        return Lot.objects.all().order_by('lot_number')

    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        if project_slug:
            project = get_object_or_404(Project, slug=project_slug)
            serializer.save(project=project)
        else:
            serializer.save()

class LotDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LotSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    lookup_field = 'id'

    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        if project_slug:
            return Lot.objects.filter(project__slug=project_slug)
        return Lot.objects.all()

    def perform_update(self, serializer):
        # Handle lot rendering file separately
        lot_rendering = self.request.FILES.get('lot_rendering')
        if lot_rendering:
            serializer.instance.lot_rendering = lot_rendering
        serializer.save()

    def perform_destroy(self, instance):
        # Delete the lot rendering file if it exists
        if instance.lot_rendering:
            instance.lot_rendering.delete(save=False)
        instance.delete()

# Floor Plan Views
class FloorPlanListCreateView(generics.ListCreateAPIView):
    queryset = FloorPlan.objects.all()
    serializer_class = FloorPlanListSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'project__name']
    filterset_fields = ['project', 'house_type', 'availability_status']

class FloorPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FloorPlan.objects.all()
    serializer_class = FloorPlanSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

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

class ProjectRenderingCreateView(generics.CreateAPIView):
    serializer_class = RenderingSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def create(self, request, *args, **kwargs):
        print("ProjectRenderingCreateView - Received data:", request.data)
        print("ProjectRenderingCreateView - Received files:", request.FILES)
        print("ProjectRenderingCreateView - Content type:", request.content_type)
        print("ProjectRenderingCreateView - Project slug:", self.kwargs.get('project_slug'))
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        print("ProjectRenderingCreateView - Saving rendering for project:", project.name)
        serializer.save(project=project)
        print("ProjectRenderingCreateView - Rendering saved successfully")

class ProjectRenderingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RenderingSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Rendering.objects.filter(project__slug=project_slug)

class ProjectFeatureFinishesView(generics.ListAPIView):
    serializer_class = FeatureFinishSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return FeatureFinish.objects.filter(project__slug=project_slug).order_by('title')

class ProjectFeatureFinishCreateView(generics.CreateAPIView):
    serializer_class = FeatureFinishSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project)

class ProjectFeatureFinishDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FeatureFinishSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return FeatureFinish.objects.filter(project__slug=project_slug)

class ProjectFloorPlansView(generics.ListAPIView):
    serializer_class = FloorPlanSerializer
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return FloorPlan.objects.filter(project__slug=project_slug).order_by('name')

class ProjectFloorPlanCreateView(generics.CreateAPIView):
    serializer_class = FloorPlanSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def create(self, request, *args, **kwargs):
        print("ProjectFloorPlanCreateView - Received data:", request.data)
        print("ProjectFloorPlanCreateView - Received files:", request.FILES)
        print("ProjectFloorPlanCreateView - Content type:", request.content_type)
        print("ProjectFloorPlanCreateView - Project field value:", request.data.get('project'))
        print("ProjectFloorPlanCreateView - Project field type:", type(request.data.get('project')))
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project)

class ProjectFloorPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FloorPlanSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def update(self, request, *args, **kwargs):
        print("ProjectFloorPlanDetailView - Received data:", request.data)
        print("ProjectFloorPlanDetailView - Received files:", request.FILES)
        print("ProjectFloorPlanDetailView - Content type:", request.content_type)
        return super().update(request, *args, **kwargs)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return FloorPlan.objects.filter(project__slug=project_slug)

# Project-specific lot views
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

# New separate tab views
class ProjectContactsView(generics.ListCreateAPIView):
    serializer_class = ContactSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        return project.contacts.all().order_by('order')
    
    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        print(f"Creating contact for project: {project.name} (slug: {project_slug})")
        print(f"Contact data: {serializer.validated_data}")
        serializer.save(project=project)

class ProjectMarketingDocumentsView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Document.objects.filter(
            project__slug=project_slug,
            document_type='Marketing Material'
        ).order_by('title')
    
    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project, document_type='Marketing Material')

class ProjectLegalDocumentsView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Document.objects.filter(
            project__slug=project_slug,
            document_type='Document'
        ).order_by('title')
    
    def perform_create(self, serializer):
        project_slug = self.kwargs.get('project_slug')
        project = get_object_or_404(Project, slug=project_slug)
        serializer.save(project=project, document_type='Document')

# Detail views for individual items
class ContactDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Contact.objects.filter(project__slug=project_slug)

class MarketingDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Document.objects.filter(
            project__slug=project_slug,
            document_type='Marketing Material'
        )

class LegalDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        project_slug = self.kwargs.get('project_slug')
        return Document.objects.filter(
            project__slug=project_slug,
            document_type='Document'
        )

# Featured Projects View
class FeaturedProjectsView(generics.ListAPIView):
    serializer_class = ProjectListSerializer
    queryset = Project.objects.filter(is_featured=True, is_active=True)
    
    def get_queryset(self):
        return super().get_queryset().select_related('city').prefetch_related(
            'renderings', 'lots', 'floor_plans', 'contacts'
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
            'renderings', 'lots', 'floor_plans', 'contacts'
        )

# Amenity Views
class AmenityListCreateView(generics.ListCreateAPIView):
    queryset = Amenity.objects.filter(is_active=True)
    serializer_class = AmenitySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    filterset_fields = ['category', 'is_active']
    ordering_fields = ['name', 'category', 'order']
    ordering = ['category', 'order', 'name']

class AmenityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer


# Project Inquiry Views
class ProjectInquiryListCreateView(generics.ListCreateAPIView):
    queryset = ProjectInquires.objects.all()
    serializer_class = ProjectInquirySerializer

class ProjectInquiryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProjectInquires.objects.all()
    serializer_class = ProjectInquirySerializer
