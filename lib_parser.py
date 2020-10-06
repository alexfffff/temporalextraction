import parser 
import re
from allennlp.models.archival import load_archive
from allennlp.predictors import Predictor
from datetime import date
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
class PretrainedModel:
    """
    A pretrained model is determined by both an archive file
    (representing the trained model)
    and a choice of predictor.
    """
    def __init__(self, archive_file: str, predictor_name: str) -> None:
        self.archive_file = archive_file
        self.predictor_name = predictor_name

    def predictor(self) -> Predictor:
        archive = load_archive(self.archive_file)
        return Predictor.from_archive(archive, self.predictor_name)

class AllenSRL:

    def __init__(self):
        model = PretrainedModel('https://s3-us-west-2.amazonaws.com/allennlp/models/srl-model-2018.05.25.tar.gz',
        #model = PretrainedModel('model.tar.gz',
                                'semantic-role-labeling')
        self.predictor = model.predictor()
        #self.predictor._model = self.predictor._model.cuda()
        #self.output_path = output_path

    def get_temporal_arguments(self,words, tags):
        ret = []
        for i, t in enumerate(tags):
            if t == "B-ARGM-TMP":
                end = i + 1
                for j in range(i+1, len(tags)):
                    if tags[j] == "I-ARGM-TMP":
                        end = j + 1
                    else:
                        break
                ret.append(words[i:end])
        return ret
    '''
    takes a sentence as a array, and the index of the target verb. 
    returns the timestructure of the predicted time that the verb happened
    '''
    def predict(self,tokens,verbindex):
        parser = Parser()
        prediction = self.predictor.predict_tokenized(tokens)
        words = prediction['words']
        # figure out which duplicate the verb is
        verb = words[verbindex]
        number = 0
        tempargs = []
        for i, x in enumerate(tokens):
            if x == verb and i != verbindex:
                number += 1
            elif i == verbindex:
                number += 1
                break
        
        # gets the temparg of the verb
        counter = 0
        for i in prediction['verbs']:
            if i['verb'] == verb:
                counter += 1
            if counter == number:
                tempargs = self.get_temporal_arguments(words,i['tags'])
                print(tempargs)
                if len(tempargs) == 0:
                    return None
                else:
                    return parser.parse_reference_date(tempargs[0])


    '''
    takes the target timestruct and today and replaces the args that are non in the timestruct with today
    returns the updated timestruct
    '''
    def replace(self,temargs,today):
        if temargs == None:
            return None
        if temargs.year == None:
            temargs.year = today.year
        if temargs.month == None:
            temargs.month = today.month
        if temargs.day == None:
            temargs.day = today.day
        return temargs
    '''
    takes the verb index for both verbs (x,y) where x is the index of sentence and y is the index of verb in sentence
    returns the time difference between the two. 
    '''
    

    def comparison_predict(self,tokens,verbix1,verbix2):
        temp = date.today()
        today = TimeStruct(None,None,temp.day,temp.month,temp.year)
        sen1 = tokens[verbix1[0]]
        sen2 = tokens[verbix2[0]]
        temparg1 = self.replace(self.predict(sen1,verbix1[1]),today)
        temparg2 = self.replace(self.predict(sen2,verbix2[1]),today)
        if temparg1 == None or temparg2 == None:
            return None
        else: 
            time1 = temparg1.year + (temparg1.month - 1) /12 + (temparg1.day) / 365
            time2 = temparg2.year + (temparg2.month - 1) /12 + (temparg2.day) / 365
        return time1<time2




        
    

        
        


        
srl = AllenSRL()
print(srl.comparison_predict(["I ate dinner on october 26 2002".split(" "),"I ran outside on october 25 2002".split(" ")],(0,1),(1,1)))
