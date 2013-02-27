from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.authentication import Authentication, SessionAuthentication, MultiAuthentication, ApiKeyAuthentication


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = "users"
        authentication = MultiAuthentication(SessionAuthentication(), ApiKeyAuthentication(), Authentication())
        excludes = ['email', 'password', 'is_staff', 'is_superuser', 'is_active', 'last_login']
