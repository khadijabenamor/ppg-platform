from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
import json

User = get_user_model()

def get_user_from_token(request):
    """Extract user from JWT token in Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        access_token = AccessToken(token)
        user_id = access_token.get('user_id')
        return User.objects.get(id=user_id)
    except Exception:
        return None

@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        password2 = data.get('password2', '')
        email = data.get('email', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        role = data.get('role', 'etudiant')

        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)

        if password != password2:
            return JsonResponse({'error': 'Les mots de passe ne correspondent pas'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Ce nom d\'utilisateur existe déjà'}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        from django.contrib.auth import authenticate
        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse({'error': 'Identifiants incorrects'}, status=401)

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': 'etudiant',
                'is_premium': False
            }
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def logout(request):
    return JsonResponse({'message': 'Logged out'})

def profile(request):
    user = get_user_from_token(request)
    if not user:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'is_premium': getattr(user, 'profile.is_premium', False) if hasattr(user, 'profile') else False
    })