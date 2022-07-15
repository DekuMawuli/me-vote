from django.urls import path
from . import views

app_name = "voters"

urlpatterns = [
    path("", views.voter_login, name="login"),
    path("process-voting/", views.process_login, name="process_voting"),
    path("dashboard/", views.voter_dashboard, name="dashboard"),
    path("vote/", views.vote, name="vote"),
    path("sign-out/", views.voter_logout, name="voter_logout"),
    path("results/", views.results, name="general_results"),
    path("results-json/", views.result_json, name="result_json"),
    path("sms/", views.sms_vote, name="sms"),

]
