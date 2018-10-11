from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.Homepage, name ='home'),
    url(r'^twitter/stream/', views.twitter_streaming, name ='stream'),
    url(r'^twitter/stream/<str:keyword>/<int:time>/<int:count>', views.twitter_streaming, name ='stream2'),
    url(r'^twitter/filter',views.search_data , name ='filter'),
    url(r'^twitter/export',views.get_csv_export , name ='csv'),
    # url(r'^wine/clear', views.clear_database,name ='clear'),
    # url(r'^wine/details/(?P<id>\w{0,50})', views.details ,name ='details')
]