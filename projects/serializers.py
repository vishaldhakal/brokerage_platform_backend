from rest_framework import serializers
from django.db import transaction
import json
from .models import (
    State, City, Rendering, SitePlan, Lot, FloorPlan,
    Document, Project, Contact, Amenity, FeatureFinish
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

class RenderingSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Rendering
        fields = '__all__'
        read_only_fields = ['project']  # Make project field read-only
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True},
        }
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class FeatureFinishSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = FeatureFinish
        fields = '__all__'
        read_only_fields = ['project']
        extra_kwargs = {
            'title': {'required': False, 'allow_blank': True},
        }

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class SitePlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitePlan
        fields = '__all__'

class FloorPlanSerializer(serializers.ModelSerializer):
    plan_file_url = serializers.SerializerMethodField()
    # Allow explicit removal of an existing file via update API
    plan_file_remove = serializers.BooleanField(write_only=True, required=False, default=False)
    
    class Meta:
        model = FloorPlan
        fields = '__all__'
        read_only_fields = ['project']  # Make project field read-only
    
    def get_plan_file_url(self, obj):
        if obj.plan_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.plan_file.url)
            return obj.plan_file.url
        return None

    def update(self, instance, validated_data):
        # Handle explicit file removal
        remove_flag = validated_data.pop('plan_file_remove', False)
        if remove_flag and instance.plan_file:
            try:
                instance.plan_file.delete(save=False)
            except Exception:
                # ignore storage delete errors; continue with nulling field
                pass
            instance.plan_file = None

        # Normalize empty numeric fields coming as empty strings
        for key in ['square_footage', 'bedrooms', 'garage_spaces']:
            if key in validated_data and (validated_data[key] == '' or validated_data[key] is None):
                validated_data[key] = None
        for key in ['bathrooms']:
            if key in validated_data and (validated_data[key] == '' or validated_data[key] is None):
                validated_data[key] = None

        return super().update(instance, validated_data)

class FloorPlanIdsFlexibleField(serializers.Field):
    """Accepts either a JSON string (e.g. "[1,2]") or a Python list of ints.

    Always returns a Python list of ints for internal value. Used as write-only.
    """

    def to_internal_value(self, data):
        # Already a list → coerce elements to ints
        if isinstance(data, list):
            coerced: list[int] = []
            for item in data:
                try:
                    coerced.append(int(item))
                except (TypeError, ValueError):
                    # skip invalid entries
                    continue
            return coerced

        # FormData case: JSON string
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
                if isinstance(parsed, list):
                    coerced: list[int] = []
                    for item in parsed:
                        try:
                            coerced.append(int(item))
                        except (TypeError, ValueError):
                            continue
                    return coerced
            except json.JSONDecodeError:
                return []
        # Any other type → empty
        return []

    def to_representation(self, value):
        # Not used (write_only), but return list of IDs if ever called
        try:
            return [int(v) for v in value]
        except Exception:
            return []


class LotSerializer(serializers.ModelSerializer):
    lot_numbers_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        source='get_lot_numbers_list'
    )
    lot_rendering_url = serializers.SerializerMethodField()
    floor_plans = FloorPlanSerializer(many=True, read_only=True)
    # Accept list[int] for JSON, or JSON string for multipart
    floor_plan_ids = FloorPlanIdsFlexibleField(write_only=True, required=False, source='floor_plans')
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    class Meta:
        model = Lot
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'project']
        extra_kwargs = {
            'lot_rendering': {'required': False, 'allow_null': True},
            'lot_size': {'required': False, 'allow_null': True},
            'price': {'required': False, 'allow_null': True},
            'est_completion': {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
        }
    
    def get_lot_rendering_url(self, obj):
        if obj.lot_rendering:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.lot_rendering.url)
            return obj.lot_rendering.url
        return None
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['lot_numbers_list'] = instance.get_lot_numbers_list()
        return data

    def create(self, validated_data):
        # Remove floor_plans from validated_data if not present or empty
        floor_plans = validated_data.pop('floor_plans', None)
        lot_numbers_list = self.context.get('lot_numbers_list', [])
        instance = super().create(validated_data)
        if lot_numbers_list:
            instance.set_lot_numbers_list(lot_numbers_list)
            instance.save()
        # Set floor_plans if provided
        if floor_plans is not None:
            floor_plan_ids = floor_plans if isinstance(floor_plans, list) else []
            instance.floor_plans.set(FloorPlan.objects.filter(id__in=floor_plan_ids))
        return instance

    def update(self, instance, validated_data):
        # Remove floor_plans from validated_data if not present or empty
        floor_plans = validated_data.pop('floor_plans', None)
        lot_numbers_list = self.context.get('lot_numbers_list', [])
        instance = super().update(instance, validated_data)
        if lot_numbers_list:
            instance.set_lot_numbers_list(lot_numbers_list)
            instance.save()
        # Set floor_plans if provided
        if floor_plans is not None:
            floor_plan_ids = floor_plans if isinstance(floor_plans, list) else []
            instance.floor_plans.set(FloorPlan.objects.filter(id__in=floor_plan_ids))
        return instance

    def validate(self, attrs):
        # Remove project from validation since it will be set by the view
        attrs.pop('project', None)
        # Normalize empty lists
        floor_plans = attrs.get('floor_plans', None)
        if floor_plans == []:
            attrs['floor_plans'] = []
        return attrs



class DocumentSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
        extra_kwargs = {
            'document': {'required': False},
            'title': {'required': False, 'allow_blank': True},
        }
    
    def get_document_url(self, obj):
        if obj.document:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.document.url)
            return obj.document.url
        return None


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone', 'order', 'project']
        extra_kwargs = {
            'project': {'read_only': True},
            'name': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
            'order': {'required': False},
        }
    
    def validate(self, data):
        print(f"ContactSerializer validate called with data: {data}")
        return data

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects
    renderings = RenderingSerializer(many=True, read_only=True)
    site_plan = SitePlanSerializer(read_only=True)
    lots_data = LotSerializer(many=True, read_only=True, source='lots')
    floor_plans_data = FloorPlanSerializer(many=True, read_only=True, source='floor_plans')
    documents = DocumentSerializer(many=True, read_only=True)
    legal_documents = serializers.SerializerMethodField()
    marketing_documents = serializers.SerializerMethodField()
    contacts = ContactSerializer(many=True, read_only=True)
    features_finishes = FeatureFinishSerializer(many=True, read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    
    def get_legal_documents(self, obj):
        legal_docs = obj.documents.filter(document_type='Document')
        return DocumentSerializer(legal_docs, many=True, context=self.context).data
    
    def get_marketing_documents(self, obj):
        marketing_docs = obj.documents.filter(document_type='Marketing Material')
        return DocumentSerializer(marketing_docs, many=True, context=self.context).data
    
    def to_representation(self, instance):
        """Override to debug contacts field"""
        data = super().to_representation(instance)
        # Debug: Check if contacts exist
        try:
            contacts_count = instance.contacts.count()
            print(f"Debug: Project {instance.name} has {contacts_count} contacts")
            data['contacts'] = ContactSerializer(instance.contacts.all(), many=True, context=self.context).data
        except Exception as e:
            print(f"Debug: Error getting contacts for {instance.name}: {e}")
            data['contacts'] = []
        return data
    
    # Related object serializers
    city = CitySerializer(read_only=True)
    
    # Foreign key IDs for write operations
    city_id = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        source='city',
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

    uploaded_floor_plans = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_legal_documents = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    uploaded_marketing_documents = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    # Features & Finishes (write-only for create/update new projects)
    # Mirror renderings write pattern for features & finishes images
    uploaded_features_finishes = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    existing_features_finishes = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    # Update fields for handling both existing and new data
    floor_plans = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    existing_images = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    existing_legal_documents = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    existing_marketing_documents = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    # Contacts data
    contacts = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    
    # Amenities data
    amenity_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    # Explicit deletions
    deleted_floor_plan_ids = serializers.ListField(
        child=serializers.IntegerField(),
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
        # Extract data
        uploaded_renderings = validated_data.pop('uploaded_renderings', [])
        uploaded_site_plan = validated_data.pop('uploaded_site_plan', {})
        uploaded_legal_documents = validated_data.pop('uploaded_legal_documents', [])
        uploaded_marketing_documents = validated_data.pop('uploaded_marketing_documents', [])
        
        # Extract new data structure
        floor_plans_data = validated_data.pop('floor_plans', [])
        contacts_data = validated_data.pop('contacts', [])
        amenity_ids = validated_data.pop('amenity_ids', [])
        
        # Ensure city_id is properly set
        if 'city_id' in validated_data:
            validated_data['city_id'] = int(validated_data['city_id'])
        uploaded_features_finishes = validated_data.pop('uploaded_features_finishes', [])
        existing_features_finishes = validated_data.pop('existing_features_finishes', [])

        # Create project
        project = Project.objects.create(**validated_data)
        
        # Create renderings
        for rendering_data in uploaded_renderings:
            Rendering.objects.create(project=project, **rendering_data)
        
        # Create site plan
        if uploaded_site_plan:
            SitePlan.objects.create(project=project, **uploaded_site_plan)
        
        # Create floor plans first
        created_floor_plans = {}
        for floor_plan_data in floor_plans_data:
            try:
                # Handle file uploads - extract files from the request
                plan_file = floor_plan_data.pop('plan_file', None)
                existing_plan_file = floor_plan_data.pop('existing_plan_file', None)
                
                # Convert string numbers to appropriate types (only if not empty)
                if floor_plan_data.get('square_footage') and floor_plan_data['square_footage'].strip():
                    floor_plan_data['square_footage'] = int(floor_plan_data['square_footage'])
                else:
                    floor_plan_data['square_footage'] = None
                if floor_plan_data.get('bedrooms') and floor_plan_data['bedrooms'].strip():
                    floor_plan_data['bedrooms'] = int(floor_plan_data['bedrooms'])
                else:
                    floor_plan_data['bedrooms'] = None
                if floor_plan_data.get('bathrooms') and floor_plan_data['bathrooms'].strip():
                    floor_plan_data['bathrooms'] = float(floor_plan_data['bathrooms'])
                else:
                    floor_plan_data['bathrooms'] = None
                if floor_plan_data.get('garage_spaces') and floor_plan_data['garage_spaces'].strip():
                    floor_plan_data['garage_spaces'] = int(floor_plan_data['garage_spaces'])
                else:
                    floor_plan_data['garage_spaces'] = None

                # Only validate that house_type and availability_status are present (they have defaults)
                if not floor_plan_data.get('house_type'):
                    floor_plan_data['house_type'] = 'Single Family'
                if not floor_plan_data.get('availability_status'):
                    floor_plan_data['availability_status'] = 'Available'
                
                # Handle file for new floor plan
                if plan_file:
                    floor_plan_data['plan_file'] = plan_file
                
                floor_plan = FloorPlan.objects.create(project=project, **floor_plan_data)
                created_floor_plans[floor_plan.id] = floor_plan
            except Exception as e:
                import logging
                logging.error(f"Error creating floor plan: {e}")
                raise serializers.ValidationError(f"Error creating floor plan: {e}")
        
        # Create legal documents
        for document_data in uploaded_legal_documents:
            Document.objects.create(project=project, **document_data)
        
        # Create marketing documents
        for document_data in uploaded_marketing_documents:
            Document.objects.create(project=project, **document_data)
        
        # Create contacts
        for contact_data in contacts_data:
            Contact.objects.create(project=project, **contact_data)
        
        # Set amenities
        if amenity_ids:
            project.amenities.set(amenity_ids)
        
        # Create features & finishes (images)
        for ff in uploaded_features_finishes:
            FeatureFinish.objects.create(project=project, **ff)
        
        return project

    def update(self, instance, validated_data):
        # Extract data
        uploaded_renderings = validated_data.pop('uploaded_renderings', [])
        uploaded_site_plan = validated_data.pop('uploaded_site_plan', {})
        uploaded_legal_documents = validated_data.pop('uploaded_legal_documents', [])
        uploaded_marketing_documents = validated_data.pop('uploaded_marketing_documents', [])
        existing_images = validated_data.pop('existing_images', [])
        existing_legal_documents = validated_data.pop('existing_legal_documents', [])
        existing_marketing_documents = validated_data.pop('existing_marketing_documents', [])
        
        # Extract update data (for both existing and new items)
        floor_plans_data = validated_data.pop('floor_plans', [])
        contacts_data = validated_data.pop('contacts', [])
        amenity_ids = validated_data.pop('amenity_ids', [])
        deleted_floor_plan_ids = validated_data.pop('deleted_floor_plan_ids', [])
        uploaded_features_finishes = validated_data.pop('uploaded_features_finishes', [])
        existing_features_finishes = validated_data.pop('existing_features_finishes', None)

        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle renderings - delete removed ones and add new ones
        # If existing_images is provided, only keep those renderings
        if existing_images is not None:
            # Delete renderings that are not in the existing_images list
            instance.renderings.exclude(id__in=existing_images).delete()
        
        # Add new renderings
        for rendering_data in uploaded_renderings:
            Rendering.objects.create(project=instance, **rendering_data)
        
        # Handle site plan
        if uploaded_site_plan:
            SitePlan.objects.update_or_create(
                project=instance,
                defaults=uploaded_site_plan
            )
        
        # Handle floor plans (both existing and new)
        existing_floor_plan_ids = set()
        newly_created_floor_plan_ids = set()
        for plan_data in floor_plans_data:
            plan_id = plan_data.get('id')
            
            # Handle file uploads - extract files from the request
            plan_file = plan_data.pop('plan_file', None)
            existing_plan_file = plan_data.pop('existing_plan_file', None)
            
            if plan_id:
                try:
                    floor_plan = FloorPlan.objects.get(id=plan_id, project=instance)
                    for attr, value in plan_data.items():
                        if attr != 'id' and hasattr(floor_plan, attr):
                            if attr in ['square_footage', 'bedrooms', 'garage_spaces'] and value and str(value).strip():
                                value = int(value)
                            elif attr in ['bathrooms'] and value and str(value).strip():
                                value = float(value)
                            elif attr in ['square_footage', 'bedrooms', 'bathrooms', 'garage_spaces'] and (not value or str(value).strip() == ''):
                                value = None
                            setattr(floor_plan, attr, value)
                    
                    # Handle file updates
                    if plan_file:
                        floor_plan.plan_file = plan_file
                    elif existing_plan_file:
                        # Keep existing file
                        pass
                    elif plan_data.get('plan_file') and plan_data['plan_file'].get('markedForDeletion'):
                        # Remove the file if marked for deletion
                        if floor_plan.plan_file:
                            floor_plan.plan_file.delete(save=False)
                        floor_plan.plan_file = None
                    
                    floor_plan.save()
                    existing_floor_plan_ids.add(plan_id)
                except Exception as e:
                    import logging
                    logging.error(f"Error updating floor plan: {e}")
                    raise serializers.ValidationError(f"Error updating floor plan: {e}")
            else:
                try:
                    # Convert string numbers to appropriate types (only if not empty)
                    if plan_data.get('square_footage') and plan_data['square_footage'].strip():
                        plan_data['square_footage'] = int(plan_data['square_footage'])
                    else:
                        plan_data['square_footage'] = None
                    if plan_data.get('bedrooms') and plan_data['bedrooms'].strip():
                        plan_data['bedrooms'] = int(plan_data['bedrooms'])
                    else:
                        plan_data['bedrooms'] = None
                    if plan_data.get('bathrooms') and plan_data['bathrooms'].strip():
                        plan_data['bathrooms'] = float(plan_data['bathrooms'])
                    else:
                        plan_data['bathrooms'] = None
                    if plan_data.get('garage_spaces') and plan_data['garage_spaces'].strip():
                        plan_data['garage_spaces'] = int(plan_data['garage_spaces'])
                    else:
                        plan_data['garage_spaces'] = None
                    # Only validate that house_type and availability_status are present (they have defaults)
                    if not plan_data.get('house_type'):
                        plan_data['house_type'] = 'Single Family'
                    if not plan_data.get('availability_status'):
                        plan_data['availability_status'] = 'Available'
                    
                    # Handle file for new floor plan
                    if plan_file:
                        plan_data['plan_file'] = plan_file

                    # De-duplication: if a floor plan with same name already exists for this project, update it
                    existing_by_name = None
                    name_value = plan_data.get('name')
                    if name_value:
                        existing_by_name = FloorPlan.objects.filter(project=instance, name=name_value).first()

                    if existing_by_name:
                        for attr, value in plan_data.items():
                            if hasattr(existing_by_name, attr):
                                setattr(existing_by_name, attr, value)
                        existing_by_name.save()
                        newly_created_floor_plan_ids.add(existing_by_name.id)
                    else:
                        new_floor_plan = FloorPlan.objects.create(project=instance, **plan_data)
                        newly_created_floor_plan_ids.add(new_floor_plan.id)
                except Exception as e:
                    import logging
                    logging.error(f"Error creating floor plan: {e}")
                    raise serializers.ValidationError(f"Error creating floor plan: {e}")
        # Only delete floor plans explicitly requested for deletion
        if deleted_floor_plan_ids:
            instance.floor_plans.filter(id__in=deleted_floor_plan_ids).delete()
        

        
        # Handle legal documents - delete removed ones and add new ones
        if existing_legal_documents is not None:
            # Delete legal documents that are not in the existing_legal_documents list
            instance.documents.filter(document_type='Document').exclude(id__in=existing_legal_documents).delete()
        
        # Add new legal documents
        for document_data in uploaded_legal_documents:
            Document.objects.create(project=instance, **document_data)
        
        # Handle marketing documents - delete removed ones and add new ones
        if existing_marketing_documents is not None:
            # Delete marketing documents that are not in the existing_marketing_documents list
            instance.documents.filter(document_type='Marketing Material').exclude(id__in=existing_marketing_documents).delete()
        
        # Add new marketing documents
        for document_data in uploaded_marketing_documents:
            Document.objects.create(project=instance, **document_data)
        
        # Handle contacts (both existing and new)
        existing_contact_ids = set()
        for contact_data in contacts_data:
            contact_id = contact_data.get('id')
            if contact_id:
                # Update existing contact
                try:
                    contact = Contact.objects.get(id=contact_id, project=instance)
                    for attr, value in contact_data.items():
                        if attr != 'id' and hasattr(contact, attr):
                            setattr(contact, attr, value)
                    contact.save()
                    existing_contact_ids.add(contact_id)
                except Contact.DoesNotExist:
                    continue
            else:
                # Create new contact
                contact = Contact.objects.create(project=instance, **contact_data)
                existing_contact_ids.add(contact.id)
        
        # Delete contacts that are no longer in the data
        instance.contacts.exclude(id__in=existing_contact_ids).delete()
        
        # Set amenities
        if amenity_ids is not None:
            instance.amenities.set(amenity_ids)
        
        # Delete removed features & finishes if client sent the list of ones to keep
        if existing_features_finishes is not None:
            instance.features_finishes.exclude(id__in=existing_features_finishes).delete()
        
        # Add newly uploaded features & finishes
        for ff in uploaded_features_finishes:
            FeatureFinish.objects.create(project=instance, **ff)
        
        return instance

# Simplified serializers for list views
class ProjectListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    total_lots = serializers.IntegerField(read_only=True)
    available_lots = serializers.IntegerField(read_only=True)
    total_floor_plans = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'project_type', 'status', 'project_address',
            'city_name', 'price_starting_from', 'price_ending_at',
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
    
    class Meta:
        model = FloorPlan
        fields = '__all__'

class LotListSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    floor_plans_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Lot
        fields = '__all__'
    
    def get_floor_plans_count(self, obj):
        return obj.floor_plans.count()
