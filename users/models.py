from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLES = [
        (1, "Super Admin"),
        (2, "Election Admin"),
        (3, "Voter"),
    ]
    role = models.PositiveIntegerField(default=1, choices=ROLES)


class ElectionAdmin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time_expired = models.BooleanField(default=False)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username

    @property
    def get_all_contestants(self):
        return sum(pos.count_contestants for pos in self.positions.all())

    @property
    def get_contestants_count(self):
        return [pos.count_contestants for pos in self.positions.all()]

    @property
    def get_election_positions(self):
        return self.positions.all()

    @property
    def get_voted_voters(self):
        return len([voter for voter in self.voter_set.all() if voter.has_voted])

    @property
    def get_voters(self):
        return self.voter_set.count()


class Voter(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    admin = models.ForeignKey(ElectionAdmin, on_delete=models.CASCADE, null=True, blank=True)
    program = models.CharField(max_length=100)
    level = models.CharField(max_length=100)
    has_voted = models.BooleanField(default=False)
    mail_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def reversed_username(self):
        uname = self.user.username.split('-')
        return "/".join(uname)


class VotersCSV(models.Model):
    file = models.FileField(upload_to="csvs/")
    is_loaded = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file} - {self.is_loaded} ::: {self.date_updated}"
