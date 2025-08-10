from django.urls import path
from . import views

urlpatterns = [
    # State endpoints
    path('states/', views.StateListCreateView.as_view(), name='state-list'),
    path('states/<slug:slug>/', views.StateDetailView.as_view(), name='state-detail'),
    
    # City endpoints
    path('cities/', views.CityListCreateView.as_view(), name='city-list'),
    path('cities/<slug:slug>/', views.CityDetailView.as_view(), name='city-detail'),
    path('cities/<slug:city_slug>/projects/', views.CityProjectsView.as_view(), name='city-projects'),
    
    # Project endpoints
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('projects/featured/', views.FeaturedProjectsView.as_view(), name='featured-projects'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    # Project-specific endpoints
    path('projects/<slug:project_slug>/renderings/', views.ProjectRenderingsView.as_view(), name='project-renderings'),
    path('projects/<slug:project_slug>/floor-plans/', views.ProjectFloorPlansView.as_view(), name='project-floor-plans'),
    path('projects/<slug:project_slug>/lots/', views.ProjectLotsView.as_view(), name='project-lots'),
    path('projects/<slug:project_slug>/documents/', views.ProjectDocumentsView.as_view(), name='project-documents'),
    
    # Rendering endpoints
    path('renderings/', views.RenderingListCreateView.as_view(), name='rendering-list'),
    path('renderings/<int:pk>/', views.RenderingDetailView.as_view(), name='rendering-detail'),
    
    # Site Plan endpoints
    path('site-plans/', views.SitePlanListCreateView.as_view(), name='site-plan-list'),
    path('site-plans/<int:pk>/', views.SitePlanDetailView.as_view(), name='site-plan-detail'),
    
    # Lot endpoints
    path('lots/', views.LotListCreateView.as_view(), name='lot-list'),
    path('lots/<int:pk>/', views.LotDetailView.as_view(), name='lot-detail'),
    
    # Floor Plan endpoints
    path('floor-plans/', views.FloorPlanListCreateView.as_view(), name='floor-plan-list'),
    path('floor-plans/<int:pk>/', views.FloorPlanDetailView.as_view(), name='floor-plan-detail'),
    
    # Document endpoints
    path('documents/', views.DocumentListCreateView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    
    # Amenity endpoints
    path('amenities/', views.AmenityListCreateView.as_view(), name='amenity-list'),
    path('amenities/<int:pk>/', views.AmenityDetailView.as_view(), name='amenity-detail'),
]
