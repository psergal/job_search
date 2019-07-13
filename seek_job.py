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
    Key_word = 'Программист'

    pop_languages = ['TypeScript', 'Swift', 'Scala', 'Kotlin', 'Go', 'C#',
                    'C++', '1С', 'PHP', 'Ruby', 'Python', 'JavaScript', 'Java']
    pop_languages = {lang: [{'vacancies_found': 0},
                            {'vacancies_processed': 0},
                            {'average_salary': 0},
                            {'ids': []}] for lang in pop_languages}
    resp = requests.get(f'{job_api}/{v}?{s}={Key_word}&{a}=1&{p}=30&page=0&per_page=20', headers=headers)
    for page in range(resp.json().get('pages')):
        resp = requests.get(f'{job_api}/{v}?{s}={Key_word}&{a}=1&{p}=30&page={page}&per_page=20', headers=headers)
        for item in resp.json().get('items'):
            match_lang(item.get('id'), item.get('name'),item.get('salary'), pop_languages)

    for lang in pop_languages:
        if pop_languages[lang][1]['vacancies_processed'] > 0:
            pop_languages[lang][2]['average_salary'] = int(pop_languages[lang][2]['average_salary'] /
                                                           pop_languages[lang][1]['vacancies_processed'])
    print(pop_languages)


def match_lang(job_id, job_name, salary, pop_languages):
    for lang, count in pop_languages.items():
        pattern = re.sub(r'C\+\+', 'C\+\+', lang)
        regex = re.compile(pattern, re.IGNORECASE)
        search_str = re.sub('1C', '1С', job_name)
        search_str = re.sub(r'С\+{2}', 'C++', search_str)
        search_str = re.sub(r'С\#', 'C#', search_str)
        search_str = re.sub('JS', 'JavaScript', search_str)
        match = re.search(regex, search_str)
        if match:
            pop_languages[lang][0]['vacancies_found'] += 1
            pop_languages[lang][3]['ids'].append(job_id)
            if salary is not None:
                avg_offer = predict_rub_salary(salary)
                if avg_offer is not None:
                    pop_languages[lang][1]['vacancies_processed'] += 1
                    pop_languages[lang][2]['average_salary'] = pop_languages[lang][2]['average_salary'] + avg_offer
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
