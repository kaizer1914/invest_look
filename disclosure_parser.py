import requests
from bs4 import BeautifulSoup


class DisclosureParser:
    SITE = 'https://www.e-disclosure.ru/'

    def __init__(self, company_id: str):
        self.__id = company_id
        self.__company_card_page = f'{self.SITE}portal/company-{self.__id}/otchyotnost-kompanii'
        self.__file_page_links = dict()

    def parse_file_page_links(self):
        request = requests.get(self.__company_card_page)
        if request:
            response = BeautifulSoup(request.content, 'lxml')
            cont_wrap = response.find('div', {'id': 'cont_wrap'})
            for a in cont_wrap.find_all('a'):
                self.__file_page_links.update({a.text: self.SITE + a['href']})

    def get_file_page_links(self) -> dict:
        return self.__file_page_links


if __name__ == '__main__':
    parser = DisclosureParser('7704')
    parser.parse_file_page_links()
    print(parser.get_file_page_links())
