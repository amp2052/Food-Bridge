from django.urls import path
from . import views

urlpatterns=[
  path('', views.landing_page, name='home'), 
  path('register/',views.register,name='register'),
  path('verify_otp/',views.verify_otp,name='verify_otp'),
  path('login/',views.login_view,name='login'),
  path('logout/',views.logout_view,name='logout'),
  path('dashboard/',views.dashboard,name='dashboard'),
  path('forgot_password/',views.forgot_password,name='forgot_password'),
  path('verify_forgot_otp/',views.verify_forgot_otp,name='verify_forgot_otp'),
  path('dashboard/donor/', views.donor_dashboard, name='donor_dashboard'),
  path('dashboard/ngo/', views.ngo_dashboard, name='ngo_dashboard'),
  path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
  path('admin/user_management/', views.user_management, name='user_management'),
  path('admin/system_stats/', views.system_stats, name='system_stats'),
  path('admin/audit_logs/', views.audit_logs, name='audit_logs'),
  path('about_us/', views.about_us, name='about_us'),
    path('contact/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy, name='privacy'),
      path('ngo/history/', views.ngo_history, name='ngo_history'),
    path('admin-dashboard/pdf-report/', views.admin_pdf_report, name='admin_pdf_report'),


  path('dashboard/donor/post_donation/', views.post_donation, name='post_donation'),
  path('claim_donation/<int:donation_id>/', views.claim_donation, name='claim_donation'),
  path('profile/', views.donor_profile, name='donor_profile'),
  path('ngo/profile/', views.ngo_profile, name='ngo_profile'),
  path('ngo/create-profile/', views.create_ngo_profile, name='create_ngo_profile'),
  path('ngo/profile/edit/', views.edit_ngo_profile, name='edit_ngo_profile'),
  
   path('admin_dashboards/', views.dashboard, name='admin_dashboard'),
    # path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard_admin/food-posts/', views.all_food_posts, name='all_food_posts'),
    path('dashboard_admin/deliveries/', views.all_deliveries, name='all_deliveries'),
    # path('dashboard_admin/donations/', views.all_donations, name='all_donations'),
]