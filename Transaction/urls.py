from django.urls import path
from . import views

urlpatterns = [
    path("list/", views.TransactionListView.as_view(), name="list"),
    path("home/", views.homepageView.as_view(), name="homepage"),
    
    path("create", views.TransactionCreateView.as_view(), name="create"),
    
    path("detail/<int:pk>/", views.TransactionDetailView.as_view(), name="detail"),
    
    path("edit/<int:pk>/", views.TransactionUpdateView.as_view(), name="edit"),
  
    path("delete/<int:pk>/", views.TransactionDeleteView.as_view(), name="delete"),
    
]
