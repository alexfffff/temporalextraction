import requests 
import re
import xml.etree.ElementTree as ET 
from bs4 import BeautifulSoup
import os
import xml.dom.minidom
from xml.dom import minidom 
import lib_parser
from datetime import datetime

#brought over march 8 check for updates 
class EventObject:
    def __init__(self,location,verb,absolute_time = None, comparison_time = None,related_events = None):
        self.location = location 
        self.verb = verb
        self.absolute_time = absolute_time
        self.comparison_time = comparison_time
        self.related_events = related_events
    def __str__(self):
        return "{} {} {} {} {}".format(str(self.location), str(self.verb), str(self.absolute_time), str(self.comparison_time),str(self.related_events))

class TimeStruct:
    def __init__(self, minute, hour, day, month, year):
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.year = year
        self.second = 0
    
    def __str__(self):
        return "({} {} {} {}:{}, {})".format(str(self.year), str(self.month), str(self.day), str(self.hour), str(self.minute),str(self.second))
    def get_date(self):
        convert_map = {
            "second": 1.0,
            "seconds": 1.0,
            "minute": 60.0,
            "minutes": 60.0,
            "hour": 60.0 * 60.0,
            "hours": 60.0 * 60.0,
            "day": 24.0 * 60.0 * 60.0,
            "days": 24.0 * 60.0 * 60.0,
            "week": 7.0 * 24.0 * 60.0 * 60.0,
            "weeks": 7.0 * 24.0 * 60.0 * 60.0,
            "month": 30.0 * 24.0 * 60.0 * 60.0,
            "months": 30.0 * 24.0 * 60.0 * 60.0,
            "year": 365.0 * 24.0 * 60.0 * 60.0,
            "years": 365.0 * 24.0 * 60.0 * 60.0,
            "decade": 10.0 * 365.0 * 24.0 * 60.0 * 60.0,
            "decades": 10.0 * 365.0 * 24.0 * 60.0 * 60.0,
            "century": 100.0 * 365.0 * 24.0 * 60.0 * 60.0,
            "centuries": 100.0 * 365.0 * 24.0 * 60.0 * 60.0,
        }
        array = []
        if self.year == None:
            array.append(0)
        else:
            array.append(self.year)
        if self.month == None:
            array.append(0)
        else:
            array.append(self.month)
        if self.day == None:
            array.append(0)
        else:
            array.append(self.day)
        if self.hour == None:
            array.append(0)
        else:
            array.append(self.hour)
        if self.minute == None:
            array.append(0)
        else:
            array.append(self.minute)
        try:
            if self.second == None:
                array.append(0)
            else:
                array.append(self.second)
        except AttributeError:
            array.append(0)

        return array[0] * convert_map['years'] + (array[1]) * convert_map['months']+ array[2] * convert_map['days']  + array[3] * convert_map['hours'] + array[4] * convert_map['minutes'] + array[5]

    def is_empty(self):
        if self == None:
            return True
        return (self.year or self.day or self.month or self.hour or self.minute) == None

    def subtract(self,compare):
        # TODO we only want to subtract the things that they share, october 26 2002 and october 27 is most likeley just 1 day apart. 
        return TimeStruct.get_date(compare) - TimeStruct.get_date(self)

        return compare.get_date - self.get_date

    def copy(self):
        x = TimeStruct(self.minute, self.hour,self.day,self.month,self.year)
        return x
    
    


def read_file(filename): 
    import codecs
    fileObj = codecs.open( filename, "r", "utf-8" )
    filetext = fileObj.read()
    fileObj.close() 
    ## changing .</TIMEX3> to </TIMEX3>. for all cases 
    filetext = re.sub('&quot;', '"', filetext) 

    return filetext

def get_text(filetext): 
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString( filetext.encode( "utf-8" ) )
    xmlTag = dom.getElementsByTagName('TEXT')[0].toxml()
    xmlData=xmlTag.replace('<TEXT>\n','').replace('</TEXT>','')
    xmlData = re.sub('&quot;', '"', xmlData) 
    return xmlData, filetext  

def correct_annotation(filetext): 
    "if there are some tags in the middle of the word, this function puts the tag outside of the word, e.g. re-<EVENT>emerged</EVENT> => <EVENT>re-emerged</EVENT>" 
    new_text = '' 
    prev = '' 
    after_bl = '' 
    for line in filetext.split('\n'):
        if re.search('<(EVENT|TIMEX)[^>]*>', line): 
            if prev != '<internal_BL>' and prev != '<internal_NL>' and re.search('[\-]+', prev):
                tmp_foo = '' 
                entities = re.findall('<[a-zA-Z][^>]*>', line) 
                for each in entities: 
                    tmp_foo += each 
                tmp_foo += re.sub('\n', '', after_bl) 
                tmp_foo += re.sub('<[a-zA-Z][^>]*>', '', line) 
                after_bl = '' 
                line = tmp_foo 

        after_bl += line + '\n' 
        if line == '<internal_BL>' or line == '<internal_NL>': 
            new_text += after_bl 
            after_bl = '' 
        prev = line 
    new_text += after_bl 
    return new_text  

'''
takes in a file name and returns a set of timestruct o
'''
def parse_text(filename,debug):

    try:
        print(f"checking {filename}")
        data, text = get_text(read_file(filename))
        data = correct_annotation(data)
        array = data.split('\n\n')
        narray = []
        finalarray = []
        for x in array:
            temp = x.replace("\n","")
            temp = re.sub(' +', ' ', temp)
            narray.append(re.split("<|>",temp))
        events = {}
        timex = {}
        reverse = {}
        dct = {}
        for sentence in narray:
            sentencearray = []
            for x in sentence:
                # if the element is a timx of event identifier 
                if re.search("EVENT", x ) or re.search("TIMEX3",x):
                    if x[0] != '/':
                        temp = x.split(" ")
                        dic = {}
                        if temp[0] == "EVENT":
                            eclass = temp[1].replace('"','').split("=")
                            eid = temp[2].replace('"','').split("=")
                            #DEBUG
                            if eclass[0] != "class":
                                print("another error wtf" + eclass[0])
                            dic["eid"] = eid[1]
                            dic['class'] = eclass[1]
                            events[(len(finalarray),len(sentencearray))] = dic
                            reverse[eid[1]] = (len(finalarray),len(sentencearray))
                        elif temp[0] == "TIMEX3":
                            for n in temp[1:]:
                                tinfo = n.replace('"','').split("=")
                                dic[tinfo[0]] = tinfo[1]
                            timex[(len(finalarray),len(sentencearray))] = dic
                            reverse[dic['tid']] = (len(finalarray),len(sentencearray))
                        else:
                            #DEBUG
                            print("oh nooooooo error:" + temp[0])
                #if it is normal word 
                else:
                    temp = x.replace("\n","")
                    temp = re.sub(' +', ' ', temp)
                    temp = re.sub(r'[^\w\s]', '', temp) 
                    if len(temp) > 0:
                        temp = temp.split(" ")
                        for i,x in enumerate(temp):
                            if len(x) == 0:
                                temp.pop(i)
                            if len(x) == 1:
                                if x.lower() != "i" and x.lower() != "a":
                                    temp.pop(i)
                        if '' not in temp:
                            sentencearray = sentencearray + temp
                        
                    
            if len(sentencearray) != 0:
                finalarray.append(sentencearray)





        # gold standard 
        graph = {}
        for x in events:
            graph[x] = EventObject(x,finalarray[x[0]][x[1]])
        import xml.etree.ElementTree as ET
        tree = ET.parse(filename)
        root = tree.getroot()
        for child in root:
            if child.tag == "DCT":
                for time in child:
                    dct = time.attrib
            if child.tag == "TLINK":
                # debug
                if child.attrib.get('eventInstanceID'):
                    eid = reverse[child.attrib.get('eventInstanceID').replace('i','')]
                    if child.attrib.get('relatedToEventInstance'):
                        # coreference
                        related  = reverse[child.attrib.get('relatedToEventInstance').replace('i','')]
                        if (related[0] == eid[0]):
                            if graph[eid].comparison_time:
                                graph[eid].comparison_time.append(related)
                            else:
                                graph[eid].comparison_time = [related]
                    elif child.attrib.get('relatedToTime'):
                        reltype = child.attrib.get("relType")
                        if  reltype == "INCLUDES" or reltype == "IS_INCLUDED" or reltype == "SIMULTANEOUS":
                            if child.attrib.get('relatedToTime') == 't0':
                                date = dct['value'].split("-")
                                graph[eid].absolute_time = TimeStruct(0,0,date[2],date[1],date[0])
                            
                            else:
                                related = reverse[child.attrib.get('relatedToTime')]
                                if (related[0] == eid[0]):
                                    if timex[related]['type'] == "DATE":
                                        if timex[related]['value'] == "PRESENT_REF":
                                            date = dct['value'].split("-")
                                        else:
                                            date = timex[related]['value'].split("-")
                                        if len(date) == 1:
                                            graph[eid].absolute_time = TimeStruct(0,0,0,0,date[0])
                                        elif len(date) == 2:
                                            graph[eid].absolute_time = TimeStruct(0,0,0,date[1],date[0])
                                        else:
                                            graph[eid].absolute_time = TimeStruct(0,0,date[2],date[1],date[0])
        # prediction        
        srl = lib_parser.AllenSRL()
        if dct["type"] == 'DATE':
            tempdatetime = datetime.strptime(dct['value'], '%Y-%m-%d')
            doctime = TimeStruct(None,None,tempdatetime.day,tempdatetime.month,tempdatetime.year)
        else:
            print(f"there is no dct? check this one {filename}")
            doctime = TimeStruct(None,None,0,0,0)
        srl.get_graph(finalarray,doctime,False)
        count_p = 0
        count_g = 0
        count_t = 0
        count_c = 0
        for x in srl.graph:
            if x in events:
                eventp = srl.graph[x]
                eventg = graph[x]
                check = []
                if eventp.absolute_time != None and eventg.absolute_time != None:
                    count_t = count_t+ 1
                    if eventp.absolute_time.year != None and eventg.absolute_time.year != "XXXX":
                        if eventp.absolute_time.year == int(float(eventg.absolute_time.year)):
                            check.append(1)
                        else: 
                            check.append(0)
                    if eventp.absolute_time.month != None and eventg.absolute_time.month != "XX":
                        if eventp.absolute_time.month == int(float(eventg.absolute_time.month)):
                            check.append(1)
                        else:
                            check.append(0)
                    if eventp.absolute_time.day != None and eventg.absolute_time.day != "XX":
                        if eventp.absolute_time.day == int(float(eventg.absolute_time.day)):
                            check.append(1)
                        else:
                            check.apennd(0)
                    
                    if sum(check) == 0:
                        print("got it all wrong rip")
                        print(eventg,eventp)
                    elif sum(check) == len(check):
                        count_c = count_c + 1
                    else:
                        print(eventp.absolute_time,eventg.absolute_time)

                if eventg.absolute_time != None:
                    if eventp.absolute_time == None:
                        1+1
                        #print(eventp.absolute_time,eventg.absolute_time)
                    count_g = count_g + 1
                if eventp.absolute_time != None:
                    count_p = count_p + 1
        if debug:
            for x in events:
                # gold stanard 
                print(graph[x])
                if x in srl.graph:
                    # prediction
                    print(srl.graph[x])
        print(f"gold:{count_g}, pred:{count_p}, both:{count_t}, correct: {count_c}")
        return count_g, count_p, count_t, count_c
    except Exception as e: 
        print(f"this {filename} has a weird thing {e}________________________")
        return 0,0,0,0
    
if __name__ == "__main__":                     
    parse_text('evaluation/Evaluation/te3-platinum/nyt_20130321_women_senate.tml',True)



