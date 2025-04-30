from django.db import models

# Create your models here.
class Events(models.Model):
    name = models.CharField(max_length=64)
    creator = models.ForeignKey('accounts.UserDisplayName', on_delete=models.CASCADE)
    startDate = models.CharField(max_length=64)
    endDate = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    description = models.CharField(max_length=64)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "creator", "startDate", "endDate"], name="unique_event")]

class UserEvents(models.Model):
    user = models.ForeignKey('accounts.UserDisplayName', on_delete=models.CASCADE)
    event = models.ForeignKey('Events', on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "event"], name="unique_user_event")]
