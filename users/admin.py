from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Voter, ElectionAdmin, VotersCSV


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            'Personal info', {
                'fields': ('first_name', 'last_name', 'role')
            }
        ),
        ('Permissions', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )
                         }
         ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    limited_fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'role', 'password1', 'password2'
            )
        }
        ),
    )
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    readonly_fields = ('last_login', 'date_joined',)


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    search_fields = ("has_voted",)
    list_display = ("user", "level", "program", "has_voted")


@admin.register(ElectionAdmin)
class ElectionAdminPanel(admin.ModelAdmin):
    list_display = ("user", "is_open", "name")


@admin.register(VotersCSV)
class VoteCSV(admin.ModelAdmin):
    list_display = ("file", "is_loaded", "date_added", "date_updated",)
    list_editable = ("is_loaded",)
