from django.urls import path

from . import views

app_name = 'platforms'


urlpatterns = [
    path('', views.platform_list, name='platform-list'),
    path('<slug:platform_slug>/', views.platform_detail, name='platform-detail'),
]
