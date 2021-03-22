from time import perf_counter_ns


class MonitorPerformance:
    def __init__(self, do_print, to_print=""):
        self.start_time = None
        self.end_time = None
        self.do_print = do_print
        self.to_print = to_print

    def __enter__(self):
        self.start_time = perf_counter_ns()

    def __exit__(self, type, value, tb):
        self.end_time = perf_counter_ns()
        if self.do_print:
            print(self.to_print + " {:.2f}".format((self.end_time - self.start_time) * 10**-9) + "s")
