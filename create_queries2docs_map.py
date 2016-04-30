
import re, xmltodict, json
from os import listdir
from os.path import isfile, join

#READ THE GOODNESS
queries = open("testRunOut/query", "r").read()
queries_d = xmltodict.parse(queries)

bugs = open("SWTBugRepository.xml", "r").read()
bugs_d = xmltodict.parse(bugs)

docs_path = "testRunOut/docs/"
docs_files = [f for f in listdir(docs_path) if isfile(join(docs_path, f))]
docs_str_d = { d : open("testRunOut/docs/"+d, "r").read() for d in docs_files }
docs_d = { d : xmltodict.parse(docs_str_d[d]) for d in docs_files }

#CHECK THOSE TURDS
#json.dumps(bugs_d)
#json.dumps(queries_d)
#json.dumps(docs_d)

#CLEAN THAT SHITE
bug_map = {}
for b in bugs_d['bugrepository']['bug']:
    if type(b['fixedFiles']['file']) is not list:
        file_list = [b['fixedFiles']['file']]
    else:
        file_list = b['fixedFiles']['file']
    bug_map[b['@id']] =  file_list #number -> files
#json.dumps(bug_map)

query_map = {}
c = re.compile(r"(\S+)\.\(class\)")
m = re.compile(r"(\S+)\.\(method\)")
i = re.compile(r"(\S+)\.\(identifier\)") 
o = re.compile(r"(\S+)\.\(comments\)")
for q in queries_d['parameters']['query']:
    text = q['text']
    c_l = list(set(c.findall(text)))
    m_l = list(set(m.findall(text)))
    i_l = list(set(i.findall(text)))
    o_l = list(set(o.findall(text)))
    query_map[q['number']] = {'class':c_l, 'method':m_l, 'identifier':i_l, 'comments':o_l}
#json.dumps(query_map)   

docs_map = {}
for _id in docs_d:
    _file = docs_d[_id]['DOC']['DOCNO']
    
    c = docs_d[_id]['DOC']['text']['class'] #WTF ... org.eclipse.swt.internal.win32.OS.java <class> is empty
    if c is None: c = ''
    
    c_l = list(set(c.split()))
    m_l = list(set(docs_d[_id]['DOC']['text']['method'].split()))
    i_l = list(set(docs_d[_id]['DOC']['text']['identifier'].split()))
    o_l = list(set(docs_d[_id]['DOC']['text']['comments'].split())) 
    docs_map[_file] = {'class':c_l, 'method':m_l, 'identifier':i_l, 'comments':o_l}


#json.dumps(docs_map)       

bug_report_sentences = {'class': [], 'method': [], 'identifier': [], 'comments': []}
fixed_file_sentences = {'class': [], 'method': [], 'identifier': [], 'comments': []}

for bug_id in bug_map:
    for fixed_file in bug_map[bug_id]:
        for field in docs_map[fixed_file]:
            bug_report_sentences[field].append(query_map[bug_id][field])
            fixed_file_sentences[field].append(docs_map[fixed_file][field])


#save as json file                
with open('bug_report_sentences.txt', 'w') as outfile:
     json.dump(bug_report_sentences, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
     
with open('fixed_file_sentences.txt', 'w') as outfile:
     json.dump(fixed_file_sentences, outfile, sort_keys = True, indent = 4, ensure_ascii=False)




