from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.resources import ModelResource
from tastypie.authentication import Authentication, SessionAuthentication, MultiAuthentication, ApiKeyAuthentication, BasicAuthentication


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = "users"
        authentication = MultiAuthentication(BasicAuthentication(),
                                             SessionAuthentication(),
                                             ApiKeyAuthentication())
        filtering = {
            'username': ALL,
            'first_name': ALL,
            'last_name': ALL
        }

        excludes = ['email', 'password', 'is_staff', 'is_superuser',
                    'is_active', 'last_login']