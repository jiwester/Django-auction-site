from django.contrib.auth.models import User
from django.db import models
from ool import VersionField, VersionedMixin


class Auction(VersionedMixin, models.Model):
    version = VersionField()
    title = models.CharField(max_length=150)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    minimum_price = models.FloatField()
    deadline_date = models.DateTimeField()
    edit_link = models.CharField(max_length=200, default="")
    highbid = models.DecimalField(max_digits=10, default=0, decimal_places=2)
    highbidder = models.CharField(max_length=200, default="None")
    status = models.CharField(max_length=200, default="active")

    def __unicode__(self):
        return self.title

    def as_json(self):
        return dict(

        )


class Bid(models.Model):
    auction_id = models.IntegerField()
    bidder = models.CharField(max_length=200, default="")
    price = models.DecimalField(max_digits=10, default=0, decimal_places=2)
