from django.contrib import admin
from .models import Association,AssociationMembership

# Register your models here.

admin.site.register(Association)
@admin.register(AssociationMembership)
class AssociationMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "association", "role", "date_joined")
    autocomplete_fields = ['user']  # Enables search for user field
