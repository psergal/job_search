import requests
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
    id = '31646032'
    Key_word = 'Программист'
    Key_Lang = 'Python'
    ws = 'only_with_salary'

    pop_languages = ['TypeScript', 'Swift', 'Scala', 'Kotlin', 'Go', 'C#',
                'C++', '1С', 'PHP', 'Ruby', 'Python', 'JavaScript', 'Java']
    pop_languages = {lang: [{'vacancies_found': 0}, {'ids': []}] for lang in pop_languages}
    resp = requests.get(f'{job_api}/{v}/{id}', headers=headers)
    resp = requests.get(f'{job_api}/{v}?{s}={Key_word}&{a}=1&{p}=30&page=0&per_page=20', headers=headers)
    for page in range(resp.json().get('pages')):
        resp = requests.get(f'{job_api}/{v}?{s}={Key_word}&{a}=1&{p}=30&page={page}&per_page=20', headers=headers)
        for item in resp.json().get('items'):
            match_lang(item.get('id'), item.get('name'), pop_languages)
    print(pop_languages)

    # resp = requests.get(f'{job_api}/{v}?{s}={Key_Lang}&{a}=1&{p}=30&{ws}=True&page=0&per_page=20', headers=headers)
    # for item in resp.json().get('items'):
    #     print(item.get('salary'))
    #     avg_offer = predict_rub_salary(item.get('salary'))
    #     print(f'Average {Key_Lang} offer is: {avg_offer}')

def match_lang(job_id, job_name, pop_languages):
    for lang, count in pop_languages.items():
        pattern = re.sub(r'C\+\+', 'C\+\+', lang)
        regex = re.compile(pattern, re.IGNORECASE)
        search_str = re.sub('1C', '1С', job_name)
        search_str = re.sub(r'С\+{2}', 'C++', search_str)
        search_str = re.sub(r'С\#', 'C#', search_str)
        search_str= re.sub('JS', 'JavaScript', search_str)
        match = re.search(regex, search_str)
        if match:
            pop_languages[lang][0]['vacancies_found'] += 1
            pop_languages[lang][1]['ids'].append(job_id)
            return


def predict_rub_salary(salary):
    if salary.get('currency') == 'RUR':
        if salary.get('to') is None:
            predict_salary = float(salary.get('from'))*1.2
        elif salary.get('from') is None:
            predict_salary = float(salary.get('to'))*0.8
        else:
            predict_salary = (float(salary.get('from'))+float(salary.get('to')))/2
        if predict_salary > 40000:
            return int(predict_salary)



if __name__ == '__main__':
    look_for_job()
