from django.utils.translation import ugettext_lazy as _

from rest_framework import status, exceptions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_auth.views import LoginView, APIView
from rest_auth.registration.views import RegisterView

from .serializers import VerifyPhoneSerializer
from .models import PhoneNumber


@api_view()
def django_rest_auth_null(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginView(LoginView):
    queryset = ''


class RegisterView(RegisterView):
    queryset = ''

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        response_data = ''
        email = request.data.get('email', None)
        phone_number = request.data.get('phone_number', None)
        if email and phone_number:
            response_data = {"detail": _("Verification e-mail and SMS sent.")}
        elif email and not phone_number:
            response_data = {"detail": _("Verification e-mail sent.")}
        else:
            response_data = {"detail": _("Verification SMS sent.")}

        return Response(response_data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class VerifyPhoneView(APIView):
    serializer_class = VerifyPhoneSerializer

    def post(self, request):
        serializer = VerifyPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.data.get('phone_number')
        passcode = serializer.data.get('passcode')
        phone = PhoneNumber.objects.get(phone_number=phone_number)
        if phone.passcode == passcode:
            phone.verfied = True
            phone.save()
            return Response(
                {"detail": _("Phone number has been verified.")},
                status=status.HTTP_200_OK
            )
        else:
            raise exceptions.ValidationError("Wrong or expired passcode")
