from tornado import web

def make_status_web_handler(shared_status, path, port, address=''):
    app = web.Application([
        (path, _StatusHandler, dict(shared_status=shared_status))
    ], debug=False)

    app.listen(port, address)
    return app

class _StatusHandler(web.RequestHandler):
    def initialize(self, shared_status):
        self.shared_status = shared_status

    def get(self):
        self.write(self.shared_status.as_dict())
