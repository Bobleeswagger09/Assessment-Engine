from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import permissions
from drf_spectacular.utils import extend_schema, OpenApiExample


class CustomAuthToken(ObtainAuthToken):
    permission_classes = []  # No authentication required
    authentication_classes = []  # No authentication required
    
    @extend_schema(
        description="Obtain authentication token by providing username and password",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'testuser'},
                    'password': {'type': 'string', 'example': 'testpass123'}
                },
                'required': ['username', 'password']
            }
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'token': {'type': 'string'},
                    'user_id': {'type': 'integer'},
                    'username': {'type': 'string'},
                    'email': {'type': 'string'}
                }
            }
        },
        examples=[
            OpenApiExample(
                'Login Example',
                value={'username': 'testuser', 'password': 'testpass123'},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        })