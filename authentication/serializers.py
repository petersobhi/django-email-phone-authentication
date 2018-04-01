import random

from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _


from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator

from phonenumber_field.serializerfields import PhoneNumberField

from .models import PhoneNumber
from .utils import send_verification_sms


from rest_framework import serializers, exceptions

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    # username = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_phone_email(self, phone_number, email, password):
        user = None

        if email and password:
            user = authenticate(username=email, password=password)
        elif phone_number and password:
            user = authenticate(username=phone_number, password=password)
        else:
            msg = _('Must include either "phone_number" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        user = self._validate_phone_email(phone_number, email, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        if email:  # If email, is the email verified?
            email_address = user.emailaddress_set.get(email=user.email)
            if not email_address.verified:
                raise serializers.ValidationError(_('E-mail is not verified.'))

        else:  # If phone number, is the phone number verified?

            if not user.phone.verified:
                raise serializers.ValidationError(_('Phone number is not verified.'))

        attrs['user'] = user
        return attrs


class RegisterSerializer(RegisterSerializer):
    username = None
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    phone_number = PhoneNumberField(required=False, write_only=True,
                                    validators=[UniqueValidator(queryset=PhoneNumber.objects.all())])

    def validate(self, data):
        email = data.get('email', None)
        phone_number = data.get('phone_number', None)
        if not (email or phone_number):
            raise serializers.ValidationError("Enter an email or a phone number.")

        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_cleaned_data_extra(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
        }

    def add_extra_info(self, user, validated_data):
        user.first_name = validated_data.get("first_name")
        user.last_name = validated_data.get("last_name")
        user.save()

    def create_phone(self, user, validated_data):
        phone_number = validated_data.get("phone_number")
        if phone_number:
            PhoneNumber.objects.create(user=user, phone_number=phone_number)
            pl = random.sample([1, 2, 3, 4, 5, 6, 7, 8, 9, 0], 4)
            passcode = ''.join(str(p) for p in pl)
            user.phone.passcode = passcode
            user.phone.save()
            send_verification_sms(phone_number, passcode)

    def custom_signup(self, request, user):
        self.add_extra_info(user, self.get_cleaned_data_extra())
        self.create_phone(user, self.get_cleaned_data_extra())


class VerifyPhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    passcode = serializers.CharField(max_length=4, required=True)

    def validate_phone_number(self, phone_number):
        try:
            user = User.objects.get(phone__phone_number=phone_number)
        except User.DoesNotExist:
            raise exceptions.ValidationError("Wrong phone number")
        return phone_number
