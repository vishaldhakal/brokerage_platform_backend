from django.urls import path
from . import views

urlpatterns = [
    path('states/', views.StateListCreateView.as_view(), name='state-list'),
    path('states/<slug:slug>/', views.StateDetailView.as_view(), name='state-detail'),
    
    path('cities/', views.CityListCreateView.as_view(), name='city-list'),
    path('cities/<slug:slug>/', views.CityDetailView.as_view(), name='city-detail'),
    
    path('builder-details/', views.BuilderDetailsListCreateView.as_view(), name='builder-details-list'),
    path('builder-details/<slug:slug>/', views.BuilderDetailsDetailView.as_view(), name='builder-details-detail'),
    
    path('communities/', views.CommunityListCreateView.as_view(), name='community-list'),
    path('communities/<slug:slug>/', views.CommunityDetailView.as_view(), name='community-detail'),
    
    path('projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),
    
    path('images/', views.ImageListCreateView.as_view(), name='image-list'),
    path('images/<int:pk>/', views.ImageDetailView.as_view(), name='image-detail'),

    path('documents/', views.DocumentListCreateView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    
    path('plans/', views.PlanListCreateView.as_view(), name='plan-list'),
    path('plans/<int:pk>/', views.PlanDetailView.as_view(), name='plan-detail'),
    
    path('testimonials/', views.TestimonialListCreateView.as_view(), name='testimonial-list'),
    path('testimonials/<int:pk>/', views.TestimonialDetailView.as_view(), name='testimonial-detail'),
]
