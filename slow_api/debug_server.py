from gunicorn.app.base import BaseApplication


class DebugServer(BaseApplication):
    """Class to run Gunicorn Server in a python process for debugging"""

    def init(self, parser, opts, args):
        pass

    def __init__(self, application, server="127.0.0.1", port="8000", workers=1):
        self.options = {"bind": f"{server}:{port}", "workers": workers}
        self.application = application
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
