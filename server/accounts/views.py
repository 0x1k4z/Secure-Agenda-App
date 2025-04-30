from django.shortcuts import render
from django.contrib.auth import authenticate
from . import models
from django.views.decorators.csrf import ensure_csrf_cookie
import random, string
import rsa

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .tokens import createJwtUser

from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


# Create your views here.
# request -> response
@api_view(["POST"])
@permission_classes((AllowAny,))
def register(request):
        if not models.UserDisplayName.objects.filter(displayName=request.POST["displayname"]).exists(): # if display name doesn't exist.
            if not models.CustomUser.objects.filter(username = request.POST["username"]).exists():  # if username doesn't exist.
                userDisplayName = models.UserDisplayName(displayName=request.POST["displayname"])
                user = models.CustomUser.objects.create_user(username=request.POST["username"], displayname=userDisplayName,
                                                             private_key=request.POST["private_key"], public_key=request.POST["public_key"],
                                                             tag=request.POST["tag"],
                                                             nonce=request.POST["nonce"])
                userDisplayName.save()  # adds new display name in table.
                user.save()
                return Response("User added successfully", status=201) # 201 status code means the request succeeded and a new resource was created.
            else:
                return Response("Username already exists", status=409) # 409 status code for conflict.
        else:
            return Response("Display name already exists", status=409) # 409 status code for conflict.

@ensure_csrf_cookie
@api_view(["POST", "GET"])
@permission_classes((AllowAny,))
def challenge(request):
    try:
        if (request.method == 'POST'):
            username = request.POST["username"]
            user = models.CustomUser.objects.filter(username=username)[0]
            if user is not None:
                challenge = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(10))
                user.challenge = challenge
                user.save()
                return Response({"challenge": challenge, "public_key": user.public_key, "private_key": user.private_key,
                                 "tag": user.tag, "nonce": user.nonce}, status=200)
            else:
                return Response("Unknown username", status=401)
        return Response("Challenge")
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    try:
        if (request.method == 'POST'):
            username = request.POST["username"]
            signed_challenge = request.POST["signed_challenge"]
            user = models.CustomUser.objects.filter(username=username)[0]
            publicKey = load_pem_public_key(user.public_key)
            if user is not None and publicKey.verify(signed_challenge, user.challenge, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256()):
                tokens = createJwtUser(user)
                return Response({"tokens": tokens, "displayname": user.displayname.displayName}, status=200)
            else:
                return Response("Incorrect credentials", status=401)
        return Response("Login")
    except:
        return Response("Problem occurred", status=400)