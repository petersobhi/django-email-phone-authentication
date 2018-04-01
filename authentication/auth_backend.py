from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class MobilePhoneOrEmailModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # the username could be either one of the two
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'phone__phone_number': username}
        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except User.DoesNotExist:
            return None
