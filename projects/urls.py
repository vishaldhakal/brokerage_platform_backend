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
    path('public/projects/<slug:slug>/', views.PublicProjectDetailView.as_view(), name='public-project-detail'),
    
    # Project-specific endpoints
    path('projects/<slug:project_slug>/renderings/', views.ProjectRenderingsView.as_view(), name='project-renderings'),
    path('projects/<slug:project_slug>/renderings/create/', views.ProjectRenderingCreateView.as_view(), name='project-rendering-create'),
    path('projects/<slug:project_slug>/renderings/<int:pk>/', views.ProjectRenderingDetailView.as_view(), name='project-rendering-detail'),
    path('projects/<slug:project_slug>/features-finishes/', views.ProjectFeatureFinishesView.as_view(), name='project-features-finishes'),
    path('projects/<slug:project_slug>/features-finishes/create/', views.ProjectFeatureFinishCreateView.as_view(), name='project-feature-finish-create'),
    path('projects/<slug:project_slug>/features-finishes/<int:pk>/', views.ProjectFeatureFinishDetailView.as_view(), name='project-feature-finish-detail'),
    path('projects/<slug:project_slug>/floor-plans/', views.ProjectFloorPlansView.as_view(), name='project-floor-plans'),
    path('projects/<slug:project_slug>/lots/', views.LotListCreateView.as_view(), name='project-lots'),

    path('projects/<slug:project_slug>/documents/', views.ProjectDocumentsView.as_view(), name='project-documents'),
    
    # New separate tab endpoints
    path('projects/<slug:project_slug>/contacts/', views.ProjectContactsView.as_view(), name='project-contacts'),
    path('projects/<slug:project_slug>/contacts/<int:pk>/', views.ContactDetailView.as_view(), name='project-contact-detail'),
    path('projects/<slug:project_slug>/marketing-documents/', views.ProjectMarketingDocumentsView.as_view(), name='project-marketing-documents'),
    path('projects/<slug:project_slug>/marketing-documents/<int:pk>/', views.MarketingDocumentDetailView.as_view(), name='project-marketing-document-detail'),
    path('projects/<slug:project_slug>/legal-documents/', views.ProjectLegalDocumentsView.as_view(), name='project-legal-documents'),
    path('projects/<slug:project_slug>/legal-documents/<int:pk>/', views.LegalDocumentDetailView.as_view(), name='project-legal-document-detail'),
    
    # Project-specific floor plan CRUD endpoints
    path('projects/<slug:project_slug>/floor-plans/create/', views.ProjectFloorPlanCreateView.as_view(), name='project-floor-plan-create'),
    path('projects/<slug:project_slug>/floor-plans/<int:pk>/', views.ProjectFloorPlanDetailView.as_view(), name='project-floor-plan-detail'),
    
    # Rendering endpoints
    path('renderings/', views.RenderingListCreateView.as_view(), name='rendering-list'),
    path('renderings/<int:pk>/', views.RenderingDetailView.as_view(), name='rendering-detail'),
    # Feature & Finish endpoints
    path('features-finishes/', views.FeatureFinishListCreateView.as_view(), name='feature-finish-list'),
    path('features-finishes/<int:pk>/', views.FeatureFinishDetailView.as_view(), name='feature-finish-detail'),
    
    # Site Plan endpoints
    path('site-plans/', views.SitePlanListCreateView.as_view(), name='site-plan-list'),
    path('site-plans/<int:pk>/', views.SitePlanDetailView.as_view(), name='site-plan-detail'),
    
    # Lot endpoints
    path('lots/', views.LotListCreateView.as_view(), name='lot-list'),
    path('lots/<int:pk>/', views.LotDetailView.as_view(), name='lot-detail'),
    
    # Project-specific lot endpoints
    path('projects/<slug:project_slug>/lots/<int:id>/', views.LotDetailView.as_view(), name='project-lot-detail'),
    
    # Project-specific inquiries
    path('projects/<slug:project_slug>/inquiries/', views.ProjectInquiriesView.as_view(), name='project-inquiries'),
    path('projects/<slug:project_slug>/inquiries/<int:pk>/', views.ProjectInquiryDetailProjectScopedView.as_view(), name='project-inquiry-detail-project'),
    
    # Floor Plan endpoints
    path('floor-plans/', views.FloorPlanListCreateView.as_view(), name='floor-plan-list'),
    path('floor-plans/<int:pk>/', views.FloorPlanDetailView.as_view(), name='floor-plan-detail'),
    
    # Document endpoints
    path('documents/', views.DocumentListCreateView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    
    # Amenity endpoints
    path('amenities/', views.AmenityListCreateView.as_view(), name='amenity-list'),
    path('amenities/<int:pk>/', views.AmenityDetailView.as_view(), name='amenity-detail'),

    # Project Inquiry endpoints
    path('inquiries/', views.ProjectInquiryListCreateView.as_view(), name='project-inquiry-list'),
    path('inquiries/<int:pk>/', views.ProjectInquiryDetailView.as_view(), name='project-inquiry-detail'),
]
