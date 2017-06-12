from django.conf.urls import patterns, include, url
from tastypie.api import Api
from tutorons.core.api import ClientQueryResource, ViewResource

v1_api = Api(api_name='v1')
v1_api.register(ClientQueryResource())
v1_api.register(ViewResource())

urlpatterns = patterns(
    '',
    url(r'^(home)?$', include('tutorons.home.urls')),
    url(r'^api/', include(v1_api.urls)),
    # Add reference to each Tutoron's URLs below this line:
    url(r'^python_builtins$', 'tutorons.modules.python_builtins.views.scan', name='python_builtins'),
    url(r'^python_builtins/', include('tutorons.modules.python_builtins.urls', namespace='python_builtins')),
)
