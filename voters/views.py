import json
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from users.models import Voter, ElectionAdmin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .decorators import allowed_to_vote, unauthenticated_user, voter_only, vote_open
from django.contrib import messages
from .models import Position, Contestant


@unauthenticated_user
def voter_login(request):
    ctx = {}
    try:
        ea = ElectionAdmin.objects.get(is_open=True, time_expired=False)
        ctx['status'] = 'ok'
    except ElectionAdmin.DoesNotExist:
        ctx['status'] = 'NAN'
    return render(request, "voters/voter-login.html", ctx)


@unauthenticated_user
@require_POST
def process_login(request):
    username = request.POST['username'].split("/")
    username = "-".join(username)
    pwd = str(request.POST['password']).strip()

    try:
        voter = Voter.objects.get(user__username=username)
    except Voter.DoesNotExist:
        messages.error(request, "Invalid Credentials... Try again !")
        return redirect("voters:login")
    if voter.has_voted:
        messages.error(request, "You have already Voted!")
        return redirect("voters:login")
    else:
        auth_user = authenticate(username=username, password=pwd)
        if auth_user is not None:
            login(request, auth_user)
            return redirect("voters:dashboard")
        else:
            messages.error(request, "You have already voted")
            return redirect("voters:login")


@login_required(login_url="voters:login")
@vote_open
@voter_only
@allowed_to_vote
def voter_dashboard(request):
    positions = Position.objects.filter(admin=request.user.voter.admin)
    ctx = {'positions': positions}
    return render(request, "voters/voter-dashboard.html", ctx)


@login_required
@vote_open
@voter_only
@allowed_to_vote
@require_POST
def vote(request):
    results = json.loads(request.POST['data'])
    for key in results.keys():
        if len(results[key]) == 2:
            sc = results[key]
            c = Contestant.objects.get(pk=int(sc['contestant']))
            if sc['value'] == "yes":
                c.votes += 1
            else:
                c.no_votes += 1
            c.save()
        else:
            sc = results[key]
            c = Contestant.objects.get(pk=int(sc['c_id']))
            c.votes += 1
            c.save()
    request.user.voter.has_voted = True
    request.user.voter.save()
    logout(request)
    return JsonResponse({"data": "Votes Recorded Successfully"}, safe=False)


@login_required
@voter_only
def voter_logout(request):
    logout(request)
    return redirect("voters:login")


def results(request):
    staff = ElectionAdmin.objects.get(time_expired=False)
    pos = Position.objects.filter(admin__time_expired=False)
    ctx = {'staff': staff, 'positions': pos}
    return render(request, "voters/results-screen.html", ctx)


def result_json(request):
    pos = Position.objects.all()
    cont_pos = []
    for p in pos:
        for cont in p.contestants.all():
            cont_pos.append({'posName': p.name, 'contName': cont.full_name, 'votes': cont.votes, 'noVotes': cont.no_votes})
    return JsonResponse({'data': cont_pos}, safe=False)


@csrf_exempt
@require_POST
def sms_vote(request):
    sender = request.POST['sender']
    sender_message = request.POST['senderMessage']
    return HttpResponse(f"Voted Uploaded")
