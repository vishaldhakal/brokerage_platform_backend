from rest_framework import serializers
from .models import (
    State, City, Developer, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project
)

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    state_abbreviation = serializers.CharField(source='state.abbreviation', read_only=True)
    
    class Meta:
        model = City
        fields = '__all__'

class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
            'logo': {'required': False, 'allow_null': True},
        }

class RenderingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rendering
        fields = '__all__'

class SitePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePlan
        fields = '__all__'

class LotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lot
        fields = '__all__'

class FloorPlanSerializer(serializers.ModelSerializer):
    lots = LotSerializer(many=True, read_only=True)
    lot_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Lot.objects.all(),
        source='lots',
        required=False
    )
    
    class Meta:
        model = FloorPlan
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects
    renderings = RenderingSerializer(many=True, read_only=True)
    site_plan = SitePlanSerializer(read_only=True)
    lots = LotSerializer(many=True, read_only=True)
    floor_plans = FloorPlanSerializer(many=True, read_only=True)
    documents = DocumentSerializer(many=True, read_only=True)
    
    # Related object serializers
    city = CitySerializer(read_only=True)
    developer = DeveloperSerializer(read_only=True)
    
    # Foreign key IDs for write operations
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source='city',
        write_only=True
    )
    developer_id = serializers.PrimaryKeyRelatedField(
        queryset=Developer.objects.all(),
        source='developer',
        write_only=True
    )
    
    # File upload fields
    uploaded_renderings = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_site_plan = serializers.DictField(
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_lots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_floor_plans = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_documents = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )

    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True},
        }

    def create(self, validated_data):
        # Extract uploaded data
        uploaded_renderings = validated_data.pop('uploaded_renderings', [])
        uploaded_site_plan = validated_data.pop('uploaded_site_plan', {})
        uploaded_lots = validated_data.pop('uploaded_lots', [])
        uploaded_floor_plans = validated_data.pop('uploaded_floor_plans', [])
        uploaded_documents = validated_data.pop('uploaded_documents', [])
        
        # Create project
        project = Project.objects.create(**validated_data)
        
        # Create renderings
        for rendering_data in uploaded_renderings:
            Rendering.objects.create(project=project, **rendering_data)
        
        # Create site plan
        if uploaded_site_plan:
            SitePlan.objects.create(project=project, **uploaded_site_plan)
        
        # Create lots
        for lot_data in uploaded_lots:
            Lot.objects.create(project=project, **lot_data)
        
        # Create floor plans
        for floor_plan_data in uploaded_floor_plans:
            lots_data = floor_plan_data.pop('lots', [])
            floor_plan = FloorPlan.objects.create(project=project, **floor_plan_data)
            if lots_data:
                floor_plan.lots.set(lots_data)
        
        # Create documents
        for document_data in uploaded_documents:
            Document.objects.create(project=project, **document_data)
        
        return project

    def update(self, instance, validated_data):
        # Extract uploaded data
        uploaded_renderings = validated_data.pop('uploaded_renderings', [])
        uploaded_site_plan = validated_data.pop('uploaded_site_plan', {})
        uploaded_lots = validated_data.pop('uploaded_lots', [])
        uploaded_floor_plans = validated_data.pop('uploaded_floor_plans', [])
        uploaded_documents = validated_data.pop('uploaded_documents', [])
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle renderings
        for rendering_data in uploaded_renderings:
            Rendering.objects.create(project=instance, **rendering_data)
        
        # Handle site plan
        if uploaded_site_plan:
            SitePlan.objects.update_or_create(
                project=instance,
                defaults=uploaded_site_plan
            )
        
        # Handle lots
        for lot_data in uploaded_lots:
            Lot.objects.create(project=instance, **lot_data)
        
        # Handle floor plans
        for floor_plan_data in uploaded_floor_plans:
            lots_data = floor_plan_data.pop('lots', [])
            floor_plan = FloorPlan.objects.create(project=instance, **floor_plan_data)
            if lots_data:
                floor_plan.lots.set(lots_data)
        
        # Handle documents
        for document_data in uploaded_documents:
            Document.objects.create(project=instance, **document_data)
        
        return instance

# Simplified serializers for list views
class ProjectListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    developer_name = serializers.CharField(source='developer.name', read_only=True)
    total_lots = serializers.IntegerField(read_only=True)
    available_lots = serializers.IntegerField(read_only=True)
    total_floor_plans = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'project_type', 'status', 'project_address',
            'city_name', 'developer_name', 'price_starting_from', 'price_ending_at',
            'total_lots', 'available_lots', 'total_floor_plans', 'is_featured',
            'is_active'
        ]

# Serializers for individual components
class RenderingListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Rendering
        fields = '__all__'

class FloorPlanListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    lots_count = serializers.SerializerMethodField()
    
    class Meta:
        model = FloorPlan
        fields = '__all__'
    
    def get_lots_count(self, obj):
        return obj.lots.count()

class LotListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Lot
        fields = '__all__'
