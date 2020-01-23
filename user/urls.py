from django.urls import path
from django.conf.urls import url
from user import views

app_name = 'user'

urlpatterns = [
    path('profile/', views.EditProfile.as_view(), name='editprofile'),
    path('', views.EditProfile.as_view(), name='user'),
]