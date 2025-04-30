from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from . import models
from accounts.models import UserDisplayName

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q

# Create your views here.
@api_view(["POST"])
def createEvent(request):
    user = request.user.displayname
    try:
        event = models.Events(name=request.POST["name"], creator=user, startDate=request.POST["startdate"], endDate=request.POST["enddate"],
                            location=request.POST["location"], description=request.POST["description"])
        event.save()
        participants = request.POST.getlist("participants")
        for i in participants:
            user_ = UserDisplayName.objects.filter(displayName=i)[0]
            try:
                userEvent = models.UserEvents(user=user_, event=event)
                userEvent.save()
            except:
                pass  # in case user already invited.
        return Response("Event created", status=201)
    except:
        return Response("Event already exists", status=409)

@api_view(["POST"])
def myEvents(request):
    user = request.user.displayname
    try:
        userEvents = models.Events.objects.filter(creator=user)
        responseData = {}
        for i in range(len(userEvents)):
            participantsEvent = models.UserEvents.objects.filter(event=userEvents[i])  # all participants.
            participants = [i.user.displayName for i in participantsEvent]
            responseData[i] = [userEvents[i].name, participants, userEvents[i].startDate, userEvents[i].endDate, userEvents[i].location, 
                                userEvents[i].description]
        
        return Response(responseData, status=200)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def invitedEvents(request):
    user = request.user.displayname
    try:
        userEvents = models.UserEvents.objects.filter(user=user)
        responseData = {}
        for i in range(len(userEvents)):
            participantsEvent = models.UserEvents.objects.filter(event=userEvents[i].event)  # all participants.
            participants = [i.user.displayName for i in participantsEvent]
            responseData[i] = [userEvents[i].event.name, userEvents[i].event.creator.displayName, participants, userEvents[i].event.startDate, 
                                userEvents[i].event.endDate, userEvents[i].event.location, userEvents[i].event.description]
        
        return Response(responseData, status=200)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def modifyEvent(request):
    user = request.user.displayname
    try:
        event = models.Events.objects.filter(name=request.POST["oldname"], creator=user, startDate=request.POST["oldstartdate"],
                                            endDate=request.POST["oldenddate"])[0]
        try:
            event.name = request.POST["newname"]
            event.startDate = request.POST["newstartdate"]
            event.endDate = request.POST["newenddate"]
            event.location = request.POST["newlocation"]
            event.description = request.POST["newdescription"]
            event.save()

            newParticipants = request.POST.getlist("newparticipants")
            newParticipantsObjectsUserDisplay = []
            for i in newParticipants:
                user_ = UserDisplayName.objects.filter(displayName=i)[0]
                newParticipantsObjectsUserDisplay.append(user_)
                try:
                    userEvent = models.UserEvents(user=user_, event=event)
                    userEvent.save()
                except:  # when there is a userEvent but he got deleted from event.
                    pass  # in case user already invited.
            
            queryset = models.UserEvents.objects.exclude(Q(user__in=newParticipantsObjectsUserDisplay))
            queryset.delete()
            return Response("Event modified", status=200)
        except:
            return Response("Event collision, change name or date", status=409)
    except:
        return Response("Problem occurred", status=400)

@api_view(["POST"])
def removeEvent(request):
    user = request.user.displayname
    try:
        models.Events.objects.filter(name=request.POST["name"], creator=user, startDate=request.POST["startdate"],
                                        endDate=request.POST["enddate"]).delete()
        return Response("Deleted event", status=200)
    except:
        return Response("Problem occurred", status=400)
