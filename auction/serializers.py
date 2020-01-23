from rest_framework import serializers
from auction.models import Auction

class AuctionDetails(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ('id', 'title', 'minimum_price', 'seller', 'highbid')
