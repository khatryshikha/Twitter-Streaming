from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.Homepage, name ='home'),
    url(r'^stream', views.twitter_streaming, name ='stream'),
    # url(r'^search',views.searchdate , name ='search'),
    # url(r'^wine/clear', views.clear_database,name ='clear'),
    # url(r'^wine/details/(?P<id>\w{0,50})', views.details ,name ='details')
]