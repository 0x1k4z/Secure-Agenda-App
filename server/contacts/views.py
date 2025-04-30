from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from . import models
from accounts.models import UserDisplayName
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

# Create your views here.
@api_view(["POST"])
def addContact(request):
    user = request.user.displayname
    try:
        friend = UserDisplayName.objects.filter(displayName=request.POST["frienddisplayname"])[0]
        if not models.Contacts.objects.filter(Q(requester=user, addressee=friend, status=1) | Q(requester=friend, addressee=user, status=1)).exists():
            if not models.Contacts.objects.filter(Q(requester=user, addressee=friend, status=0) | Q(requester=friend, addressee=user, status=0)).exists():
                contact = models.Contacts(requester=user, addressee=friend, status=0)
                contact.save()
                return Response("Invitation sent", status=201)
            else:
                return Response("Invitation already pending", status=401)
        else:
            return Response("You are already friends", status=401)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def myContacts(request):
    user = request.user.displayname
    try:
        contacts = models.Contacts.objects.filter(Q(requester=user, status=1) | Q(addressee=user, status=1))
        contactsDisplayName = list()
        for i in contacts:
            if (i.addressee == user):
                contactsDisplayName.append(i.requester.displayName)
            else:
                contactsDisplayName.append(i.addressee.displayName)
        
        return Response(contactsDisplayName, status=200)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def pendingContacts(request):
    user = request.user.displayname
    try:
        pendingContacts = models.Contacts.objects.filter(addressee=user, status=0)
        pendingContactsDisplayName = [i.requester.displayName for i in pendingContacts]
        return Response(pendingContactsDisplayName, status=200)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def acceptContact(request):
    addressee = request.user.displayname
    try:
        requester = UserDisplayName.objects.filter(displayName=request.POST["frienddisplayname"])[0]
        models.Contacts.objects.filter(addressee=addressee, requester=requester, status=0).update(status=1)
        return Response("Accepted invitation", status=200)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def removeContact(request):
    user = request.user.displayname
    try:
        friend = UserDisplayName.objects.filter(displayName=request.POST["frienddisplayname"])[0]
        models.Contacts.objects.filter(Q(requester=user, addressee=friend) | Q(requester=friend, addressee=user)).delete()
        return Response("Deleted contact", status=200)
    except:
        return Response("Problem occurred", status=400)
