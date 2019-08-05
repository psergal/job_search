import requests
from dotenv import load_dotenv
import os
import http.client as httplib
import re
from terminaltables import SingleTable
from itertools import count

def look_job_sites():
    """
    Main module reads authorization data from env file and launches requests to hh.ru and superjob.ru sites
    :return: print results to the console
    """
    httplib.HTTPConnection.debuglevel = 0  # 1 -включает
    pop_languages = {
        'TypeScript': re.compile(r'TypeScript|Type.Script', re.IGNORECASE),
        'Swift': re.compile(r'Swift|Cвифт', re.IGNORECASE),
        'Scala': re.compile(r'Scala|Скала', re.IGNORECASE),
        'Kotlin': re.compile(r'Kotlin|Котлин', re.IGNORECASE),
        'Go': re.compile(r'Go|Го',re.IGNORECASE),
        'C#': re.compile(r'C#|Си.шарп', re.IGNORECASE),
        'C++': re.compile(r'C\+\+|С\+\+', re.IGNORECASE),
        '1С': re.compile(r'1С|1С', re.IGNORECASE),
        'PHP': re.compile(r'PHP|ПХП|РНР', re.IGNORECASE),
        'Ruby': re.compile(r'Ruby|Руби', re.IGNORECASE),
        'Python': re.compile(r'Python|Phyton|Питон|Пайтон', re.IGNORECASE),
        'JavaScript': re.compile(r'JavaScript|JS|Java.Script', re.IGNORECASE),
        'Java': re.compile(r'Java|Ява|Джава', re.IGNORECASE)
    }
    pop_sj_languages = look_superjob(pop_languages)
    print_lang_stat('SuperJob', pop_sj_languages)
    pop_hh_languages = look_hh(pop_languages)
    print_lang_stat('HeadHunter', pop_hh_languages)


def look_hh(pop_languages):
    pop_languages_stats = {lang: [0,0,0] for lang in pop_languages}
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
    params = {'text': key_word, 'area': area, 'period': period, 'page':page, 'per_page': per_page}
    for page in count():
        params['page'] = page
        resp = requests.get(job_api, params=params, headers=headers)
        resp.raise_for_status()
        hh_response = resp.json()
        if 'error' in hh_response:
            raise requests.exceptions.HTTPError(hh_response['error'])
        for item in hh_response['items']:
            if item.get('salary') is None:
                salary_cur, salary_from, salary_to = '', 0, 0
            else:
                salary_cur = item.get('salary').get('currency', '') or ''
                salary_from = item.get('salary').get('from', 0) or 0
                salary_to = item.get('salary').get('to', 0) or 0
            # match_lang(pop_languages_stats, item.get('id'), item.get('name'), salary_from, salary_to, salary_cur)
            match_lang = retrieve_lang(pop_languages,item.get('name'))
            if match_lang is None:
                continue
            pop_languages_stats[match_lang][0] += 1  # vacancy_founded
            if  salary_from + salary_to ==0:
                continue
            avg_offer = predict_rub_salary(salary_from, salary_to, salary_cur)
            if avg_offer is None:
                continue
            pop_languages_stats[match_lang][1] += 1  # vacancies_processed
            pop_languages_stats[match_lang][2] += avg_offer  # average_salary
        if page == hh_response['pages']-1:
            break

    for lang, statistics in pop_languages_stats.items():
        if statistics[1] > 0:
            statistics[2] = int(statistics[2] / statistics[1])
    return pop_languages_stats


def look_superjob(pop_languages):
    pop_languages_stats = {lang: [0,0,0] for lang in pop_languages}
    params ={'login': sj_login,'password': sj_pwd, 'client_id': sj_client_id, 'client_secret': sj_key}
    headers = {
        'Host': 'api.superjob.ru',
        'X-Api-App-Id': sj_key,
        'Content-Type': 'application/json;charset=UTF-8'
    }
    api_sj = 'https://api.superjob.ru/2.0/'
    sj_response = requests.get(f'{api_sj}oauth2/password/', params=params, headers=headers).json()
    if 'error' in sj_response:
        raise requests.exceptions.HTTPError(sj_response['error'])
    access_token = sj_response.get('access_token')
    headers['Authorization'] = f'Bearer {access_token}'
    catalogue_id_development = 48
    town_id = 4
    keyword = 'Программист'
    count = 50
    page = 0
    params = {'town': town_id, 'catalogues': catalogue_id_development, 'keyword': keyword, 'count': count, 'page': page}
    page, more = 0, True
    while more:
        sj_response = requests.get(f'{api_sj}vacancies', params=params, headers=headers).json()
        if 'error' in sj_response:
            raise requests.exceptions.HTTPError(sj_response['error'])
        for vacancy in sj_response['objects']:
            match_lang = retrieve_lang(pop_languages, vacancy.get('profession'))
            if match_lang is None:
                continue
            pop_languages_stats[match_lang][0] += 1  # vacancy_founded
            if vacancy.get('payment_from', 0) + vacancy.get('payment_to', 0) == 0:
                continue
            avg_offer = predict_rub_salary(vacancy.get('payment_from', 0),
                                           vacancy.get('payment_to', 0),
                                           vacancy.get('currency', '')
                                           )
            if avg_offer is None:
                continue
            pop_languages_stats[match_lang][1] += 1  # vacancies_processed
            pop_languages_stats[match_lang][2] += avg_offer  # average_salary
        more = sj_response['more']
        params['page'] += 1

    for lang, statistics in pop_languages_stats.items():
        if statistics[1] > 0:
            statistics[2] = int(statistics[2] / statistics[1])
    return pop_languages_stats


def retrieve_lang(pop_languages, job_name):
    for lang, pattern in pop_languages.items():
        match = re.search(pattern, job_name)
        if match:
            return lang


def predict_rub_salary(salary_from, salary_to, cur):
    if not cur.upper() in ('RUR', 'RUB'):
        return
    if salary_to == 0:
        predict_salary = float(salary_from)*1.2
    elif salary_from == 0:
        predict_salary = float(salary_to)*0.8
    else:
        predict_salary = (float(salary_from)+float(salary_to))/2
    if predict_salary > 40000:
        return int(predict_salary)


def print_lang_stat(job_site, pop_languages):
    if not pop_languages:
        return
    table_data = [
        ['Programming language', 'Vacancies founded', 'Vacancies processed', 'Average_salary']
    ]
    for lang, statistics in pop_languages.items():
        table_data.append([lang,
                           '{p[0]}'.format(p=statistics),
                           '{p[1]}'.format(p=statistics),
                           '{p[2]}'.format(p=statistics)
                           ])
    table_instance = SingleTable(table_data, job_site.capitalize())
    table_instance.justify_columns = dict(zip(range(1, 4), ['right']*3))
    print(table_instance.table)


if __name__ == '__main__':
    load_dotenv()
    sj_key = os.getenv('SJ_SECRET_KEY')
    sj_client_id = os.getenv('SJ_CLIENT_ID')
    sj_login = os.getenv('SJ_LOGIN')
    sj_pwd = os.getenv('SJ_PWD')
    look_job_sites()
