from django.db import models

# Create your models here.
class Contacts(models.Model):
    requester = models.ForeignKey('accounts.UserDisplayName', on_delete=models.CASCADE)
    addressee = models.ForeignKey('accounts.UserDisplayName', related_name="friend_id", on_delete=models.CASCADE)
    status = models.IntegerField()  # 0: not friends yet (pending), 1: friends.

    class Meta:
        constraints = [models.UniqueConstraint(fields=["requester", "addressee"], name="unique_friendship")]
