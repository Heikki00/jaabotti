from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^player/$', views.player),
    url(r'^login/([A-Za-z1-9]+)$', views.login)
]
