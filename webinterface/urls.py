"""URL Mappings for the webinterface application.
"""
from catamidb import authorization
from django.conf.urls import patterns, url, include
from django.conf import settings
from django.contrib.auth import views as auth_views

from django.contrib import admin


from userena import views as userena_views
from userena import settings as userena_settings

admin.autodiscover()

#configure initial auth and groups
authorization.on_startup_configuration()

urlpatterns = patterns(
    'webinterface.views',
    url(r'^$', 'index', name='index'),

    #Info Pages
    url(r'^faq', 'faq'),
    url(r'^contact', 'contact'),
    url(r'^licensing', 'licensing'),
    url(r'^howto', 'howto'),
    url(r'^about', 'about'),
    url(r'^proxy/$', 'proxy'),
    url(r'^classification', 'classification'),
    #url(r'^viewcollection$', 'viewcollection'),

    #Staging
    #url(r'^staging/', include('staging.urls')),
    # campaign creating
    url(r'^staging/campaign/create$', 'campaigncreate', name='staging_campaign_create'),
    url(r'^staging/upload/$', 'data_upload'),


    # Projects
    #url(r'^projects$', 'projects'),
    url(r'^projects/$', 'projects'),
    url(r'^projects/create/$', 'project_create'),
    url(r'^projects/import/$', 'project_import'),
    url(r'^projects/(?P<project_id>\d+)/$', 'project_view'),
    url(r'^projects/(?P<project_id>\d+)/configure/$', 'project_configure'),
    url(r'^projects/(?P<project_id>\d+)/annotate/$', 'project_annotate'),
   

    #plain data views
    url(r'^data/$', 'data'),
    url(r'^data/deployments/$', 'deployment_list'),
    url(r'^data/deployments/(?P<deployment_id>\d+)/$',
        'deployment_view'),
    url(r'^data/campaigns_old/$', 'campaigns'),
    url(r'^data/campaigns/$', 'campaign_list'),
    url(r'^data/campaigns/(?P<campaign_id>\d+)/$',
        'campaign_view'),

    #API docs
    url(r'^api/', include('jsonapi.urls')),

    #dbadmin tool
    #url(r'^report/', include('dbadmintool.urls')),

    # userena profile management
    url(r'^accounts/(?P<username>[\.\w]+)/email/$', userena_views.email_change, {'template_name': 'accounts/email_form.html'}, name='userena_email_change'),
    url(r'^accounts/(?P<username>[\.\w]+)/password/$', userena_views.password_change,  {'template_name': 'accounts/password_reset_form.html'}, name='password_change'),
    url(r'^accounts/(?P<username>[\.\w]+)/password/complete/$', userena_views.direct_to_user_template, {'template_name': 'accounts/password_complete.html'}, name='userena_password_change_complete'),
    url(r'^accounts/(?P<username>[\.\w]+)/edit/$', userena_views.profile_edit,  {'template_name': 'accounts/profile_form.html'}, name='userena_profile_edit'),
    url(r'^accounts/(?P<username>[\.\w-]+)/email/complete/$', userena_views.direct_to_user_template, {'template_name': 'accounts/email_change_complete.html'}, name='userena_email_change_complete'),
    url(r'^accounts/(?P<username>[\.\w-]+)/confirm-email/complete/$', userena_views.direct_to_user_template, {'template_name': 'accounts/email_confirm_complete.html'}, name='userena_email_confirm_complete'),
    url(r'^accounts/(?P<username>[\.\w-]+)/signup/complete/$', userena_views.direct_to_user_template, {'template_name': 'accounts/signup_complete.html', 'extra_context': {'userena_activation_required': userena_settings.USERENA_ACTIVATION_REQUIRED, 'userena_activation_days': userena_settings.USERENA_ACTIVATION_DAYS}}, name='userena_signup_complete'),

    url(r'^accounts/(?P<username>(?!signout|signup|signin)[\.\w]+)/$', userena_views.profile_detail, {'template_name': 'accounts/profile_detail.html'},  name='userena_profile_detail'),

    url(r'^accounts/activate/(?P<activation_key>\w+)/$', userena_views.activate, name='userena_activate'),

    # Disabled account
    url(r'^accounts/(?P<username>[\.\w-]+)/disabled/$',userena_views.direct_to_user_template, {'template_name': 'accounts/disabled.html'}, name='userena_disabled'),

    #userena profile list
    url(r'accounts/$', userena_views.profile_list, {'template_name': 'accounts/profile_list.html'},  name='userena_profile_list'),

    #userena signin/signup
    url(r'^accounts/signup/$', userena_views.signup, {'template_name': 'accounts/signup_form.html'}, name='userena_signup'),
    url(r'^accounts/signin/$', userena_views.signin, {'template_name': 'accounts/signin_form.html'}, name='userena_signin'),
    url(r'^accounts/signout/$', auth_views.logout, {'next_page': userena_settings.USERENA_REDIRECT_ON_SIGNOUT, 'template_name': 'accounts/signout.html'}, name='userena_signout'),
    url(r'^accounts/password/reset/$', auth_views.password_reset, {'template_name': 'accounts/password_reset_form.html', 'email_template_name': 'accounts/emails/password_reset_message.txt'}, name='userena_password_reset'),
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, {'template_name': 'accounts/password_reset_done.html'}, name='userena_password_reset_done'),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm, {'template_name': 'accounts/password_reset_confirm_form.html'}, name='userena_password_reset_confirm'),
    url(r'^accounts/password/reset/confirm/complete/$', auth_views.password_reset_complete, {'template_name': 'accounts/password_reset_complete.html'}),

    # Retry activation
    url(r'^accounts/activate/retry/(?P<activation_key>\w+)/$', userena_views.activate_retry, name='userena_activate_retry'),

    # Change email and confirm it
    url(r'^accounts/confirm-email/(?P<confirmation_key>\w+)/$', userena_views.email_confirm, name='userena_email_confirm'),

    # Disabled account
    url(r'^accounts/(?P<username>[\.\w-]+)/disabled/$', userena_views.direct_to_user_template, {'template_name': 'accounts/disabled.html'}, name='userena_disabled'),

    url(r'^accounts/page/(?P<page>[0-9]+)/$', userena_views.ProfileListView.as_view(), name='userena_profile_list_paginated'),
    url(r'^accounts/$', userena_views.ProfileListView.as_view(), name='userena_profile_list'),

    #userana to catch any un
    url(r'^accounts/', include('userena.urls')), url(r'^logout/$', 'logout_view'),

    #admin interface
    url(r'^admin/', include(admin.site.urls)),

)

urlpatterns += patterns(
    '',
    url(r'images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.IMPORT_PATH, 'show_indexes': True}),
)
