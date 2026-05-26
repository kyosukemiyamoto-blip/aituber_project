from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/generate-comment/", views.generate_comment_api, name="generate_comment_api"),
    path("api/reply-to-comment/", views.reply_to_comment_api, name="reply_to_comment_api"),
    path("api/self-introduction/",views.self_introduction_api, name="self_introduction_api"),
    path("api/news-talk/",views.news_talk_api,name= "news_talk_api"),
    path("api/weather-talk/",views.weather_talk_api,name= "weather_talk_api"),
    path("api/user-comment/", views.user_comment_api, name="user_comment_api"),
]