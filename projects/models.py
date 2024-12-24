from django.db import models
from django.utils.text import slugify

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

class BuilderDetails(SlugMixin, models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    website = models.URLField(blank=True)
    logo = models.FileField(blank=True)
    company_name = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    details = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Developer(SlugMixin, models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    details = models.TextField(blank=True)
    logo = models.FileField(upload_to='developer_logos/', blank=True)

    def __str__(self):
        return self.name

class State(SlugMixin, models.Model):
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=2)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class City(SlugMixin, models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Image(models.Model):
    image = models.FileField(upload_to='images/')

    def __str__(self):
        return str(self.image)

    
class Plan(models.Model):
    AVAILABILITY_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Unavailable', 'Unavailable'),
    ]
    plan_type = models.CharField(max_length=100)
    plan_name = models.CharField(max_length=100)
    plan = models.FileField()
    availability_status = models.CharField(max_length=50, choices=AVAILABILITY_STATUS_CHOICES,default='Available')

    def __str__(self):
        return self.plan_name
    
class Document(models.Model):
    title = models.CharField(max_length=200)
    document = models.FileField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        ordering = ['-created_at']

class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()

    def __str__(self):
        return self.question

    
class Project(SlugMixin, models.Model):
    PROJECT_TYPE_CHOICES = [
        ('Single Family', 'Single Family'),
        ('Multi Family', 'Multi Family'),
        ('Condominium', 'Condominium'),
        ('Townhouse', 'Townhouse'),
        ('Move in Ready', 'Move in Ready'),
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
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    project_type = models.CharField(max_length=100, choices=PROJECT_TYPE_CHOICES,default='Single Family')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES,default='Planning')
    project_address = models.CharField(max_length=200)
    price_starting_from = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price_ending_at = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    project_description = models.TextField(blank=True)
    project_video_url = models.URLField(blank=True)
    area_square_footage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    lot_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    garage_spaces = models.IntegerField(blank=True, null=True)
    plans = models.ManyToManyField(Plan, blank=True)
    images = models.ManyToManyField(Image, blank=True)
    documents = models.ManyToManyField(Document, blank=True)
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, blank=True, null=True)
    developer = models.ForeignKey(Developer, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Testimonial(models.Model):
    SOURCE_CHOICES = [
        ('Google', 'Google'),
        ('Facebook', 'Facebook'),
        ('Yelp', 'Yelp'),
        ('Zillow', 'Zillow'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=100)
    testimonial = models.TextField()
    image = models.FileField()
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES,default='Other')

    def __str__(self):
        return self.name