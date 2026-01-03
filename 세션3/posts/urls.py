from django.urls import path
from . import views

app_name = "posts"

urlpatterns = [
	    # path('', views.hello_world, name='hello'),
        path('', views.posts_list, name='posts_list'),
        path('<int:pk>/', views.posts_read, name='read'),
        path('create/', views.posts_create, name='create'),
        path('<int:pk>/delete/', views.posts_delete, name='delete'),
        path('<int:pk>/update/', views.post_update, name='update'),
        
]

             