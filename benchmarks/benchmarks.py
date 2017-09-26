import gnss.coord_system as cs

class TimeSuite:
    """
    An example benchmark that times the performance of various kinds
    of iterating over dictionaries in Python.
    """
    def setup(self):
        self.a = (38., 122., 0.)

    def time_to_ecef(self):
        cs.ecef_from_llh(self.a)
