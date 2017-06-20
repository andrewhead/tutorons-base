from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^example$', 'tutorons.modules.{{ app_name }}.views.example', name='example'),
    url(r'^scan$', 'tutorons.modules.{{ app_name }}.views.scan', name='scan'),
)
