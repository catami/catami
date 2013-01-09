from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(r'^accounts/', include('userena.urls')))
