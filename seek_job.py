import requests
import json


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
    # resp = requests.get(f'{job_api}/{v}/{id}', headers=headers)
    resp = requests.get(f'{job_api}/{v}?{s}=Программист&{a}=1&{p}=30&page=1&per_page=20', headers=headers)
    with open("hh1.json", "w",encoding='utf8') as write_file:
        json.dump(resp.json(), write_file, indent=2, ensure_ascii=False)
    # print(resp.json())



if __name__ == '__main__':
    look_for_job()
