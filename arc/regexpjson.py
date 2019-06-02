import json
import re
# 1С  по русски
pop_jobs = ['TypeScript', 'Swift', 'Scala', 'Objective-C', 'Shell', 'Go', 'C#', 'C++', '1С', 'C', 'PHP', 'Ruby', 'Python', 'Java', 'JavaScript']
# pop_jobs = ['C#', 'C++', '1С', 'C']
pop_jobs = {job: 0 for job in pop_jobs}

with open('hh1.json', 'r',encoding='utf8') as hh:
    sfile = json.load(hh)

for item in sfile.get('items'):
    # print(item.get('id'),item.get('name'))
    Match = False
    for job, count in pop_jobs.items():
        pattern = re.sub(r'C\+\+', 'C\+\+', job)
        regex = re.compile(pattern, re.IGNORECASE)
        search_str= re.sub('1C', '1С', item.get('name'))
        search_str= re.sub(r'С\+{2}', 'C++', search_str)
        search_str= re.sub(r'С\#', 'C#', search_str)
        match = re.search(regex, search_str)
        if match:
            pop_jobs[job] = count+1
            # print(regex,'---', job, pop_jobs[job])
            break
print(pop_jobs)
