from django.shortcuts import render
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from .models import (
    BuilderDetails, State, City, Image, Plan, Document, 
    FAQ, Community, Project, Testimonial
)
from .serializers import (
    BuilderDetailsSerializer, StateSerializer, CitySerializer,
    ImageSerializer, PlanSerializer, DocumentSerializer,
    FAQSerializer, CommunitySerializer, ProjectSerializer,
    TestimonialSerializer
)
import json

# Create your views here.

class StateListCreateView(generics.ListCreateAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'abbreviation']
    filterset_fields = ['name', 'abbreviation']

class StateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    lookup_field = 'slug'

class CityListCreateView(generics.ListCreateAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'state__name']
    filterset_fields = ['state']

class CityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    lookup_field = 'slug'

class BuilderDetailsListCreateView(generics.ListCreateAPIView):
    queryset = BuilderDetails.objects.all()
    serializer_class = BuilderDetailsSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'company_name']

class BuilderDetailsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BuilderDetails.objects.all()
    serializer_class = BuilderDetailsSerializer
    lookup_field = 'slug'

class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'city__name', 'community_title']
    filterset_fields = ['city']

    def perform_create(self, serializer):
        try:
            # Get FAQs data
            faqs_data = self.request.data.get('faqs', '[]')
            
            # Parse FAQs data safely
            if isinstance(faqs_data, str):
                try:
                    faqs_data = json.loads(faqs_data)
                except json.JSONDecodeError:
                    faqs_data = []
            
            # Create community instance
            instance = serializer.save()
            
            # Handle FAQs
            for faq_data in faqs_data:
                if isinstance(faq_data, dict):
                    faq = FAQ.objects.create(
                        question=faq_data.get('question', ''),
                        answer=faq_data.get('answer', '')
                    )
                    instance.faqs.add(faq)
            
            return instance
            
        except Exception as e:
            # Log the error and re-raise
            print(f"Error creating community: {str(e)}")
            raise

class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'slug'

    def perform_update(self, serializer):
        try:
            # Get FAQs data
            faqs_data = self.request.data.get('faqs', '[]')
            if isinstance(faqs_data, str):
                try:
                    faqs_data = json.loads(faqs_data)
                except json.JSONDecodeError:
                    faqs_data = []

            # Update community instance
            instance = serializer.save()

            # Handle FAQs - clear existing and add new ones
            if faqs_data:
                instance.faqs.clear()
                for faq_data in faqs_data:
                    if isinstance(faq_data, dict):
                        faq = FAQ.objects.create(
                            question=faq_data.get('question', ''),
                            answer=faq_data.get('answer', '')
                        )
                        instance.faqs.add(faq)

            return instance

        except Exception as e:
            print(f"Error updating community: {str(e)}")
            raise

class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'community__name', 'project_type']
    filterset_fields = ['project_type', 'status', 'community']

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = (MultiPartParser, FormParser)
    lookup_field = 'slug'

class ImageListCreateView(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class ImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class DocumentListCreateView(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

class PlanListCreateView(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['plan_name', 'plan_type']

class PlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'source']

class TestimonialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
