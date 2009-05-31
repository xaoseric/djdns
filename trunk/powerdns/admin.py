from django.contrib import admin

class DomainAdmin(admin.ModelAdmin):
    pass

class RecordAdmin(admin.ModelAdmin):
    ordering = [ 'domain', 'type', 'prio', 'name' ]
    list_display = [ 'domain', 'type', 'name', 'content' ]
    list_filter = [ 'domain', 'type' ]
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': ('domain', ('type', 'name', 'content', 'ttl'))
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('prio', 'change_date')
        }),
    )
    search_fields = ['domain__name', 'name', 'content']

class SupermasterAdmin(admin.ModelAdmin):
    pass

class ImportedZoneFileAdmin(admin.ModelAdmin):
    pass
