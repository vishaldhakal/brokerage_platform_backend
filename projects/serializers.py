from rest_framework import serializers
from .models import (
    BuilderDetails, State, City, Image, Plan, Document, 
    FAQ, Project, Testimonial
)

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    
    class Meta:
        model = City
        fields = '__all__'

class BuilderDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuilderDetails
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    plans = PlanSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_plans = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_documents = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        allow_empty=True
    )
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())

    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def _is_file(self, data):
        """Helper method to check if the data is a file object"""
        return hasattr(data, 'read') and callable(data.read)

    def _get_valid_files(self, data, field_name):
        """Helper method to extract valid files from request data"""
        if not data:
            return []
            
        if isinstance(data, list):
            return [f for f in data if self._is_file(f)]
            
        if isinstance(data, dict):
            return [f for f in data.values() if self._is_file(f)]
            
        return []

    def create(self, validated_data):
        # Extract and validate files
        uploaded_images = self._get_valid_files(validated_data.pop('uploaded_images', []), 'uploaded_images')
        uploaded_plans = self._get_valid_files(validated_data.pop('uploaded_plans', []), 'uploaded_plans')
        uploaded_documents = self._get_valid_files(validated_data.pop('uploaded_documents', []), 'uploaded_documents')
        
        project = Project.objects.create(**validated_data)
        
        # Handle images
        for image_file in uploaded_images:
            image = Image.objects.create(image=image_file)
            project.images.add(image)
            
        # Handle plans
        for plan_file in uploaded_plans:
            plan = Plan.objects.create(
                plan=plan_file,
                plan_name=getattr(plan_file, 'name', 'Unnamed Plan'),
                plan_type='Default'
            )
            project.plans.add(plan)
            
        # Handle documents
        for doc_file in uploaded_documents:
            document = Document.objects.create(
                document=doc_file,
                title=getattr(doc_file, 'name', 'Unnamed Document')
            )
            project.documents.add(document)
            
        return project

    def update(self, instance, validated_data):
        # Extract and validate files
        uploaded_images = self._get_valid_files(validated_data.pop('uploaded_images', []), 'uploaded_images')
        uploaded_plans = self._get_valid_files(validated_data.pop('uploaded_plans', []), 'uploaded_plans')
        uploaded_documents = self._get_valid_files(validated_data.pop('uploaded_documents', []), 'uploaded_documents')
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle images
        for image_file in uploaded_images:
            image = Image.objects.create(image=image_file)
            instance.images.add(image)
            
        # Handle plans
        for plan_file in uploaded_plans:
            plan = Plan.objects.create(
                plan=plan_file,
                plan_name=getattr(plan_file, 'name', 'Unnamed Plan'),
                plan_type='Default'
            )
            instance.plans.add(plan)
            
        # Handle documents
        for doc_file in uploaded_documents:
            document = Document.objects.create(
                file=doc_file,
                title=getattr(doc_file, 'name', 'Unnamed Document')
            )
            instance.documents.add(document)
            
        return instance

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'
