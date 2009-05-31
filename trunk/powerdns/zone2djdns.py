from djdns.utils.parsers import *

class ImporterError(Exception):
    pass

class BindZoneImporter(object):
    def import_from_file(self, domain, path, DomainClass, RecordClass):
        self.parser = BindZoneFileParser(domain, path)
        self.DomainClass = DomainClass
        self.RecordClass = RecordClass
        self.domain, created = self.DomainClass.objects.get_or_create(
            name=domain,
        )
        if created:
            self.domain.save()
        for record in self.parser.records:
            if record.recordtype == 'A':
                self.add_a_record(record)
            elif record.recordtype == 'CNAME':
                self.add_cname_record(record)
            elif record.recordtype == 'MX':
                self.add_mx_record(record)
            elif record.recordtype == 'NS':
                self.add_ns_record(record)
            elif record.recordtype == 'TXT':
                self.add_txt_record(record)
            elif record.recordtype == 'PTR':
                self.add_ptr_record(record)
            else:
                raise ImporterError(
                    'unsupported recordtype requested: %s' % record.recordtype,
                )

    def add_basic_record(self, record):
        if hasattr(record, 'priority'):
            db_record, created = self.RecordClass.objects.get_or_create(
                domain = self.domain,
                type = record.recordtype,
                name = record.name,
                content = record.content,
                prio = record.priority,
            )
        else:
            db_record, created = self.RecordClass.objects.get_or_create(
                domain = self.domain,
                type = record.recordtype,
                name = record.name,
                content = record.content,
            )
        if created:
            db_record.save()

    def add_a_record(self, record):
        # only one a record per ip per domain
        # so let see if see exists already
        try:
            a_record = self.RecordClass.objects.get(
                domain = self.domain,
                type = record.recordtype,
                content = record.content,
            )
            if a_record.name != record.name:
                # create a cname record instead
                cname_record = self.RecordClass(
                    domain = self.domain,
                    type = 'CNAME',
                    name = record.name,
                    content = a_record.name,
                )
                cname_record.save()
        except:
            a_record = self.RecordClass(
                domain = self.domain,
                type = record.recordtype,
                name = record.name,
                content = record.content,
            )
            a_record.save()

    def add_cname_record(self, record):
        self.add_basic_record(record)

    def add_mx_record(self, record):
        self.add_basic_record(record)

    def add_ns_record(self, record):
        self.add_basic_record(record)

    def add_txt_record(self, record):
        self.add_basic_record(record)

    def add_ptr_record(self, record):
        # ptr an only have a single record per name
        try:
            ptr_record = self.RecordClass.objects.get(
                domain = self.domain,
                type = record.recordtype,
                name = record.name,
            )
            if ptr_record.content != record.content:
                ptr_record.content = record.content
                ptr_record.save()
        except:
            ptr_record = self.RecordClass(
                domain = self.domain,
                type = record.recordtype,
                name = record.name,
                content = record.content,
            )
            ptr_record.save()
