from .models import CustomUser, Voter, ElectionAdmin, VotersCSV
from django.dispatch import receiver
from django.db.models.signals import post_save
from .tasks import save_bulk_voters


@receiver(signal=post_save, sender=CustomUser)
def user_created(instance, created, **kwargs):
    if created:
        if instance.role == 2:
            ElectionAdmin.objects.create(user=instance)
    else:
        print(instance.role)
        if instance.role == 2:
            instance.electionadmin.save()


@receiver(signal=post_save, sender=VotersCSV)
def file_saved(sender, instance, created, **kwargs):
    if created:
        save_bulk_voters.delay(instance.file.path, instance.pk)
    else:
        if not instance.is_loaded:
            save_bulk_voters.delay(instance.file.path, instance.pk)
