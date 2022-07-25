import json
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.indeed.com/jobs?'
site = 'https://www.indeed.com'

params = {
    'q': 'Python Developer',
    'l': 'New York State',
    'vjk': '455282569a65db72'
}

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
}

res = requests.get(url, params=params, headers=headers)


def get_total_pages(query, location):
    params = {
        'q': query,
        'l': location,
        'vjk': '455282569a65db72'
    }

    res = requests.get(url, params=params, headers=headers)

    total_pages = []

    # Scraping Step
    soup = BeautifulSoup(res.text, 'html.parser')
    pagination = soup.find('ul', 'pagination-list')
    pages = pagination.find_all('li')

    for page in pages:
        total_pages.append(page.text)

    total = int(max(total_pages))
    return total


def get_all_items(query, location, start, page):
    params = {
        'q': query,
        'l': location,
        'start': start,
        'vjk': '455282569a65db72'
    }

    res = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # Scraping Process
    contents = soup.find_all('table', 'jobCard_mainContent big6_visualChanges')

    # pick item
    # * title
    # * company name
    # * company link
    # * company address

    jobs_list = []

    for item in contents:
        title = item.find('h2', 'jobTitle').text
        company = item.find('span', 'companyName')
        company_name = company.text
        try:
            company_link = site + company.find('a')['href']
        except:
            company_link = 'Link is not available'

        # sorting data
        data_dict = {
            'title': title,
            'company name': company_name,
            'link': company_link
        }

        jobs_list.append(data_dict)

    # writing json file
    try:
        os.mkdir('json_result')
    except FileExistsError:
        pass

    with open(f'json_result/{query}_in_{location}_page_{page}.json', 'w+') as json_data:
        json.dump(jobs_list, json_data)

    print('json created')
    return jobs_list


def create_document(dataFrame, filename):
    try:
        os.mkdir('results')
    except FileExistsError:
        pass

    df = pd.DataFrame(dataFrame)
    df.to_csv(f'results/{filename}.csv', index=False)
    df.to_excel(f'results/{filename}.xlsx', index=False)

    print(f'File {filename}.csv and {filename}.xlsx successfully created')


def run():
    query = input('Enter Your Query: ')
    location = input('Enter Your Location: ')

    total = get_total_pages(query, location)
    counter = 0
    final_result = []
    for page in range(total):
        page += 1
        counter += 10
        final_result += get_all_items(query, location, counter, page)

    # formatting data
    try:
        os.mkdir('reports')
    except FileExistsError:
        pass

    with open('reports/{}.json'.format(query), 'w+') as final_data:
        json.dump(final_result, final_data)

    print('Data JSON Has Created')

    # create document
    create_document(final_result, query)


if __name__ == '__main__':
    run()
