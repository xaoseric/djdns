import os.path
from django.db import models
from django.db.models import signals
from django.conf import settings
from django.contrib import admin
from djdns.powerdns.admin import *
from djdns.powerdns.zone2djdns import BindZoneImporter

class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True, db_index=True)
    type = models.CharField(
                max_length=6, db_index=True, default='NATIVE',
                choices=((x,x) for x in ('NATIVE', 'MASTER')),
        )
    notified_serial = models.PositiveIntegerField(
                null=True, blank=True, db_index=True,
        )
    master = models.CharField(
                max_length=128, null=True,blank=True, db_index=True,
        )
    last_check = models.PositiveIntegerField(
                null=True, blank=True, db_index=True,
        )
    account = models.CharField(
                max_length=40, null=True, blank=True, db_index=True,
        )

    class Meta:
        db_table = 'domains'
        ordering = ( 'name', 'type' )

    def __unicode__(self):
        return self.name

class Record(models.Model):
    type_choices=(
        (x,x) for x in ('A', 'CNAME', 'NS', 'MX', 'PTR', 'SOA', 'TXT')
    )
    domain      = models.ForeignKey('Domain')
    name        = models.CharField(max_length=255, db_index=True)
    type        = models.CharField(max_length=6, db_index=True,
                                   choices=type_choices)
    content     = models.CharField(max_length=255, db_index=True)
    ttl         = models.PositiveIntegerField(db_index=True, default=3200)
    prio        = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    change_date = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'records'
        ordering = ( 'domain', 'type', 'prio', 'name' )
        unique_together = ( 'name', 'type', 'content' )

    def __unicode__(self):
        return self.name

class Supermaster(models.Model):
    nameserver = models.CharField(max_length=255, db_index=True)
    account    = models.CharField(max_length=40, null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'supermasters'
        ordering = ( 'nameserver', 'account' )
        unique_together = ( 'nameserver', 'account' )

    def __unicode__(self):
        return self.nameserver

def get_zonefile_path(self, *args):
    return os.path.join('incoming', args[0])

class ImportedZoneFile(models.Model):
    zonefile = models.FileField(upload_to=get_zonefile_path)
    domain = models.CharField(max_length=100)
    uploaded = models.DateTimeField(auto_now_add=True)

def import_zone_file(sender, **kwargs):
    instance = kwargs['instance']
    importer = BindZoneImporter()
    importer.import_from_file(instance.domain, instance.zonefile.path,
                              Domain, Record)

signals.post_save.connect(import_zone_file, sender=ImportedZoneFile)

admin.site.register(Domain, DomainAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Supermaster, SupermasterAdmin)
admin.site.register(ImportedZoneFile, ImportedZoneFileAdmin)
