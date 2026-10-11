from django.urls import path
from . import views

urlpatterns = [
    path('companies/', views.CompanyList.as_view()),
    path('quote-requests/', views.QuoteRequestCreate.as_view()),
    path('company/register/', views.CompanyRegister.as_view()),
    path('company/login/', views.CompanyLogin.as_view()),
    path('company/requests/', views.MyQuoteRequests.as_view()),
    path('company/requests/<int:pk>/', views.MyQuoteRequestUpdate.as_view()),
    path('quote-requests/bulk/', views.BulkQuoteRequestCreate.as_view()),
    path('compare/', views.CompareQuotes.as_view()),
]