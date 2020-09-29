'''
An example of the data structure, it's up to you to use it or not
'''
class DateStruct:
    def __init__(self, minute, hour, day, month, year):
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year

class ComparativeStruct:
    def __init__(self):
        # DIY
        pass

class Parser:
    def __init__(self):
        pass

    '''
    Input: a list of tokens.
    e.g., ["in", "2002"]
    '''
    def parse_phrase(self, tmp_arg):
        date_obj = self.parse_reference_date(tmp_arg)
        fuzzy_date_obj = self.parse_fuzzy_date(tmp_arg)
        duration_obj = self.parse_duration(tmp_arg)
        comparative_timepoint = self.parse_comparative_timepoint(tmp_arg)
        comparative_event = self.parse_comparative_event(tmp_arg)
        # Then do something
        # Eventually we want to return something meaningful to the caller

    '''
    Parse explicit timepoint in the timex
    e.g., 2002, February, morning, 8 AM
    '''
    def parse_reference_date(self, tmp_arg):
        return None

    '''
    Parse implicit/fuzzy timepoint in the timex
    e.g., Friday, Thanksgiving
    For you to think: how to handle things like ~last Monday~?
    '''
    def parse_fuzzy_date(self, tmp_arg):
        return None

    '''
    Parse durations in the timex, you may do it later
    e.g., for 2 hours, for 3 weeks
    '''
    def parse_duration(self, tmp_arg):
        return None

    '''
    Parse comparative timepoints
    e.g., yesterday, tomorrow, next week, 2 days ago
    '''
    def parse_comparative_timepoint(self, tmp_arg):
        return None

    '''
    Parse comparative events, you may do it later
    e.g., before I graduated
    '''
    def parse_comparative_event(self, tmp_arg):
        return None

    '''
    Add other functions / cases 
    '''