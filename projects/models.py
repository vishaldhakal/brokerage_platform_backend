from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

class SlugMixin:
    def generate_unique_slug(self):
        if not self.name:  # Skip if name is not set
            return
            
        base_slug = slugify(self.name)
        slug = base_slug
        counter = 1
        model = self.__class__
        while model.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it's not set
            self.generate_unique_slug()
        super().save(*args, **kwargs)

class State(SlugMixin, models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = "States"

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"
    
class City(SlugMixin, models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['state__name', 'name']
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name}, {self.state.abbreviation}"

class Rendering(models.Model):
    title = models.CharField(max_length=200, help_text="e.g., Kitchen, Living Room, Exterior")
    image = models.FileField(upload_to='renderings/')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='renderings')

    class Meta:
        ordering = ['title']
        verbose_name_plural = "Renderings"

    def __str__(self):
        return f"{self.title} - {self.project.name}"

class SitePlan(models.Model):
    project = models.OneToOneField('Project', on_delete=models.CASCADE, related_name='site_plan')
    file = models.FileField(upload_to='site_plans/', blank=True, null=True, help_text="Site plan file (PDF or image)")

    class Meta:
        verbose_name_plural = "Site Plans"

    def __str__(self):
        return f"Site Plan - {self.project.name}"

class FloorPlan(models.Model):
    HOUSE_TYPE_CHOICES = [
        ('Single Family', 'Single Family'),
        ('Townhouse', 'Townhouse'),
        ('Duplex', 'Duplex'),
        ('Triplex', 'Triplex'),
        ('Condo', 'Condo'),
        ('Custom', 'Custom'),
    ]
    
    AVAILABILITY_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Sold', 'Sold'),
        ('Coming Soon', 'Coming Soon'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='floor_plans')
    name = models.CharField(max_length=200, help_text="Name of the floor plan", blank=True, null=True)
    house_type = models.CharField(max_length=50, choices=HOUSE_TYPE_CHOICES, default='Single Family')
    square_footage = models.PositiveIntegerField(help_text="Total square footage", blank=True, null=True)
    bedrooms = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], blank=True, null=True)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(0), MaxValueValidator(20)], blank=True, null=True)
    garage_spaces = models.PositiveIntegerField(default=0, help_text="Number of garage spaces", blank=True, null=True)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS_CHOICES, default='Available')
    plan_file = models.FileField(upload_to='floor_plans/', blank=True, null=True, help_text="Floor plan file (PDF or image)")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Floor Plans"

    def __str__(self):
        return f"{self.name} - {self.project.name}"

class Lot(models.Model):
    AVAILABILITY_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Reserved', 'Reserved'),
        ('Sold', 'Sold'),
        ('Coming Soon', 'Coming Soon'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='lots')
    lot_number = models.CharField(max_length=50, help_text="e.g., 112, 12A, 15B")
    lot_numbers = models.TextField(blank=True, help_text="Comma-separated lot numbers (e.g., 1,2,3,4,5)")
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS_CHOICES, default='Available')
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Lot size in square feet")
    price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    est_completion = models.CharField(max_length=100, blank=True, help_text="Estimated completion (e.g., 'Spring 2024', 'Q2 2024')")
    description = models.TextField(blank=True)
    lot_rendering = models.FileField(upload_to='lot_renderings/', blank=True, help_text="Rendering image for this specific lot")
    floor_plans = models.ManyToManyField(FloorPlan, blank=True, help_text="Available floor plans for this lot")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'lot_number']
        verbose_name_plural = "Lots"

    def __str__(self):
        return f"Lot {self.lot_number} - {self.project.name}"
    
    def get_lot_numbers_list(self):
        """Return list of lot numbers from comma-separated field"""
        if self.lot_numbers:
            return [num.strip() for num in self.lot_numbers.split(',') if num.strip()]
        return [self.lot_number] if self.lot_number else []
    
    def set_lot_numbers_list(self, lot_numbers_list):
        """Set lot numbers from a list"""
        if lot_numbers_list:
            self.lot_numbers = ','.join(str(num).strip() for num in lot_numbers_list)
        else:
            self.lot_numbers = ''

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('Brochure', 'Brochure'),
        ('Fact Sheet', 'Fact Sheet'),
        ('Floor Plan', 'Floor Plan'),
        ('Site Plan', 'Site Plan'),
        ('Contract', 'Contract'),
        ('Disclosure', 'Disclosure'),
        ('Permit', 'Permit'),
        ('Other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES, default='Other')
    document = models.FileField(upload_to='documents/')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='documents', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.title} ({self.document_type})"

class Amenity(models.Model):
    CATEGORY_CHOICES = [
        ('Recreation', 'Recreation'),
        ('Fitness', 'Fitness'),
        ('Community', 'Community'),
        ('Security', 'Security'),
        ('Transportation', 'Transportation'),
        ('Lifestyle', 'Lifestyle'),
        ('Technology', 'Technology'),
        ('Environment', 'Environment'),
        ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name or emoji")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name_plural = "Amenities"
    
    def __str__(self):
        return self.name

class Project(SlugMixin, models.Model):
    PROJECT_TYPE_CHOICES = [
        ('Single Family', 'Single Family'),
        ('Multi Family', 'Multi Family'),
        ('Condominium', 'Condominium'),
        ('Townhouse', 'Townhouse'),
        ('Move in Ready', 'Move in Ready'),
        ('Custom Build', 'Custom Build'),
        ('Other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('Planning', 'Planning Phase'),
        ('Approval', 'Approval Process'),
        ('Sales', 'Sales Phase'),
        ('Construction', 'Construction Phase'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    project_type = models.CharField(max_length=100, choices=PROJECT_TYPE_CHOICES, default='Single Family')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Planning')
    project_address = models.CharField(max_length=500)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='projects')
    
    # Description
    project_description = models.TextField(blank=True)
    project_video_url = models.URLField(blank=True)
    
    # Pricing
    price_starting_from = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_ending_at = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    pricing_details = models.TextField(blank=True, help_text="Rich text field for detailed pricing information")
    
    # Property Details
    # Removed area_square_footage, lot_size, garage_spaces, bedrooms, bathrooms as they are now handled at lot/floor plan level
    
    # Financial Information
    deposit_structure = models.TextField(blank=True, help_text="Rich text field for deposit structure details")
    commission = models.TextField(blank=True, help_text="Rich text field for commission information")
    
    # Timeline Information
    occupancy = models.TextField(blank=True, help_text="Occupancy timeline and details")
    aps = models.TextField(blank=True, help_text="APS (Agreement of Purchase and Sale) details")
    
    # Amenities
    amenities = models.ManyToManyField(Amenity, blank=True, help_text="Available amenities for this project")
    
    # Meta Information
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']  # Last updated on top (newest first)
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.name

    @property
    def total_lots(self):
        return self.lots.count()

    @property
    def available_lots(self):
        return self.lots.filter(availability_status='Available').count()

    @property
    def total_floor_plans(self):
        return self.floor_plans.count()


class Contact(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Contacts"
    
    def __str__(self):
        return f"{self.name} - {self.project.name}"