import requests
from bs4 import BeautifulSoup


class DisclosureParser:
    SITE = 'https://www.e-disclosure.ru/'

    def __init__(self, company_id: str):
        self.__id = company_id
        self.__company_card_page = f'{self.SITE}portal/company-{self.__id}/otchyotnost-kompanii'
        self.__report_page_links = dict()

    def parse_report_page_links(self):
        request = requests.get(self.__company_card_page)
        if request:
            response = BeautifulSoup(request.content, 'lxml')
            cont_wrap = response.find('div', {'id': 'cont_wrap'})
            for a in cont_wrap.find_all('a'):
                self.__report_page_links.update({a.text: self.SITE + a['href']})

    def parse_file_links(self, report_page: str):
        request = requests.get(report_page)
        if request:
            response = BeautifulSoup(request.content, 'lxml')
            cont_wrap = response.find('table', {'class': 'zebra noBorderTbl centerHeader files-table'})
            columns = cont_wrap.findNext('tr').text
            # columns = columns.split()
            print(columns)
            for row in cont_wrap.find_all('tr'):
                for cell in row.find_all('td'):
                    # print(cell)
                    pass

    def get_report_page_links(self) -> dict:
        return self.__report_page_links


if __name__ == '__main__':
    parser = DisclosureParser('1389')
    parser.parse_report_page_links()
    link = parser.get_report_page_links().get('Годовая')
    parser.parse_file_links(link)
