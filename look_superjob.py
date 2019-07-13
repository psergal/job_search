import requests
from dotenv import load_dotenv
import os
import http.client as httplib
import re
import math

def look_superjob():
    httplib.HTTPConnection.debuglevel = 0  # 1 -включает
    load_dotenv()
    sj_key = os.getenv('Secret_key')
    sj_client_id = os.getenv('clienr_id')
    sj_login = os.getenv('login')
    sj_pwd = os.getenv('pwd')

    pop_languages = ['TypeScript', 'Swift', 'Scala', 'Kotlin', 'Go', 'C#',
                     'C++', '1С', 'PHP', 'Ruby', 'Python', 'JavaScript', 'Java']
    pop_languages = {lang: [{'vacancies_found': 0},
                            {'vacancies_processed': 0},
                            {'average_salary': 0},
                            {'ids': []}] for lang in pop_languages}
    headers = {
    'Host': 'api.superjob.ru',
    'X-Api-App-Id': sj_key,
    'Content-Type': 'application/json;charset=UTF-8'
    }
    api_sj = 'https://api.superjob.ru/2.0/oauth2/password'
    resp = requests.get(f'{api_sj}/?login={sj_login}&password={sj_pwd}&client_id={sj_client_id}&client_secret={sj_key}',
                        headers=headers)
    access_token = resp.json().get('access_token')
    token_type = resp.json().get('token_type')
    print(resp.json().get('access_token'), resp.json().get('refresh_token'), token_type)
    headers['Authorization'] = f'Bearer {access_token}'
    api_sj = 'https://api.superjob.ru/2.0/vacancies/'
    catalogue_id_development = 48
    town_id = 4
    keyword = 'Программист'
    count = 50
    param = {'town': town_id, 'catalogues': catalogue_id_development, 'keyword': keyword, 'count': count}
    resp = requests.get(api_sj, params=param, headers=headers)
    total = int(resp.json().get('total'))
    pages = math.ceil(total//count)
    for page in range(pages+1):
        param['page'] = page
        resp = requests.get(api_sj, params=param, headers=headers)
        for vacancy in resp.json().get('objects'):
            match_lang(pop_languages,vacancy.get('id_client'), vacancy.get('profession'),
                       vacancy.get('payment_from'), vacancy.get('payment_to'), vacancy.get('currency'))

    for lang in pop_languages:
        if pop_languages[lang][1]['vacancies_processed'] > 0:
            pop_languages[lang][2]['average_salary'] = int(pop_languages[lang][2]['average_salary'] /
                                                           pop_languages[lang][1]['vacancies_processed'])
    print(pop_languages)


def match_lang(pop_languages,job_id, job_name, salary_from, salary_to, salary_cur):
    for lang, count in pop_languages.items():
        pattern = re.sub(r'C\+\+', 'C\+\+', lang)
        regex = re.compile(pattern, re.IGNORECASE)
        search_str = re.sub('1C', '1С', job_name.upper())
        search_str = re.sub(r'С\+{2}', 'C++', search_str)
        search_str = re.sub(r'С\#', 'C#', search_str)
        search_str = re.sub('JS', 'JAVASCRIPT', search_str)
        search_str = re.sub('JAVA.SCRIPT', 'JAVASCRIPT', search_str)
        search_str = re.sub('PHYTON', 'PYTHON', search_str)
        match = re.search(regex, search_str)
        if match:
            pop_languages[lang][0]['vacancies_found'] += 1
            pop_languages[lang][3]['ids'].append(job_id)
            if salary_from+salary_to > 0:
                avg_offer = predict_rub_salary(salary_from, salary_to, salary_cur)
                if avg_offer is not None:
                    pop_languages[lang][1]['vacancies_processed'] += 1
                    pop_languages[lang][2]['average_salary'] = pop_languages[lang][2]['average_salary'] + avg_offer
            return


def predict_rub_salary(salary_from, salary_to, cur):
    if cur.upper() in ('RUR', 'RUB'):
        if salary_to == 0:
            predict_salary = float(salary_from)*1.2
        elif salary_from == 0:
            predict_salary = float(salary_to)*0.8
        else:
            predict_salary = (float(salary_from)+float(salary_to))/2
        if predict_salary > 40000:
            return int(predict_salary)




if __name__ == '__main__':
    look_superjob()

