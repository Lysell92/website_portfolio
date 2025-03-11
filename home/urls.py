from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('cv/', views.cv_view, name='cv'),
    path('experience/', views.experience_view, name='experience'),
    path('contact/', views.contact_view, name='contact'),
]