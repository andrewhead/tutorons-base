from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^$', 'tutorons.home.views.home', name='home'),
    url(r'^home$', 'tutorons.home.views.home', name='home'),
)
