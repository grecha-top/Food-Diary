from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('admin/allergen/add', views.admin_create_allergen, name='admin_create_allergen'),
    path('my/allergen/add', views.user_create_allergen, name='user_create_allergen')
]