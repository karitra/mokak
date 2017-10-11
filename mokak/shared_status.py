import time
from collections import namedtuple


TRIM_DESC_LIMIT = 180


def _int_seconds_from_epoch():
    return int(time.time())


def _norm_desc(desc, limit=TRIM_DESC_LIMIT):
    if len(desc) > limit:
        desc = desc[:limit]
    return desc


class _FieldsNames(object):
    STATUS = 'status'
    LAST_UPDATE = 'last_update'
    EXTENDEND_STATUS = 'extendend_status'


class _StatusHandler(object):

    OK_STATUS, WARN_STATUS, CRIT_STATUS = \
        'OK', 'WARN', 'CRIT'

    Status = namedtuple('Status', [
        'status',
        'desc'
    ])

    def __init__(self, shared_status, name):
        self.shared_status = shared_status
        self.name = name

    def mark_ok(self, desc):
        desc = self._norm_desc(desc)
        self.shared_status.mark_submodule_status(
            self.name, _StatusHandler.Status(_StatusHandler.OK_STATUS, desc))

    def mark_warn(self, desc):
        desc = self._norm_desc(desc)
        self.shared_status.mark_submodule_status(
            self.name, _StatusHandler.Status(_StatusHandler.WARN_STATUS, desc))

    def mark_crit(self, desc):
        desc = self._norm_desc(desc)
        self.shared_status.mark_submodule_status(
            self.name, _StatusHandler.Status(_StatusHandler.CRIT, desc))


class SharedStatus(object):
    def __init__(self):
        self.status = dict(last_update=_int_seconds_from_epoch())
        self.submodules_status = dict()

    def register(self, name):
        return _StatusHandler(self, name)

    def mark_submodule_status(self, submodule_name, status):
        self.status[_FieldsNames.LAST_UPDATE] = _int_seconds_from_epoch()
        self.submodules_status[submodule_name] = status

    def as_dict(self):
        is_crit = self._has_status(_StatusHandler.CRIT_STATUS)
        is_warn = self._has_status(_StatusHandler.WARN_STATUS)

        status = _StatusHandler.OK_STATUS
        if is_crit:
            status = _StatusHandler.CRIT_STATUS
        elif is_warn:
            statis = _StatusHandler.WARN_STATUS

        self.status[_FieldsNames.STATUS] = status
        extendend_status = {
            submodule_name: status._as_dict()
            for submodule_name, status in self.submodules_status.iteritems()
        }

        return dict(
            self.status, **{_FieldsNames.EXTENDEND_STATUS: extendend_status})

    def _has_status(self, status):
        return any(
            st.status == status
            for _, st in self.submodules_status.iteritems())
