import requests 
import re
import xml.etree.ElementTree as ET 
from bs4 import BeautifulSoup
import lib_parser
import os
from evaluation_timex import parse_text

# evaulates 
directory = "evaluation/Evaluation/te3-platinum"
total_p = 0
total_g = 0 
total_t = 0
total_c = 0
for file in os.listdir(directory):
    filename = os.fsdecode(file)

    if filename.endswith(".tml"):
        count_g,count_p,count_t,count_c = parse_text(directory + "/"  + filename,False)
        total_p += count_p
        total_g += count_g
        total_t += count_t
        total_c += count_c
    else: 
        continue
print(f"gold:{total_g}, pred:{total_p}, both:{total_t}, correct: {total_c}")

 




# for file in os.listdir(directory):
#     filename = os.fsdecode(file)
#     if filename.endswith(".tml"):
#         with open(os.path.join(directory, filename), 'r') as f:
#             contents = f.read() 
#             soup = BeautifulSoup(contents, 'lxml')
#             #take only the elements in the text tag
#             array = soup.text.split('\n\n')
#             newarray = []
#             for x in array[1:]:
#                 if len(x) > 0:
#                     #remove the next lines and + and spaces and white space
#                     temp = x.replace("\n","")
#                     temp = re.sub(' +', ' ', temp)
#                     temp = re.sub(r'[^\w\s]', '', temp) 
#                     if len(temp) > 0:
#                         temp = temp.split(" ")
#                         if( '' in temp):
#                             temp.remove('')
#                             if ('' in temp):
#                                 temp.remove('')

#                         newarray.append(temp)
#             srl = lib_parser.AllenSRL()
#             doctime = lib_parser.TimeStruct(None,None,None,None,2002)
#             srl.get_graph(newarray,doctime)
#     else:
#         continue
