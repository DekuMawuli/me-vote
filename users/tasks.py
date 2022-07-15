from __future__ import absolute_import, unicode_literals
from users.models import CustomUser, Voter, VotersCSV, ElectionAdmin
from celery import shared_task
import csv
from django.core import mail
from django.conf import settings
import time


@shared_task(name="save_bulk_voters")
def save_bulk_voters(filename, cs_id):
    with open(filename) as f:
        reader = csv.DictReader(f)
        admin = ElectionAdmin.objects.get(time_expired=False)
        voter_mails = []
        for row in reader:
            if row['is_voter']:
                user_pwd = CustomUser.objects.make_random_password(length=8)
                c = CustomUser(username=row['username'], is_voter=True, email=row['email'])
                c.set_password(user_pwd)
                c.save()
                voter = Voter.objects.create(user=c, program=row['program'], level=row['level'], has_voted=False, admin=admin)
                c.voter = voter
                c.save()
                voter_mails.append({'username': row['username'], 'password': user_pwd, 'email': row['email']})
        v_csv = VotersCSV.objects.get(pk=cs_id)
        v_csv.is_loaded = not v_csv.is_loaded
        v_csv.save()
        send_voters_email.delay(voter_mails)
        return "Working Well"


@shared_task(name="send_voters_email")
def send_voters_email(voter_mails):
    count = 0
    with mail.get_connection() as connection:
        for user in voter_mails:
            if count == 50:
                time.sleep(120)
                count = 0
            subj = f'FastVote - {user["username"]}'
            body = f"Your password is: {user['password']}"
            recipient = [user['email']]
            mail.EmailMessage(subj, body, settings.EMAIL_HOST_USER, recipient, connection=connection).send()
            count += 1


@shared_task(name='send_single_voter_email')
def send_single_voter_email(data):
    un = str(data["username"]).split('-')
    un = '/'.join(un)
    subj = f'FastVote - {un}'
    body = f"Your password is: {data['password']}"
    recipient = [data['email']]
    mail.send_mail(subj, body, settings.EMAIL_HOST_USER, recipient)
    return 0
