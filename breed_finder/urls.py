from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'breed_finder'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('api/ollama/', views.ollama_proxy, name='ollama_proxy'),  # This URL is accessed as /api/ollama/
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='breed_finder/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='breed_finder:login'), name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    
    # Password reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='breed_finder/password_reset.html',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='breed_finder/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='breed_finder/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='breed_finder/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # User profile URLs
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Pet management URLs
    path('pets/', views.pet_list, name='pet_list'),
    path('pets/add/', views.add_pet, name='add_pet'),
    path('pets/<int:pet_id>/', views.pet_detail, name='pet_detail'),
    path('pets/<int:pet_id>/edit/', views.edit_pet, name='edit_pet'),
    path('pets/<int:pet_id>/delete/', views.delete_pet, name='delete_pet'),
]