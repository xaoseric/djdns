from djdns.utils.parsers import BindZoneFileParser

class BindZoneImporter(object):
    def import_from_file(self, domain, path, domainclass, recordclass):
        self.parser = BindZoneFileParser(domain, path)
        self.domain, created = domainclass.objects.get_or_create(name=domain)
        if created:
            self.domain.save()
        for record in self.parser.records:
            # see if record exists
            db_record, created = recordclass.objects.get_or_create(
                domain = self.domain,
                type = record.recordtype,
                name = record.name,
                content = record.content,
            )
            if created:
                db_record.save()





