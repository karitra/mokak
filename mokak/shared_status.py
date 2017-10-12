import time
from collections import namedtuple


TRIM_DESC_LIMIT = 180


def _int_seconds_from_epoch():
    return int(time.time())


def _norm_desc(desc, limit=TRIM_DESC_LIMIT):
    if len(desc) > limit:
        desc = desc[:limit]
    # TODO: correct to allowed symbols ''^[0-9a-Z ]{0,180}$'
    return desc


class _FieldsNames(object):
    STATUS = 'status'
    LAST_UPDATE = 'last_update'
    EXTENDEND_STATUS = 'extendend_status'
    DESC = 'desc'
    NAME = 'name'


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
        desc = _norm_desc(desc)
        self.shared_status.mark_submodule_status(
            self.name, _StatusHandler.Status(_StatusHandler.OK_STATUS, desc)
        )

    def mark_warn(self, desc):
        desc = _norm_desc(desc)
        self.shared_status.mark_submodule_status(
            self.name, _StatusHandler.Status(_StatusHandler.WARN_STATUS, desc)
        )

    def mark_crit(self, desc):
        desc = _norm_desc(desc)
        self.shared_status.mark_submodule_status(
            self.name, _StatusHandler.Status(_StatusHandler.CRIT_STATUS, desc)
        )


class SharedStatus(object):
    def __init__(self, name=None):
        self.status = dict(last_update=_int_seconds_from_epoch())
        self.submodules_status = dict()

        if name:
            self.status[_FieldsNames.NAME] = name

    def register(self, name):
        hnd = _StatusHandler(self, name)
        hnd.mark_ok('init done')

        return hnd

    def mark_submodule_status(self, submodule_name, status):
        self.status[_FieldsNames.LAST_UPDATE] = _int_seconds_from_epoch()
        self.submodules_status[submodule_name] = status

    def as_dict(self):
        crit_submod = self._has_status(_StatusHandler.CRIT_STATUS)
        warn_submod = self._has_status(_StatusHandler.WARN_STATUS)

        status = _StatusHandler.OK_STATUS
        desc = 'system healthy and running'
        if crit_submod:
            status = _StatusHandler.CRIT_STATUS
            desc = 'critical errors in ' + ' '.join(crit_submod)
        elif warn_submod:
            status = _StatusHandler.WARN_STATUS
            desc = 'warnings in ' + ' '.join(warn_submod)

        self.status[_FieldsNames.STATUS] = status
        self.status[_FieldsNames.DESC] = desc

        extendend_status = {
            submodule_name: status._asdict()
            for submodule_name, status in self.submodules_status.iteritems()
        }

        return dict(
            self.status, **{_FieldsNames.EXTENDEND_STATUS: extendend_status})

    def _has_status(self, status):
        return [
            module
            for module, st in self.submodules_status.iteritems()
            if st.status == status
        ]
