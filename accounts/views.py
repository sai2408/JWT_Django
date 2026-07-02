import json
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

_ACCESS_LIFETIME = timedelta(minutes=15)
_REFRESH_LIFETIME = timedelta(days=7)


def _make_token(user_id, token_type, lifetime):
    payload = {
        "user_id": user_id,
        "type": token_type,
        "exp": datetime.now(tz=timezone.utc) + lifetime,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def _user_from_bearer(request):
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[7:]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return User.objects.get(id=payload["user_id"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


def _parse_json(request):
    try:
        return json.loads(request.body), None
    except json.JSONDecodeError:
        return None, JsonResponse({"error": "Invalid JSON"}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    data, err = _parse_json(request)
    if err:
        return err

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse({"error": "username and password are required"}, status=400)
    if len(password) < 6:
        return JsonResponse({"error": "password must be at least 6 characters"}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "username already taken"}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    return JsonResponse({"id": user.id, "username": user.username, "email": user.email}, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    data, err = _parse_json(request)
    if err:
        return err

    user = authenticate(request, username=data.get("username"), password=data.get("password"))
    if user is None:
        return JsonResponse({"error": "Invalid credentials"}, status=401)

    return JsonResponse({
        "access": _make_token(user.id, "access", _ACCESS_LIFETIME),
        "refresh": _make_token(user.id, "refresh", _REFRESH_LIFETIME),
    })


@csrf_exempt
@require_http_methods(["POST"])
def refresh_view(request):
    data, err = _parse_json(request)
    if err:
        return err

    try:
        payload = jwt.decode(data.get("refresh", ""), settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError("wrong token type")
    except jwt.ExpiredSignatureError:
        return JsonResponse({"error": "Refresh token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"error": "Invalid refresh token"}, status=401)

    return JsonResponse({"access": _make_token(payload["user_id"], "access", _ACCESS_LIFETIME)})


@require_http_methods(["GET"])
def me_view(request):
    user = _user_from_bearer(request)
    if user is None:
        return JsonResponse({"error": "Unauthorized"}, status=401)
    return JsonResponse({"id": user.id, "username": user.username, "email": user.email})
