from django.urls import path
from . import views
app_name = 'hello_world' # This is for namespacing; we'll discuss it later.
urlpatterns = [
path('', views.hello_world, name='hello_world'),
]