import requests
from dotenv import load_dotenv
import os
import http.client as httplib
import re
import math
from terminaltables import SingleTable

def look_job_sites():
    """
    Main module reads authorization data from env file and launches requests to hh.ru and superjob.ru sites
    :return: print results to the console
    """
    httplib.HTTPConnection.debuglevel = 0  # 1 -включает
    pop_languages = ['TypeScript', 'Swift', 'Scala', 'Kotlin', 'Go', 'C#',
                     'C++', '1С', 'PHP', 'Ruby', 'Python', 'JavaScript', 'Java']
    pop_languages = {lang: [{'vacancies_found': 0},
                            {'vacancies_processed': 0},
                            {'average_salary': 0},
                            {'ids': []}] for lang in pop_languages}
    pop_languages = look_superjob(pop_languages)
    print_lang_stat('SuperJob', pop_languages)
    pop_languages = {lang: [{'vacancies_found': 0},
                            {'vacancies_processed': 0},
                            {'average_salary': 0},
                            {'ids': []}] for lang in pop_languages}
    pop_languages = look_hh(pop_languages)
    print_lang_stat('HeadHunter', pop_languages)


def look_hh(pop_languages):
    job_api = 'https://api.hh.ru/vacancies'
    headers ={
    'User-Agent': 'HH-User-Agent',
    'Accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8'
    }
    key_word = 'Программист'
    area = 1
    period = 30
    page = 0
    per_page = 20
    param = {'text': key_word, 'area': area, 'period': period, 'page':page, 'per_page': per_page}
    resp = requests.get(job_api, params=param, headers=headers)
    for page in range(resp.json().get('pages')):
        param['page'] = page
        resp = requests.get(job_api, params=param, headers=headers)
        for item in resp.json().get('items'):
            if item.get('salary') is None:
                salary_cur, salary_from, salary_to = '', 0, 0
            else:
                salary_cur = '' if item.get('salary').get('currency') is None else item.get('salary').get('currency')
                salary_from = 0 if item.get('salary').get('from') is None else item.get('salary').get('from')
                salary_to = 0 if item.get('salary').get('to') is None else item.get('salary').get('to')
            match_lang(pop_languages, item.get('id'), item.get('name'), salary_from,salary_to, salary_cur)
    return pop_languages


def look_superjob(pop_languages):
    load_dotenv()
    sj_key = os.getenv('Secret_key')
    sj_client_id = os.getenv('clienr_id')
    sj_login = os.getenv('login')
    sj_pwd = os.getenv('pwd')
    headers = {
        'Host': 'api.superjob.ru',
        'X-Api-App-Id': sj_key,
        'Content-Type': 'application/json;charset=UTF-8'
    }
    api_sj = 'https://api.superjob.ru/2.0/oauth2/password'
    resp = requests.get(f'{api_sj}/?login={sj_login}&password={sj_pwd}&client_id={sj_client_id}&client_secret={sj_key}',
                        headers=headers)
    access_token = resp.json().get('access_token')
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
    return pop_languages


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


def print_lang_stat(job_site, pop_languages):
    if len(pop_languages) > 0:
        table_data = [
            ['Programming language', 'Vacancies founded', 'Vacancies processed', 'Average_salary']
        ]
        for lang in pop_languages.items():
            table_data.append([lang[0],
                               '{p[vacancies_found]}'.format(p=lang[1][0]),
                               '{p[vacancies_processed]}'.format(p=lang[1][1]),
                               '{p[average_salary]}'.format(p=lang[1][2])
                               ])
        table_instance = SingleTable(table_data, job_site.capitalize())
        table_instance.justify_columns[1] = 'right'
        table_instance.justify_columns[2] = 'right'
        table_instance.justify_columns[3] = 'right'
        print(table_instance.table)


if __name__ == '__main__':
    look_job_sites()
