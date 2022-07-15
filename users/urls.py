from django.urls import path
from . import views

app_name = "staffs"

urlpatterns = [
    path("", views.staff_login, name="login"),
    path("process-voting/", views.process_login, name="process_voting"),
    path("dashboard/", views.staff_dashboard, name="dashboard"),
    path("sign-out/", views.staff_logout, name="staff_logout"),
    path("toggle-election/", views.toggle_election_status, name="toggle_election_status"),

    # TODO ============== POSITION CRUD OPERATIONS

    path("positions/", views.positions, name="positions"),
    path("position/add/", views.add_position, name="add_position"),
    path("positions-json/", views.positions_json, name="positions_json"),
    path("position/<int:pid>/", views.one_position, name="one_position"),
    path("position/<int:pid>/update/", views.update_position, name="update_position"),
    path("position/<int:pid>/delete/", views.delete_position, name="delete_position"),

    # TODO ============= VOTERS CRUD OPERATIONS
    path("voters/", views.voters, name="voters"),
    path("voter/add/", views.add_voter, name="add_voter"),
    path("voter/process/", views.process_voter_registration, name="process_registration"),
    path("voter/save-csv/", views.save_csv, name="save_csv"),
    path("voter/<int:vid>/", views.one_voter, name="one_voter"),
    path("voter/<int:vid>/update/", views.update_voter, name="update_voter"),
    path("voter/<int:vid>/delete/", views.delete_voter, name="delete_voter"),


    # TODO ============== CONTESTANTS CRUD OPERATIONS
    path("contestants/", views.contestants, name="contestants"),
    path("contestant/add/", views.add_contestant, name="add_contestant"),
    path("contestant/process/", views.process_candidate_registration, name="process_contestant_registration"),
    path("contestants-json/", views.contestants_json, name="contestants_json"),
    path("contestant/<int:cid>/", views.one_contestant, name="one_contestant"),
    path("contestant/<int:cid>/update/", views.update_contestant, name="update_contestant"),
    path("contestant/<int:cid>/delete/", views.delete_contestant, name="delete_contestant"),



    # TODO ======================= REPORTS ROUTES
    path("reports/voters/", views.VotersReportView.as_view(), name='voters_report'),
    path("reports/general-statistics/", views.VoterGeneralStatistics.as_view(), name='general_statistics'),
    # path("reports/voters/", views.voters_report, name='voters_report'),
    # path("reports/voters/", views.voters_report, name='voters_report'),
]
