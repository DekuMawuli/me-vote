from django.db import models
from users.models import ElectionAdmin


class Position(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey(ElectionAdmin, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="positions")

    def __str__(self):
        return self.name

    @property
    def count_contestants(self):
        return self.contestants.all().count()

    @property
    def pos_contestants(self):
        return self.contestants.all()

    @property
    def get_total_votes(self):
        return sum([v.votes + v.no_votes for v in self.contestants.all()])


class Contestant(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name="contestants")
    full_name = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to="profile_images/", default="default.jpg")
    votes = models.IntegerField(default=0)
    no_votes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.position.name} - {self.full_name}"

    @property
    def get_yes_percentage(self):
        if self.votes == 0:
            return 0
        return f"{(self.votes/self.position.get_total_votes * 100):.1f}"

    @property
    def get_no_percentage(self):
        if self.no_votes == 0:
            return 0
        return f"{(self.no_votes/self.position.get_total_votes * 100):.1f}"
