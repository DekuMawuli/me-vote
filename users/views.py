from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .decorators import staff_only
from .models import CustomUser, Voter, ElectionAdmin, VotersCSV
from voters.models import Position, Contestant
from django.template.loader import render_to_string
from voters.forms import ContestantForm
from .forms import CustomUserCreationForm, VoterForm
from django.conf import settings
from easy_pdf.views import PDFTemplateView
from django.utils.decorators import method_decorator
from .tasks import send_single_voter_email


def staff_login(request):
    return render(request, "users/login.html")


@require_POST
def process_login(request):
    username = request.POST['username']
    if '/' in username:
        username = username.split('/')
        username = '-'.join(username)
    password = request.POST['password']
    
    try:
        user = CustomUser(username=username, role=2)
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid Credentials")
        return redirect("staffs:login")
    
    auth_user = authenticate(username=user.username, password=password)
    if auth_user is not None:
        login(request, auth_user)
        return redirect("staffs:dashboard")
    else:
        messages.error(request, "Invalid Credentials")
        return redirect("staffs:login")
    

@login_required(login_url="staffs:login")
@staff_only
def staff_dashboard(request):
    pos = request.user.electionadmin.get_election_positions
    my_voters = request.user.electionadmin.get_voters
    voted_voters = request.user.electionadmin.get_voted_voters
    ctx = {'positions': pos, 'voters': my_voters, 'vv': voted_voters}
    return render(request, "users/staff-dashboard.html", context=ctx)


@login_required(login_url="staffs:login")
@staff_only
def staff_logout(request):
    logout(request)
    return redirect("staffs:login")


# TODO ================ POSITIONS CRUD
@login_required(login_url="staffs:login")
@staff_only
def positions(request):
    return render(request, "positions/position.html")


@login_required(login_url="staffs:login")
@staff_only
def positions_json(request):
    pos = request.user.electionadmin.get_election_positions
    ctx = {'positions': pos}
    pos_html = render_to_string("positions/position-list.inc.html", context=ctx)
    return JsonResponse({'data': pos_html}, safe=False)


@login_required(login_url="staffs:login")
@staff_only
def one_position(request, pid):
    try:
        pos = Position.objects.get(pk=pid)
        res = {'pk': pos.pk, 'name': pos.name}
        return JsonResponse({'data': res}, safe=False)
    except Position.DoesNotExist:
        return JsonResponse({'data': "No Position Found"}, safe=False)


@login_required(login_url="staffs:login")
@staff_only
def update_position(request, pid):
    pos_name = request.POST['position']
    try:
        position = Position.objects.get(pk=pid)
        position.name = pos_name
        position.save()
        return JsonResponse({'data': "Update Successful"}, safe=False)
    except Position.DoesNotExist:
        return JsonResponse({'data': "Position Does Not Exist"}, safe=False)


@login_required(login_url="staffs:login")
@staff_only
def add_position(request):
    pos_name = request.POST['position']
    try:
        Position.objects.create(name=pos_name, admin=request.user.electionadmin)
        return JsonResponse({'data': "Position Added Successfully"}, safe=False)
    except Exception as e:
        return JsonResponse({'data': e}, safe=False)


@login_required(login_url="staffs:login")
@staff_only
def delete_position(request, pid):
    try:
        position = Position.objects.get(pk=pid)
        position.delete()
        return JsonResponse({'data': "Success"}, safe=False)
    except Position.DoesNotExist:
        return JsonResponse({'data': "Position Does Not Exist"}, safe=False)


# TODO ==================== CONTESTANTS CRUD
@login_required(login_url="staffs:login")
@staff_only
def contestants(request):
    return render(request, 'contestants/contestants.html')


@login_required(login_url="staffs:login")
@staff_only
def contestants_json(request):
    cons = Contestant.objects.filter(position__admin=request.user.electionadmin)
    ctx = {'contestants': cons}
    cons_html = render_to_string("contestants/contestant-list.inc.html", context=ctx)
    return JsonResponse({'data': cons_html}, safe=False)


@login_required(login_url="staffs:login")
@staff_only
def one_contestant(request, cid):
    try:
        con = Contestant.objects.get(pk=cid)
    except Contestant.DoesNotExist:
        return JsonResponse({'data': "No Contestant Available"}, safe=False)
    c_form = ContestantForm(instance=con)
    ctx = {'contestant': con, 'form': c_form}
    c_html = render_to_string("contestants/contestant-form.inc.html", context=ctx, request=request)
    return JsonResponse({'data': c_html}, safe=False)


@login_required(login_url="staffs:login")
@staff_only
def add_contestant(request):
    cf = ContestantForm()
    ctx = {'form': cf}
    return render(request, 'contestants/add-contestant.html', ctx)


@require_POST
@login_required(login_url="staffs:login")
@staff_only
def process_candidate_registration(request):
    cf = ContestantForm(request.POST, request.FILES)
    if cf.is_valid():
        cf.save()
        messages.success(request, "Candidate Added Successfully")
        return redirect("staffs:add_contestant")
    else:
        messages.error(request, cf.errors)
        return redirect("staffs:add_contestant")


@require_POST
@login_required(login_url="staffs:login")
@staff_only
def update_contestant(request, cid):
    con = Contestant.objects.get(pk=cid)
    cf = ContestantForm(request.POST, request.FILES, instance=con)
    if cf.is_valid():
        cf.save()
        messages.success(request, "Candidate Update Successful")
        return redirect("staffs:contestants")
    else:
        messages.error(request, cf.errors)
        return redirect("staffs:contestants")


@require_POST
@login_required(login_url="staffs:login")
@staff_only
def delete_contestant(request, cid):
    try:
        con = Contestant.objects.get(pk=cid)
        name = con.full_name
        con.delete()
        return JsonResponse({'data': f"{name} Deleted Successfully"}, safe=False)
    except Position.DoesNotExist:
        return JsonResponse({'data': "Contestant Does Not Exist"}, safe=False)


# TODO ========================== VOTER CRUD
@login_required(login_url="staffs:login")
@staff_only
def voters(request):
    all_voters = request.user.electionadmin.voter_set.all()
    ctx = {'voters': all_voters}
    return render(request, 'voters/all-voters.html', context=ctx)


@require_POST
@login_required(login_url="staffs:login")
@staff_only
def update_voter(request, vid):
    pass


@login_required(login_url="staffs:login")
@staff_only
def one_voter(request, vid):
    pass


@require_POST
@login_required(login_url="staffs:login")
@staff_only
def delete_voter(request, vid):
    pass





@require_POST
@login_required(login_url="staffs:login")
@staff_only
def process_voter_registration(request):
    stud_id = request.POST['username'].split('/')
    stud_id = '-'.join(stud_id)
    email = request.POST['email']
    program = request.POST['program']
    level = request.POST['level']
    u_pwd = CustomUser.objects.make_random_password(length=8)
    try:
        user = CustomUser.objects.create(username=stud_id, email=email, role=3)
        user.set_password(u_pwd)
        user.save()
    except Exception as e:
        messages.error(request, e)
        return redirect("staffs:add_voter")
    try:
        voter = Voter.objects.create(user_id=user.pk, admin=request.user.electionadmin, level=level, program=program, has_voted=False)
        data = {'username': voter.user.username, 'password': u_pwd, 'email': voter.user.email}
        send_single_voter_email.delay(data)
    except Exception as e:
        messages.error(request, e)
        return redirect("staffs:add_voter")
    messages.success(request, f"{voter.user.username} is added successfully!")
    return redirect("staffs:add_voter")


@require_POST
@login_required(login_url="staffs:login")
@staff_only
def save_csv(request):
    stud_csv = request.FILES['students']
    VotersCSV.objects.create(is_loaded=False, file=stud_csv)
    messages.success(request, "Voters Being Uploaded")
    return redirect("staffs:add_voter")


@login_required(login_url="staffs:login")
@staff_only
def add_voter(request):
    cf = CustomUserCreationForm()
    vf = VoterForm()
    ctx = {'u_form': cf, 'v_form': vf}
    return render(request, "voters/add-voter.html", context=ctx)


@login_required(login_url="staffs:login")
@staff_only
def toggle_election_status(request):
    staffer = ElectionAdmin.objects.get(user=request.user)
    staffer.is_open = not staffer.is_open
    staffer.save()
    return redirect("staffs:dashboard")


class VotersReportView(PDFTemplateView):
    template_name = 'reports/voters.html'  # html template

    base_url = 'file://' + str(settings.STATIC_ROOT)
    download_filename = 'voters_report.pdf'  # File name when downloading pdf
    req = ""

    @method_decorator(login_required(login_url="staffs:login"), staff_only)
    def dispatch(self, request, *args, **kwargs):
        global req
        req = request
        return super().dispatch(*args, request, **kwargs)

    def get_context_data(self, **kwargs):
        global req
        print(kwargs)
        return super(VotersReportView, self).get_context_data(
            pagesize='A4',
            title="Voter's Report",  # The title at the top of the file after converting to pdf
            voters=req.user.electionadmin.voter_set.all(),
            **kwargs
        )


class VoterGeneralStatistics(PDFTemplateView):
    template_name = 'reports/gen-stats.html'  # html template

    base_url = 'file://' + str(settings.STATIC_ROOT)
    download_filename = 'general-statistics.pdf'  # File name when downloading pdf
    requests = ""

    @method_decorator(login_required(login_url="staffs:login"), staff_only)
    def dispatch(self, request,  *args, **kwargs):
        global requests
        requests = request
        return super().dispatch(*args, request, **kwargs)

    def get_context_data(self,  **kwargs):
        global requests
        all_voters = requests.user.electionadmin.voter_set.all()
        return super(VoterGeneralStatistics, self).get_context_data(
            pagesize='A4',
            title="General Statistics",  # The title at the top of the file after converting to pdf
            voters=all_voters.count(),
            voted_voters=len([v for v in all_voters if v.has_voted]),
            aspirants=Contestant.objects.filter(position__admin=requests.user.electionadmin),
            all_pos=requests.user.electionadmin.get_election_positions,
            **kwargs
        )

