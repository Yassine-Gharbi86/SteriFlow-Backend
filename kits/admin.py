from django.contrib import admin
from .models import Kit, Report


@admin.register(Kit)
class KitAdmin(admin.ModelAdmin):
    list_display  = ('kit_id', 'kit_name', 'service', 'status', 'created_by', 'updated_at')
    list_filter   = ('status', 'service')
    search_fields = ('kit_id', 'kit_name', 'service')
    ordering      = ('-updated_at',)
    readonly_fields = ('kit_id', 'created_at', 'updated_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display  = ('id', 'kit_name_snapshot', 'reporter_nom', 'reporter_prenom', 'severity', 'status', 'created_at')
    list_filter   = ('severity', 'status')
    search_fields = ('reporter_nom', 'reporter_prenom', 'kit_name_snapshot', 'message')
    ordering      = ('-created_at',)
    readonly_fields = ('created_at',)
