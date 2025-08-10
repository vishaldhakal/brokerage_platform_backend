from django.core.management.base import BaseCommand
from projects.models import Amenity


class Command(BaseCommand):
    help = 'Create sample amenities for testing'

    def handle(self, *args, **options):
        amenities_data = [
            # Recreation
            {'name': 'Swimming Pool', 'category': 'Recreation', 'icon': '🏊‍♂️', 'description': 'Indoor/outdoor swimming pool'},
            {'name': 'Playground', 'category': 'Recreation', 'icon': '🏞️', 'description': 'Children playground area'},
            {'name': 'Tennis Court', 'category': 'Recreation', 'icon': '🎾', 'description': 'Professional tennis court'},
            {'name': 'Basketball Court', 'category': 'Recreation', 'icon': '🏀', 'description': 'Basketball court'},
            {'name': 'Game Room', 'category': 'Recreation', 'icon': '🎮', 'description': 'Indoor game room'},
            
            # Fitness
            {'name': 'Fitness Center', 'category': 'Fitness', 'icon': '🏋️‍♂️', 'description': 'Fully equipped gym'},
            {'name': 'Yoga Studio', 'category': 'Fitness', 'icon': '🧘‍♀️', 'description': 'Dedicated yoga and meditation space'},
            {'name': 'Jogging Trail', 'category': 'Fitness', 'icon': '🏃‍♂️', 'description': 'Scenic jogging trail'},
            
            # Community
            {'name': 'Community Center', 'category': 'Community', 'icon': '🏢', 'description': 'Multi-purpose community center'},
            {'name': 'BBQ Area', 'category': 'Community', 'icon': '🔥', 'description': 'Outdoor BBQ and picnic area'},
            {'name': 'Event Hall', 'category': 'Community', 'icon': '🎉', 'description': 'Hall for community events'},
            {'name': 'Library', 'category': 'Community', 'icon': '📚', 'description': 'Community library'},
            
            # Security
            {'name': '24/7 Security', 'category': 'Security', 'icon': '🔐', 'description': '24/7 security service'},
            {'name': 'Gated Community', 'category': 'Security', 'icon': '🚪', 'description': 'Gated and secure community'},
            {'name': 'CCTV Surveillance', 'category': 'Security', 'icon': '📹', 'description': 'CCTV monitoring system'},
            
            # Transportation
            {'name': 'Parking Garage', 'category': 'Transportation', 'icon': '🚗', 'description': 'Covered parking garage'},
            {'name': 'Electric Car Charging', 'category': 'Transportation', 'icon': '🔌', 'description': 'EV charging stations'},
            {'name': 'Public Transit Access', 'category': 'Transportation', 'icon': '🚌', 'description': 'Close to public transportation'},
            
            # Lifestyle
            {'name': 'Spa', 'category': 'Lifestyle', 'icon': '💆‍♀️', 'description': 'Full-service spa'},
            {'name': 'Concierge', 'category': 'Lifestyle', 'icon': '🛎️', 'description': '24/7 concierge service'},
            {'name': 'Pet Park', 'category': 'Lifestyle', 'icon': '🐕', 'description': 'Dedicated pet exercise area'},
            {'name': 'Gardens', 'category': 'Lifestyle', 'icon': '🌸', 'description': 'Beautiful landscaped gardens'},
            
            # Technology
            {'name': 'High-Speed Internet', 'category': 'Technology', 'icon': '💻', 'description': 'Fiber optic internet'},
            {'name': 'Smart Home Ready', 'category': 'Technology', 'icon': '🏠', 'description': 'Smart home technology ready'},
            
            # Environment
            {'name': 'Green Building', 'category': 'Environment', 'icon': '🌱', 'description': 'LEED certified green building'},
            {'name': 'Solar Panels', 'category': 'Environment', 'icon': '☀️', 'description': 'Solar energy system'},
        ]
        
        created_count = 0
        for amenity_data in amenities_data:
            amenity, created = Amenity.objects.get_or_create(
                name=amenity_data['name'],
                defaults=amenity_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created amenity: {amenity.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Amenity already exists: {amenity.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new amenities')
        )
