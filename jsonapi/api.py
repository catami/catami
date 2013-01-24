from django.contrib.auth.models import User
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = "users"
        authentication = BasicAuthentication()
        excludes = ['email', 'password', 'is_staff', 'is_superuser', 'is_active', 'last_login']

