from django.urls import path

from . import views

app_name = 'games'


urlpatterns = [
    path('', views.game_list, name='game-list'),
    path('<slug:game_slug>/', views.game_detail, name='game-detail'),
    path('<slug:game_slug>/reviews/', views.review_list, name='review-list'),
    # path('add/', views.add_post, name='add-post'),
]
