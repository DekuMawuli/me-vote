from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import  logout


def staff_only(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.is_authenticated and request.user.electionadmin:
                if request.user.electionadmin.time_expired:
                    messages.warning(request, "Contact Admin to Renew your access.")
                    logout(request)
                    return redirect("staffs:login")
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, "Only Staff Members can Access this page")
                return redirect("staffs:login")
        except Exception as e:
            messages.warning(request, "Only Staff Members can Access this page")
            return redirect("staffs:login")
    return wrapper

