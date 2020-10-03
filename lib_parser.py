import parser 
import re
'''
An example of the data structure, it's up to you to use it or not
'''
class TimeStruct:
    def __init__(self, minute, hour, day, month, year):
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year
    
    def __str__(self):
        return "{} {} {} {}:{}".format(str(self.year), str(self.month), str(self.day), str(self.hour), str(self.minute))


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
    months = {'januray': 1, 'jan':1, 'feburary':2, 'feb':2, 'march':3,'mar':3,'april':4,'apr':4,'may':5,'june':6,'jun':6,'july':7,'jul':7,'august':8,'aug':8,'september':9,'sep':9,'october':10,'oct':10,'november':11,'nov':11,'december':12,'dec':12}
    '''
    Parse explicit timepoint in the timex
    e.g., 2002, February, morning, 8 AM
    '''
            
    def parse_reference_date(self, tmp_arg):
        months = {'januray': 1, 'jan':1, 'feburary':2, 'feb':2, 'march':3,'mar':3,'april':4,'apr':4,'may':5,'june':6,'jun':6,'july':7,'jul':7,'august':8,'aug':8,'september':9,'sep':9,'october':10,'oct':10,'november':11,'nov':11,'december':12,'dec':12}
        result = TimeStruct(None,None,None,None,None)
        if 'in' in tmp_arg:
            result = parser.extract_in(tmp_arg)
        elif 'at' in tmp_arg:
            result = parser.extract_at(tmp_arg)
        elif 'on' in tmp_arg:
            result = parser.extract_on(tmp_arg)
        
        year = None
        month = None
        day = None
        timeh = None
        timem = None
        dateameric = re.compile("^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]|(?:Jan|Mar|May|Jul|Aug|Oct|Dec)))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2]|(?:Jan|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)(?:0?2|(?:Feb))\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9]|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep))|(?:1[0-2]|(?:Oct|Nov|Dec)))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$")
        for i, x in enumerate(tmp_arg):
            try:
                float(x)
                if result.year is None and int(x) > 1000 and int(x) < 3000:
                    year = x
                    print(year)
                if result.day is None and int(x) < 32:
                    day = x
                    print(day)
            except ValueError:
                if result.month is None and x in months:
                    month = months[x]
                if (result.day is None) and (x.endswith('th') or x.endswith('st') or x.endswith('nd')):
                    day = x[:-2]
                if dateameric.match(x):
                    if len(x.split('/')) > 1:
                        if(len(x.split('/'))== 2):
                            # TODO create regex that will accept 04/02
                            month = x[0]
                            year = x[1]
                        elif(len(x.split('/')) == 3):
                            day = x[0]
                            month = x[1]
                            year = x[2]
        if year is not None:
            result.year = year 
        if day is not None:
            result.day = day
        if month is not None:
            result.month = month
        


        return result
            
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

