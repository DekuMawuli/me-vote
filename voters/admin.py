from django.contrib import admin
from .models import Position, Contestant
# Register your models here.


class ContestantAdmin(admin.TabularInline):
    model = Contestant


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    inlines = (ContestantAdmin,)
    list_display = ("name",)

