from django.shortcuts import render
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser
from .models import (
    BuilderDetails, State, City, Image, Plan, Document, 
    FAQ, Project, Testimonial
)
from .serializers import (
    BuilderDetailsSerializer, StateSerializer, CitySerializer,
    ImageSerializer, PlanSerializer, DocumentSerializer,
    FAQSerializer, ProjectSerializer,
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


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'project_type', 'project_address', 'city__name']
    filterset_fields = {
        'project_type': ['exact'],
        'status': ['exact'],
        'city': ['exact'],
        'price_starting_from': ['gte', 'lte'],
        'price_ending_at': ['gte', 'lte'],
        'bedrooms': ['exact', 'gte', 'lte'],
        'bathrooms': ['exact', 'gte', 'lte'],
        'garage_spaces': ['exact', 'gte', 'lte'],
    }
    ordering_fields = ['price_starting_from', 'price_ending_at', 'name', 'created_at']

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
