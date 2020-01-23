from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from auction.models import Auction
from auction.serializers import AuctionDetails

class BrowseAuctionApi(APIView):

    def get(self, request):
        auctions = Auction.objects.all()
        serializer = AuctionDetails(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionApi(APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request, title):
        auctions = Auction.objects.filter(title__icontains=title)
        serializer = AuctionDetails(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionWithTermApi(APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request):
        query = self.request.GET.get('term')
        auctions = Auction.objects.filter(title__icontains=query)
        serializer = AuctionDetails(auctions, many=True)
        return Response(serializer.data)



class SearchAuctionApiById(APIView):

    renderer_classes = [JSONRenderer]

    def get(self, request, id):
        auctions = Auction.objects.filter(id=id)
        serializer = AuctionDetails(auctions, many=True)
        return Response(serializer.data)


class BidAuctionApi(APIView):
    pass
