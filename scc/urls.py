from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.registration, name='reg'),
    path('login/', views.login, name='log'),
    path('logout/', views.logout, name='logout'),
    path('contact/', views.contact, name='cont'),
    path('privacy/', views.privacy, name='priv'),
    path('admi/', views.admi, name='admi'),
    path('admindash/', views.admindash, name='admindash'),
    path('userdash/', views.userdash, name='userdash'),
    path('profile/', views.profile, name='profile'),
    path('user_profiles_list/', views.user_profiles_list, name='user_profiles_list'),
    path('predict/', views.predict, name='predict'),
    path('contact_view/', views.contact_view, name='contact_view'),
    path('contact_list/', views.contact_list, name='contact_list'),
    path('disease-view/', views.disease_view, name='disease_view'),
    path('download-pdf/', views.download_pdf_view, name='download_pdf'),
]