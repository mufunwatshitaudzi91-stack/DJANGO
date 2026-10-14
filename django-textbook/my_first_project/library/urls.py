from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book-list'),
    path('new/', views.BookCreateView.as_view(), name='book-create'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('<int:pk>/edit/', views.BookUpdateView.as_view(), name='book-update'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book-delete'),
]