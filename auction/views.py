import random
import string
from _datetime import datetime
from django.utils import translation
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.views.generic import ListView
from user.forms import CreateAuctionForm, ConfirmAuction, EditAuctionForm, BidForm
from auction.models import Auction, Bid
from django.core.mail import send_mail
from user.models import UserProfile
from django.utils.translation import gettext as _
from django.contrib import messages


def index(request):
    checkLanguage(request)
    all_auctions = Auction.objects.filter(status="active").order_by('deadline_date')
    return render(request, 'home.html', {"all_auctions": all_auctions})


class CreateAuction(View):
    def get(self, request):
        if request.user.is_authenticated:
            auction_form = CreateAuctionForm()
            return render(request, "createauction.html", {"auction_form": auction_form})
        else:
            print("Unauthorised user", request.user)
            return HttpResponseRedirect(reverse('signin'))

    def post(self, request):
        if request.user.is_authenticated:
            auction_form = CreateAuctionForm(request.POST)
            if auction_form.is_valid():
                title = auction_form.cleaned_data['title']
                description = auction_form.cleaned_data['description']
                minimum_price = auction_form.cleaned_data['minimum_price']
                deadline_date = auction_form.cleaned_data['deadline_date'].strftime('%d.%m.%Y %H:%M:%S')

                end = datetime.strptime(deadline_date, '%d.%m.%Y %H:%M:%S')
                now = datetime.strptime((datetime.now().strftime('%d.%m.%Y %H:%M:%S')), '%d.%m.%Y %H:%M:%S')

                if (end - now).total_seconds() < 259200:
                    error_message = "You have to set the deadline of the auction to at least 72 hours from now."
                    return render(request, "createauction.html",
                                  {"auction_form": auction_form, "error_message": error_message})

                if minimum_price < 0.01:
                    error_message = "Ensure that the price is greater than or equal to 0.01"
                    return render(request, "createauction.html",
                                  {"auction_form": auction_form, "error_message": error_message})

                confirm_form = ConfirmAuction()
                return render(request, "wizardtest.html",
                              {"confirm_form": confirm_form, "title": title, "description": description,
                               "minimum_price": minimum_price, "deadline_date": deadline_date})

            else:
                print("Invalid auction data")
                auction_form = CreateAuctionForm()
                return render(request, "createauction.html", {"auction_form": auction_form})
        else:
            return HttpResponseRedirect(reverse('signin'))


class EditAuction(View):
    def get(self, request, auction_id):
        try:
            auction_edit = Auction.objects.get(id=auction_id)
        except Auction.DoesNotExist:
            raise Http404("Auction does not exist")

        if request.user.is_authenticated:
            edit_auction_form = EditAuctionForm(request.POST)
            return render(request, "editauction.html",
                          {"edit_auction_form": edit_auction_form, "auction_edit": auction_edit})

        else:
            return HttpResponseRedirect(reverse("auction:edit"))

    def post(self, request, auction_id):
        try:
            auction_edit = Auction.objects.get(pk=auction_id)
        except Auction.DoesNotExist:
            raise Http404("Auction not found")

        if auction_edit.version != request.session["version"]:
            return HttpResponse("Someone else is currently editing this item, try again later.")

        if request.user.is_authenticated:
            if request.user == auction_edit.seller:
                current_auction = Auction.objects.get(pk=auction_id)
                edit_auction_form = EditAuctionForm(request.POST)

                if edit_auction_form.is_valid():
                    auction_edit.description = edit_auction_form.cleaned_data['description']
                    auction_edit.save()

                    return HttpResponseRedirect(reverse('index'))
                else:
                    return HttpResponseRedirect(reverse('auction:edit'))
            else:
                return HttpResponse("That is not your auction to edit")
        else:
            return HttpResponse("Unauthorized user")


def confirmauction(request):
    if request.user.is_authenticated:
        option = request.POST.get('option', '')
        if option == 'Yes':
            seller = request.user
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            minimum_price = request.POST.get('minimum_price').replace(',', '.')
            deadline_date = datetime.strptime(request.POST.get('deadline_date'), '%d.%m.%Y %H:%M:%S')
            edit_link = ''.join(random.choice(string.ascii_letters) for i in range(8))

            new_auction = Auction(seller=seller, title=title, description=description, minimum_price=minimum_price,
                                  deadline_date=deadline_date, edit_link=edit_link)
            new_auction.save()

            editlink = "http://127.0.0.1:8000/auction/edit/" + str(new_auction.id) + "/" + edit_link + "/"
            send_mail("Auction created", "Your auction has been listed" + "Edit your auction description here: " +
                      editlink, "test@yaas.com", [request.user.email], fail_silently=False)

            return HttpResponseRedirect(reverse('index'))
        else:
            auction_form = CreateAuctionForm()
            return render(request, "createauction.html", {'auction_form': auction_form})


class editAuctionByLink(View):
    def get(self, request, link, auction_id):
        try:
            auction_edit = Auction.objects.get(edit_link=link)
        except Auction.DoesNotExist:
            raise Http404("Auction not found")

        edit_auction_form = EditAuctionForm()
        return render(request, "editauction.html",
                      {"edit_auction_form": edit_auction_form, "auction_edit": auction_edit})

    def post(self, request, link, auction_id):
        try:
            auction_edit = Auction.objects.get(edit_link=link)

        except Auction.DoesNotExist:
            raise Http404("Auction not found")

        edit_auction_form = EditAuctionForm(request.POST)
        if edit_auction_form.is_valid():
            auction_edit.description = edit_auction_form.cleaned_data['description']
            auction_edit.save()
            return HttpResponseRedirect(reverse('index'))

        else:
            return render(request, "editauction.html",
                          {"edit_auction_form": edit_auction_form, "auction_edit": auction_edit})


def viewauction(request, auction_id):
    requested_auction = Auction.objects.filter(id=auction_id)

    if requested_auction:
        requested_auction = Auction.objects.get(id=auction_id)
        request.session["version"] = requested_auction.version

    bids = Bid.objects.filter(auction_id=auction_id)
    if bids:
        bids = checkBids(Auction.objects.get(id=auction_id))
    return render(request, "auction.html", {"requested_auction": requested_auction, "bids": bids})


class SearchAuctions(ListView):
    model = Auction
    template_name = 'searchresult.html'

    def get_queryset(self):
        query = self.request.GET.get('term')
        auctions = Auction.objects.filter(title__icontains=query,
                                          status="active")  # Case insensitive search
        return auctions


def bid(request, item_id):
    auction = Auction.objects.get(pk=item_id)

    if auction.version != request.session["version"]:
        return HttpResponse("Someone else is currently bidding on this item, try again later.")

    if auction.status == "active":
        if request.method == "POST":
            if request.user.is_authenticated:
                bid_form = BidForm(request.POST)
                if bid_form.is_valid():
                    new_bid = Bid()
                    new_bid.price = bid_form.cleaned_data['new_price']
                    new_bid.auction_id = item_id
                    new_bid.bidder = request.user

                    if (float(auction.minimum_price) + 0.01) > float(new_bid.price) or (
                            float(auction.highbid) + 0.01) > float(new_bid.price):
                        msg = _("Bid must be at least 0.01 higher than minimum price or previous bid.")
                        messages.add_message(request, messages.ERROR, msg)
                        #print("Bid has to be at least 0.01 higher than minimum price or previous bid.")
                        return HttpResponseRedirect(reverse('index'))

                    previous_bidder = auction.highbidder
                    auction.highbid = new_bid.price
                    auction.highbidder = request.user.username

                    new_bid.save()
                    auction.save()

                    # Check for previous bidder and notify via email
                    if previous_bidder != "None":
                        previous_bidder_email = User.objects.get(username=previous_bidder)

                        send_mail("Outbid", "Your have been outbid on the following item: " + auction.title,
                                  "test@yaas.com",
                                  [previous_bidder_email.email], fail_silently=False)

                    # Notify new bidder
                    send_mail("New bid", "Your bid on " + auction.title + " has been recieved", "test@yaas.com",
                              [request.user.email], fail_silently=False)

                    # Notify the seller
                    send_mail("New bid",
                              "A new bid " + str(new_bid.price) + " has been placed on you auction: " + auction.title,
                              "test@yaas.com",
                              [auction.seller.email], fail_silently=False)

                    print("New bid recieved on ", auction.title, " with the amount of ", new_bid.price)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    print("Incorrect bid given")
                    return render(request, "bid.html", {"bid_form": bid_form})
            else:
                print("Unauthenticated user tried to place a bid")
                return HttpResponseRedirect(reverse('signin'))
        else:
            if float(auction.highbid) == 0:
                price = auction.minimum_price
                auction.highbid = float(price)
                auction.save()
            else:
                price = float(auction.minimum_price)

            bid_form = BidForm()
            return render(request, "bid.html", {"bid_form": bid_form, "auction": auction, "price": price})

    else:  # Auction is not active, return to home page
        return HttpResponseRedirect(reverse('index'))


def checkBids(Auction):
    bids = []
    all_bids = Bid.objects.all()
    if all_bids:
        for b in all_bids:
            if Auction.id == b.auction_id:
                bids.append(b)
    else:
        print("No bids placed on auction yet")
    return bids


def ban(request, item_id):
    if request.user.get_username() == "admin":
        banned_auction = Auction.objects.get(pk=item_id)
        banned_auction.status = "banned"
        banned_auction.save()

        # Send mail to seller of the item
        send_mail("Auction banned", "Your auction: " + banned_auction.title + " has been banned", "test@yaas.com",
                  [banned_auction.seller.email], fail_silently=False)

        bidders = []
        selected_bids = Bid.objects.filter(auction_id=item_id)

        for bid in selected_bids:
            currentbidder = User.objects.get(username=bid.bidder)
            if currentbidder not in bidders:
                bidders.append(currentbidder.email)

        # Send mail to bidders of the item
        send_mail("Auction banned", "The auction: " + banned_auction.title + " you have bid on has been banned",
                  "test@yaas.com",
                  bidders, fail_silently=False)

        msg = _("Ban successfully")
        messages.add_message(request, messages.SUCCESS, msg)
        return render(request, "bannedauctions.html", {"banned_auction": banned_auction})
    else:
        return HttpResponseRedirect(reverse('index'))


def resolve(request):
    auctions = Auction.objects.filter(status="active")
    now = datetime.strptime((datetime.now().strftime('%d.%m.%Y %H:%M:%S')), '%d.%m.%Y %H:%M:%S')
    bidders = []
    resolved_auctions = []
    for auction in auctions:
        resolve_bids = Bid.objects.filter(auction_id=auction.id)
        deadline_date = auction.deadline_date.strftime('%d.%m.%Y %H:%M:%S')
        end = datetime.strptime(deadline_date, '%d.%m.%Y %H:%M:%S')
        if (end - now).total_seconds() <= 18000:  #Timezone did not work correctly
            auction.status = "resolved"
            auction.save()
            resolved_auctions.append(auction.title)
            # Send email to seller
            send_mail("Auction finished", "Your auction: " + auction.title + " has finished",
                      "test@yaas.com",
                      [auction.seller.email], fail_silently=False)
            if resolve_bids:
                winner = auction.highbidder
                winner_email = User.objects.get(username=winner).email
                for bid in resolve_bids:
                    currentbidder = User.objects.get(username=bid.bidder)
                    if (currentbidder not in bidders):
                        bidders.append(currentbidder.email)
                # Send email to all bidders
                send_mail("Auction finished",
                          "The auction for: " + auction.title + " has finished. Unfortunately, you did not win.",
                          "test@yaas.com",
                          bidders, fail_silently=False)

                # Send mail to winner
                send_mail("Auction finished",
                          "You won he auction for: " + auction.title + " !",
                          "test@yaas.com",
                          [winner_email], fail_silently=False)

    data = {"resolved_auctions": resolved_auctions}
    return JsonResponse(data, safe=False)


def changeLanguage(request, lang_code):
    if request.user.is_authenticated:
        currentprofile = UserProfile.objects.get(user=request.user)
        currentprofile.language = lang_code
        currentprofile.save()
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code

    else:
        translation.activate(lang_code)
        request.session[translation.LANGUAGE_SESSION_KEY] = lang_code

    if lang_code == 'en':
        msg = _("Language has been changed to English")
        messages.add_message(request, messages.SUCCESS, msg)

    if lang_code == 'sv':
        msg = _("Language has been changed to Swedish")
        messages.add_message(request, messages.SUCCESS, msg)


    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def checkLanguage(request):
    if request.user.is_authenticated:
        currentprofile = UserProfile.objects.get(user=request.user)
        lang_code = currentprofile.language
        translation.activate(lang_code)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def changeCurrency(request, currency_code):
    pass
