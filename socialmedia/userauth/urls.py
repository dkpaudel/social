from django.contrib import admin
from django.urls import path
from socialmedia import settings
from userauth import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home),
    path('loginn/',views.loginn),
    path('signup/',views.signup),
    path('logoutt/',views.logoutt),
    path('upload',views.upload),
    path('like-post/<str:id>', views.likes, name='like-post'),
    path('dislike-post/<str:id>/', views.dislikes, name="dislike-post"), 
    path('#<str:id>', views.home_post),
    path('explore',views.explore),
    path('profile/<str:id_user>', views.profile),
    path('delete/<str:id>', views.delete),
    path('search-results/', views.search_results, name='search_results'),
    path('follow', views.follow, name='follow'),
    path('add-comment/<str:id>', views.add_comment, name='add_comment'), 
    path('fetch-comments/<str:id>/', views.fetch_comments, name='fetch_comments'),
    path('chat/', views.chat_home, name='chat_home'),
    path('chat/<uuid:room_id>/', views.chat_room, name='chat_room'),
    path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
    path('fetch-likes/<str:id>/', views.fetch_likes, name='fetch_liked_users'),
    path('fetch-dislikes/<str:id>/', views.fetch_dislikes, name='fetch_disliked_users'),
    path('fetch-followers/<str:username>/', views.fetch_followers),
    path('fetch-followings/<str:username>/', views.fetch_followings),
 


]
    
  
    

