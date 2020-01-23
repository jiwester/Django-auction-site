from django.contrib import messages, auth
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, redirect
from user.forms import UserForm, EditProfileForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from user import forms
from django.utils.translation import gettext as _
from django.contrib import messages



@login_required
def special(request):
    return HttpResponse("You are logged in!")


@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


class SignUp(View):

    def get(self, request):
        user_form = UserForm()
        return render(request, "signup.html", {'user_form': user_form})

    def post(self, request):
        user_form = UserForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if user_form.is_valid():
            new_user = user_form.save()
            new_user.set_password(password)
            new_user.save()
            # return reverse('signin')
            print("New user created with info:", username, email, password)
            return HttpResponseRedirect(reverse("index"))

        else:
            print("User creation failed")
            user_form = UserForm(request.POST)
            return render(request, "signup.html", {'user_form': user_form})


class SignIn(View):
    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            msg = _("Login successful!")
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect(reverse("index"))
        else:
            msg = _("Invalid username or password.")
            messages.add_message(request, messages.ERROR, msg)
            return HttpResponseRedirect(reverse("signin"))


class EditProfile(View):
    def get(self, request):
        if request.user.is_authenticated:
            edit_form = EditProfileForm()
            print("User:", request.user, request.user.id, "is authenticated")
            return render(request, "editprofile.html", {'edit_form': edit_form})
        else:
            print("Unauthorised user", request.user)
            return HttpResponseRedirect(reverse('signin'))

    def post(self, request):
        if request.user.is_authenticated:
            edit_form = EditProfileForm(request.POST, instance=request.user)
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(request.user, request.user.username, request.user.email, "is editing user info")

            if edit_form.is_valid():
                # Check if email exists
                if not User.objects.filter(email=email).count():
                    request.user.email = email
                    edited = edit_form.save()
                    edited.set_password(password)
                    edited.save()
                    update_session_auth_hash(request, edited)
                    print("User info saved with info:", username, email, password)

                else:
                    return HttpResponseRedirect(reverse("user:editprofile"))
            else:
                edit_form = EditProfileForm(request.POST)
                return render(request, "editprofile.html", {'edit_form': edit_form})

        else:
            return HttpResponseRedirect(reverse("signin"))

        return HttpResponseRedirect(reverse("index"))
