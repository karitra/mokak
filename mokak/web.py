from tornado import web


def make_status_web_handler(shared_status, path, port, address=''):
    app = web.Application([
        (path, _StatusHandler, dict(shared_status=shared_status))
    ], debug=False)

    app.listen(port, address)
    return app


class _StatusHandler(web.RequestHandler):
    TASK_NAME = 'status_handler'

    def initialize(self, shared_status):
        self.shared_status = shared_status
        self.status = shared_status.register(_StatusHandler.TASK_NAME)
        self.requests_count = 0

    def get(self):
        self._inc_count()
        self.write(self.shared_status.as_dict())
        self._drop_count()

    def _inc_count(self):
        self.requests_count += 1
        self._mark_ok()

    def _drop_count(self):
        self.requests_count -= 1
        if self.requests_count <= 0:
            self.requests_count = 0
            self.status.mark_ok('idle')
        else:
            self._mark_ok()

    def _mark_ok(self):
        self.status.mark_ok(
            'processing {} request(s)'.format(self.requests_count))
