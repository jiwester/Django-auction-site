from django.urls import path, re_path
from . import views

app_name = 'auction'
urlpatterns = [
    path('search/', views.SearchAuctions.as_view(), name='search'),
    path('<int:auction_id>/', views.viewauction, name='id'),
    path('create/', views.CreateAuction.as_view(), name='create'),
    re_path(r'^edit/$', views.EditAuction.as_view(),name='edit'),
    re_path(r'^edit/(?P<auction_id>[0-9]+)/$', views.EditAuction.as_view(),),
    re_path(r'^edit/(?P<auction_id>[0-9]+)/(?P<link>[^/]+)/$', views.editAuctionByLink.as_view()),
    re_path(r'^bid/(?P<item_id>\w+)/$', views.bid, name='bid'),
    re_path(r'^ban/(?P<item_id>\w+)/$', views.ban, name='ban'),
    path('resolve/', views.resolve, name='resolve'),
    path('confirmauction/', views.confirmauction, name='confirm'),
    path('', views.index, name='index'),
]
