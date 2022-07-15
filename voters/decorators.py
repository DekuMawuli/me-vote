from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout


def allowed_to_vote(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.voter.has_voted:
            return view_func(request, *args, **kwargs)
        else:
            logout(request)
            messages.error(request, "You have Voted")
            return redirect("voters:login")
    return wrapper


def unauthenticated_user(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            if request.user.is_voter:
                return redirect("voters:dashboard")
            else:
                return redirect("staffs:dashboard")
    return wrapper


def voter_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 3:
            return view_func(request, *args, **kwargs)
        elif not request.user.role == 3:
            return redirect("staffs:dashboard")
        else:
            messages.info(request, "Voter Only")
            return redirect("voters:login")
    return wrapper


def vote_open(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.voter.admin.is_open:
            return view_func(request, *args, **kwargs)
        else:
            logout(request)
            messages.info(request, "Voting Process is closed")
            return redirect("voters:login")
    return wrapper
