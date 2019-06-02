import requests
import json
import re

def look_for_job():
    job_api = 'https://api.hh.ru'
    headers ={
        'User-Agent': 'HH-User-Agent',
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
    }
    v = 'vacancies'
    s = 'text'
    a = 'area'
    p = 'period'
    id = '29443519'
    spec_key = '?specialization=Банковское ПО'
    pop_languages = ['TypeScript', 'Swift', 'Scala', 'Kotlin', 'Go', 'C#',
                'C++', '1С', 'C', 'PHP', 'Ruby', 'Python', 'Java', 'JavaScript']
    pop_languages = {lang: 0 for lang in pop_languages}
    # resp = requests.get(f'{job_api}/{v}/{id}', headers=headers)
    resp = requests.get(f'{job_api}/{v}?{s}=Программист&{a}=1&{p}=30&page=0&per_page=20', headers=headers)
    for page in range(resp.json().get('pages')):
        resp = requests.get(f'{job_api}/{v}?{s}=Программист&{a}=1&{p}=30&page={page}&per_page=20', headers=headers)
        for item in resp.json().get('items'):
            for lang, count in pop_languages.items():
                pattern = re.sub(r'C\+\+', 'C\+\+', lang)
                regex = re.compile(pattern, re.IGNORECASE)
                search_str = re.sub('1C', '1С', item.get('name'))
                search_str = re.sub(r'С\+{2}', 'C++', search_str)
                search_str = re.sub(r'С\#', 'C#', search_str)
                match = re.search(regex, search_str)
                if match:
                    pop_languages[lang] = count+1
                    break
    print(pop_languages)

if __name__ == '__main__':
    look_for_job()
