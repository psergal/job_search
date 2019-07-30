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
        'TypeScript': ['TypeScript', 'Type.Script'],
        'Swift': ['Swift', 'Cвифт'],
        'Scala': ['Scala', 'Скала'],
        'Kotlin': ['Kotlin', 'Котлин'],
        'Go': ['Go', 'Го'],
        'C#': ['C#', 'Си.шарп'],
        'C++': ['C\+\+', 'С\+\+'],
        '1С': ['1С', '1С'],
        'PHP': ['PHP', 'ПХП','РНР'],
        'Ruby': ['Ruby', 'Руби'],
        'Python': ['Python', 'Phyton', 'Питон', 'Пайтон'],
        'JavaScript': ['JavaScript', 'JS', 'Java.Script'],
        'Java': ['Java', 'Ява', 'Джава']
    }
    pop_sj_languages = look_superjob(pop_languages)
    print_lang_stat('SuperJob', pop_sj_languages)
    pop_hh_languages = look_hh(pop_languages)
    print_lang_stat('HeadHunter', pop_hh_languages)


def look_hh(pop_languages):
    pop_languages_stats = {lang: [
        {'pattern': '|'.join(map(str, pattern))},
        {'vacancies_found': 0},
        {'vacancies_processed': 0},
        {'average_salary': 0},
        {'ids': []}] for lang, pattern in pop_languages.items()}
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
    for page in count():
        param['page'] = page
        resp = requests.get(job_api, params=param, headers=headers)
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
            match_lang(pop_languages_stats, item.get('id'), item.get('name'), salary_from, salary_to, salary_cur)
        if page == hh_response['pages']-1:
            break

    for lang in pop_languages_stats:
        if pop_languages_stats[lang][2]['vacancies_processed'] > 0:
            pop_languages_stats[lang][3]['average_salary'] = int(pop_languages_stats[lang][3]['average_salary'] /
                                                                 pop_languages_stats[lang][2]['vacancies_processed'])
    return pop_languages_stats


def look_superjob(pop_languages):
    pop_languages_stats = {lang: [
        {'pattern': '|'.join(map(str, pattern))},
        {'vacancies_found': 0},
        {'vacancies_processed': 0},
        {'average_salary': 0},
        {'ids': []}] for lang, pattern in pop_languages.items()}
    load_dotenv()
    sj_key = os.getenv('SJ_SECRET_KEY')
    sj_client_id = os.getenv('SJ_CLIENT_ID')
    sj_login = os.getenv('SJ_LOGIN')
    sj_pwd = os.getenv('SJ_PWD')
    param ={'login': sj_login,'password': sj_pwd, 'client_id' : sj_client_id, 'client_secret': sj_key}
    headers = {
        'Host': 'api.superjob.ru',
        'X-Api-App-Id': sj_key,
        'Content-Type': 'application/json;charset=UTF-8'
    }
    api_sj = 'https://api.superjob.ru/2.0/'
    sj_response = requests.get(f'{api_sj}oauth2/password/', params=param, headers=headers).json()
    if 'error' in sj_response:
        raise requests.exceptions.HTTPError(sj_response['error'])
    access_token = sj_response.get('access_token')
    headers['Authorization'] = f'Bearer {access_token}'
    catalogue_id_development = 48
    town_id = 4
    keyword = 'Программист'
    count = 50
    page = 0
    param = {'town': town_id, 'catalogues': catalogue_id_development, 'keyword': keyword, 'count': count, 'page': page}
    page, more = 0, True
    while more:
        sj_response = requests.get(f'{api_sj}vacancies', params=param, headers=headers).json()
        if 'error' in sj_response:
            raise requests.exceptions.HTTPError(sj_response['error'])
        for vacancy in sj_response['objects']:
            match_lang(pop_languages_stats, vacancy.get('id_client'), vacancy.get('profession'),
                       vacancy.get('payment_from', 0), vacancy.get('payment_to', 0), vacancy.get('currency', ''))
        more = sj_response['more']
        param['page'] += 1

    for lang in pop_languages_stats:
        if pop_languages_stats[lang][2]['vacancies_processed'] > 0:
            pop_languages_stats[lang][3]['average_salary'] = int(pop_languages_stats[lang][3]['average_salary'] /
                                                                 pop_languages_stats[lang][2]['vacancies_processed'])
    return pop_languages_stats


def match_lang(pop_languages_stats, job_id, job_name, salary_from, salary_to, salary_cur):
    for lang, prop_list in pop_languages_stats.items():
        pattern = prop_list[0]['pattern']
        regex = re.compile(pattern, re.IGNORECASE)
        match = re.search(regex, job_name)
        if not match:
            continue
        pop_languages_stats[lang][1]['vacancies_found'] += 1
        pop_languages_stats[lang][4]['ids'].append(job_id)
        if salary_from+salary_to > 0:
            avg_offer = predict_rub_salary(salary_from, salary_to, salary_cur)
            if avg_offer is None:
                break
            pop_languages_stats[lang][2]['vacancies_processed'] += 1
            pop_languages_stats[lang][3]['average_salary'] = pop_languages_stats[lang][3]['average_salary'] + avg_offer
        break


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
                               '{p[vacancies_found]}'.format(p=lang[1][1]),
                               '{p[vacancies_processed]}'.format(p=lang[1][2]),
                               '{p[average_salary]}'.format(p=lang[1][3])
                               ])
        table_instance = SingleTable(table_data, job_site.capitalize())
        table_instance.justify_columns[1] = 'right'
        table_instance.justify_columns[2] = 'right'
        table_instance.justify_columns[3] = 'right'
        print(table_instance.table)


if __name__ == '__main__':
    look_job_sites()
