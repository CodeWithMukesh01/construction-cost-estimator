from django.urls import path
from . import views, analytics

urlpatterns = [
    path('estimate/', views.estimate),
    path('estimate/pdf/', views.estimate_pdf),
    path('staff/login/', analytics.StaffLogin.as_view()),
    path('staff/analytics/', analytics.Analytics.as_view()),
]