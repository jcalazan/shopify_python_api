import re
import json
from six.moves.urllib import request

class InvalidVersionError(Exception):
    pass

class VersionNotFoundError(Exception):
    pass

class ApiVersion(object):
    versions = {}

    @classmethod
    def coerce_to_version(cls, version):
        try:
            return cls.versions[version]
        except KeyError:
            raise VersionNotFoundError

    @classmethod
    def define_version(cls, version):
        cls.versions[version.name] = version
        return version

    @classmethod
    def define_known_versions(cls):
        json_string = '{"apis":[{"handle":"admin","versions":[{"handle":"2019' \
                      '-04","latest_supported":false,"display_name":"2019-04 ' \
                      '(Unsupported)","supported":true},{"handle":"2019-07",' \
                      '"latest_supported":false,"display_name":"2019-07 ' \
                      '(Unsupported)","supported":true},{"handle":"2019-10",' \
                      '"latest_supported":false,"display_name":"2019-10 ' \
                      '(Unsupported)","supported":true},{"handle":"2020-01",' \
                      '"latest_supported":false,"display_name":"2020-01 ' \
                      '(Unsupported)","supported":true},{"handle":"2020-04",' \
                      '"latest_supported":false,"display_name":"2020-04",' \
                      '"supported":true},{"handle":"2020-07","latest_' \
                      'supported":false,"display_name":"2020-07","supported":' \
                      'true},{"handle":"2020-10","latest_supported":false,' \
                      '"display_name":"2020-10","supported":true},{"handle":' \
                      '"2021-01","latest_supported":true,"display_name":' \
                      '"2021-01 (Latest)","supported":true},{"handle":' \
                      '"2021-04","latest_supported":false,"display_name":' \
                      '"2021-04 (Release candidate)","supported":false},' \
                      '{"handle":"unstable","latest_supported":false,"display' \
                      '_name":"unstable","supported":false}]},{"handle":' \
                      '"storefront","versions":[{"handle":"2019-07","latest_' \
                      'supported":false,"display_name":"2019-07 ' \
                      '(Unsupported)","supported":true},{"handle":"2019-10",' \
                      '"latest_supported":false,"display_name":"2019-10 ' \
                      '(Unsupported)","supported":true},{"handle":"2020-01",' \
                      '"latest_supported":false,"display_name":"2020-01 ' \
                      '(Unsupported)","supported":true},{"handle":"2020-04",' \
                      '"latest_supported":false,"display_name":"2020-04",' \
                      '"supported":true},{"handle":"2020-07","latest_' \
                      'supported":false,"display_name":"2020-07",' \
                      '"supported":true},{"handle":"2020-10","latest_' \
                      'supported":false,"display_name":"2020-10","supported":' \
                      'true},{"handle":"2021-01","latest_supported":true,' \
                      '"display_name":"2021-01 (Latest)","supported":true},' \
                      '{"handle":"2021-04","latest_supported":false,' \
                      '"display_name":"2021-04 (Release candidate)",' \
                      '"supported":false},{"handle":"unstable","latest_' \
                      'supported":false,"display_name":"unstable","supported"' \
                      ':false}]}]}'
        data = json.loads(json_string)
        for api in data['apis']:
            if api['handle'] == 'admin':
                for release in api['versions']:
                    if release['handle'] == 'unstable':
                        cls.define_version(Unstable())
                    else:
                        cls.define_version(Release(release['handle']))

    @classmethod
    def clear_defined_versions(cls):
        cls.versions = {}

    @property
    def numeric_version(self):
        return self._numeric_version

    @property
    def name(self):
        return self._name

    def api_path(self, site):
        return site + self._path

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.numeric_version == int(other.numeric_version)


class Release(ApiVersion):
    FORMAT = re.compile(r'^\d{4}-\d{2}$')
    API_PREFIX = '/admin/api'

    def __init__(self, version_number):
        if not self.FORMAT.match(version_number):
            raise InvalidVersionError
        self._name = version_number
        self._numeric_version = int(version_number.replace('-', ''))
        self._path = '%s/%s' % (self.API_PREFIX, version_number)

    @property
    def stable(self):
        return True


class Unstable(ApiVersion):
    def __init__(self):
        self._name = 'unstable'
        self._numeric_version = 9000000
        self._path =  '/admin/api/unstable'

    @property
    def stable(self):
        return False


ApiVersion.define_known_versions()
