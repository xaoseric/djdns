import re


class RecordError(Exception):
    pass

class ParserError(Exception):
    pass

class RecordParseError(ParserError, RecordError):
    pass

class DNSRecord(object):
    recordtype = ''
    validate_content = True
    validate_name = True
    validate_domain = True
    def __init__(self, domain, name, content):
        self.domain = domain
        if self.validate_name:
            self.name = self._validate_name(name)
        else:
            self.name = name
        if self.validate_content:
            self.content = self._validate_name(content)
        else:
            self.content = content

    def _validate_name(self, name):
        if name.endswith('.'):
            # dot qualified so end should match domain
            if self.validate_domain and not name.endswith(self.domain + '.'):
                raise RecordError(
                    'dot qualified name does not end properly: %s' % \
                    name,
                )
            else:
                return name.rstrip('\.')
        elif name.endswith(self.domain):
            # fully qualified
            return name
        elif name == '@' or name.startswith('@'):
            # records pointing to the origin domain
            return self.domain
        else:
            return name + '.' + self.domain

    def __str__(self):
        return '%s IN %s %s' % (self.name, self.recordtype, self.content)

    def __unicode__(self):
        return unicode(self.__str__())

class A(DNSRecord):
    recordtype = 'A'
    validate_content = False

class CNAME(DNSRecord):
    recordtype = 'CNAME'

class MX(DNSRecord):
    recordtype = 'MX'
    validate_domain = False

    def __init__(self, domain, name, content, priority):
        self.priority = priority
        super(MX, self).__init__(domain, name, content)

    def __str__(self):
        return '%s IN %s %s %s' % (self.name, self.recordtype, self.priority,
                                self.content)

class NS(DNSRecord):
    recordtype = 'NS'
    validate_domain = False

class TXT(DNSRecord):
    recordtype = 'TXT'
    validate_content = False

class PTR(DNSRecord):
    recordtype = 'PTR'
    validate_content = False

class SOA(DNSRecord):
    recordtype = 'SOA'
    validate_name = False
    validate_content = False

class BindZoneFileParser(object):
    """a parser for bind style zone files"""
    def __init__(self, domain, path):
        """parse a domains zonefile from disk"""
        self.domain = domain
        self.path = path
        self.records = []
        zonefile = open(self.path, 'r')
        self.data = zonefile.readlines()
        zonefile.close()
        self._parse_zonefile()

    def _parse_zonefile(self):
        self._clean_data()
        for line in self.data:
            if 'IN' in line and 'SOA' not in line:
                self.records.append(self._parse_record(line))

    def _clean_data(self):
        whitespace = re.compile('\s')
        multiwhite = re.compile('\s+')
        for count in range(0, len(self.data)):
            self.data[count] = re.sub(whitespace, ' ', self.data[count]).strip()
            self.data[count] = re.sub(multiwhite, ' ',
                                      self.data[count]).split(' ')
        # remove empty lines and comments
        self.data = [ l for l in self.data if l[0] and l[0] not in [ ';', ]]

    def _parse_record(self, record):
        # check for a records
        if 'A' in record:
            if len(record) != 4:
                raise RecordParseError('A record len not 4: %s' % str(record))
            else:
                return A(self.domain, record[0], record[-1])
        elif 'CNAME' in record:
            if len(record) != 4:
                raise RecordParseError('CNAME record len not 4: %s' % str(record))
            else:
                return CNAME(self.domain, record[0], record[-1])
        elif 'MX' in record:
            if not len(record) >= 5:
                raise RecordParseError('MX record len not gte 5: %s' % str(record))
            else:
                index = record.index('MX')
                return MX(self.domain, record[0], record[index+2], record[index+1])
        elif 'NS' in record:
            if len(record) != 4:
                raise RecordParseError('CNAME record len not 4: %s' % str(record))
            else:
                return NS(self.domain, record[0], record[-1])
        elif 'TXT' in record:
            index = record.index('TXT')
            content = ' '.join(record[index+1:])
            return TXT(self.domain, record[0], content)
        elif 'PTR' in record:
            if len(record) != 4:
                raise RecordParseError('PTR record len not 4: %s' % str(record))
            else:
                return PTR(self.domain, record[0], record[-1])
        elif 'SOA' in record:
            raise str(record)
        else:
            raise RecordParseError('could not determine record type: %s' % str(record))
