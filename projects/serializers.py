from rest_framework import serializers
from .models import (
    State, City, Rendering, SitePlan, Lot, FloorPlan, 
    Document, Project, Contact
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
    
    class Meta:
        model = FloorPlan
        fields = '__all__'
    
    def get_plan_file_url(self, obj):
        if obj.plan_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.plan_file.url)
            return obj.plan_file.url
        return None

class LotSerializer(serializers.ModelSerializer):
    lot_numbers_list = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        source='get_lot_numbers_list'
    )
    lot_rendering_url = serializers.SerializerMethodField()
    floor_plans = FloorPlanSerializer(many=True, read_only=True)
    floor_plan_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=FloorPlan.objects.all(),
        source='floor_plans',
        required=False
    )
    
    class Meta:
        model = Lot
        fields = '__all__'
    
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
        lot_numbers_list = self.context.get('lot_numbers_list', [])
        instance = super().create(validated_data)
        if lot_numbers_list:
            instance.set_lot_numbers_list(lot_numbers_list)
            instance.save()
        return instance
    
    def update(self, instance, validated_data):
        lot_numbers_list = self.context.get('lot_numbers_list', [])
        instance = super().update(instance, validated_data)
        if lot_numbers_list:
            instance.set_lot_numbers_list(lot_numbers_list)
            instance.save()
        return instance

class DocumentSerializer(serializers.ModelSerializer):
    document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = '__all__'
    
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
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects
    renderings = RenderingSerializer(many=True, read_only=True)
    site_plan = SitePlanSerializer(read_only=True)
    lots_data = LotSerializer(many=True, read_only=True, source='lots')
    floor_plans_data = FloorPlanSerializer(many=True, read_only=True, source='floor_plans')
    documents = DocumentSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    
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
    
    # Update fields for handling both existing and new data
    lots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
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
    existing_documents = serializers.ListField(
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
        uploaded_documents = validated_data.pop('uploaded_documents', [])
        
        # Extract new data structure
        lots_data = validated_data.pop('lots', [])
        floor_plans_data = validated_data.pop('floor_plans', [])
        contacts_data = validated_data.pop('contacts', [])
        
        # Ensure city_id is properly set
        if 'city_id' in validated_data:
            validated_data['city_id'] = int(validated_data['city_id'])
        
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
        
        # Create lots with floor plan associations
        for lot_data in lots_data:
            floor_plan_ids = lot_data.pop('floor_plan_ids', [])
            
            # Handle file uploads - extract files from the request
            lot_rendering = lot_data.pop('lot_rendering', None)
            
            try:
                # Convert string numbers to appropriate types (only if not empty)
                if lot_data.get('lot_size') and lot_data['lot_size'].strip():
                    lot_data['lot_size'] = float(lot_data['lot_size'])
                else:
                    lot_data['lot_size'] = None
                if lot_data.get('price') and lot_data['price'].strip():
                    lot_data['price'] = float(lot_data['price'])
                else:
                    lot_data['price'] = None
                
                # Handle lot rendering file
                if lot_rendering:
                    lot_data['lot_rendering'] = lot_rendering
                
                lot = Lot.objects.create(project=project, **lot_data)
                if floor_plan_ids:
                    lot.floor_plans.set(floor_plan_ids)
            except Exception as e:
                import logging
                logging.error(f"Error creating lot: {e}")
                raise serializers.ValidationError(f"Error creating lot: {e}")
        
        # Create documents
        for document_data in uploaded_documents:
            Document.objects.create(project=project, **document_data)
        
        # Create contacts
        for contact_data in contacts_data:
            Contact.objects.create(project=project, **contact_data)
        
        return project

    def update(self, instance, validated_data):
        # Extract data
        uploaded_renderings = validated_data.pop('uploaded_renderings', [])
        uploaded_site_plan = validated_data.pop('uploaded_site_plan', {})
        uploaded_documents = validated_data.pop('uploaded_documents', [])
        existing_images = validated_data.pop('existing_images', [])
        existing_documents = validated_data.pop('existing_documents', [])
        
        # Extract update data (for both existing and new items)
        lots_data = validated_data.pop('lots', [])
        floor_plans_data = validated_data.pop('floor_plans', [])
        contacts_data = validated_data.pop('contacts', [])
        
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
                    
                    new_floor_plan = FloorPlan.objects.create(project=instance, **plan_data)
                    newly_created_floor_plan_ids.add(new_floor_plan.id)
                except Exception as e:
                    import logging
                    logging.error(f"Error creating floor plan: {e}")
                    raise serializers.ValidationError(f"Error creating floor plan: {e}")
        # Merge both sets before deletion
        all_floor_plan_ids_to_keep = existing_floor_plan_ids | newly_created_floor_plan_ids
        instance.floor_plans.exclude(id__in=all_floor_plan_ids_to_keep).delete()
        
        # Handle lots (both existing and new)
        existing_lot_ids = set()
        for lot_data in lots_data:
            lot_id = lot_data.get('id')
            floor_plan_ids = lot_data.pop('floor_plan_ids', [])
            
            # Handle file uploads - extract files from the request
            lot_rendering = lot_data.pop('lot_rendering', None)
            existing_rendering = lot_data.pop('existing_rendering', None)
            
            if lot_id:
                # Update existing lot
                try:
                    lot = Lot.objects.get(id=lot_id, project=instance)
                    for attr, value in lot_data.items():
                        if attr != 'id' and hasattr(lot, attr):
                            # Convert string numbers to appropriate types (only if not empty)
                            if attr in ['lot_size'] and value and str(value).strip():
                                value = float(value)
                            elif attr in ['price'] and value and str(value).strip():
                                value = float(value)
                            elif attr in ['lot_size', 'price'] and (not value or str(value).strip() == ''):
                                value = None
                            setattr(lot, attr, value)
                    
                    # Handle lot rendering file
                    if lot_rendering:
                        lot.lot_rendering = lot_rendering
                    elif existing_rendering:
                        # Keep existing rendering
                        pass
                    
                    lot.save()
                    if floor_plan_ids:
                        lot.floor_plans.set(floor_plan_ids)
                    existing_lot_ids.add(lot_id)
                except Lot.DoesNotExist:
                    continue
            else:
                # Create new lot
                try:
                    # Convert string numbers to appropriate types (only if not empty)
                    if lot_data.get('lot_size') and lot_data['lot_size'].strip():
                        lot_data['lot_size'] = float(lot_data['lot_size'])
                    else:
                        lot_data['lot_size'] = None
                    if lot_data.get('price') and lot_data['price'].strip():
                        lot_data['price'] = float(lot_data['price'])
                    else:
                        lot_data['price'] = None
                    
                    # Handle lot rendering file
                    if lot_rendering:
                        lot_data['lot_rendering'] = lot_rendering
                    
                    lot = Lot.objects.create(project=instance, **lot_data)
                    if floor_plan_ids:
                        lot.floor_plans.set(floor_plan_ids)
                    existing_lot_ids.add(lot.id)
                except Exception as e:
                    import logging
                    logging.error(f"Error creating lot: {e}")
                    raise serializers.ValidationError(f"Error creating lot: {e}")
        
        # Delete lots that are no longer in the data
        instance.lots.exclude(id__in=existing_lot_ids).delete()
        
        # Handle documents - delete removed ones and add new ones
        # If existing_documents is provided, only keep those documents
        if existing_documents is not None:
            # Delete documents that are not in the existing_documents list
            instance.documents.exclude(id__in=existing_documents).delete()
        
        # Add new documents
        for document_data in uploaded_documents:
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
