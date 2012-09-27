from django.conf.urls import patterns, include, url
from service import views
import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bugzilla.views.home', name='home'),
    # url(r'^bugzilla/', include('bugzilla.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^test$',views.testView),
    url(r'^(?P<namespace>bug|bugzilla|product|util|user)/(?P<function>[a-zA-Z0-9_\.]{1,})', views.BugzillaConnector(settings.BUGZILLA_XMLRPC)._dispatcher),
)