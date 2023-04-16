class DryRunner:

    def __init__(self, dry_run):
        self.dry_run = dry_run

    def run(self, func, *args, **kwargs):
        func(*args, **kwargs, dry_run=self.dry_run)
