import logging
from typing import List

import requests
import re
import difflib
from utils.const import *
from bs4 import BeautifulSoup

# DEPENDENT_REGEX = r'(claim)(\s+)?\d(\,|\s+?\,)?\s?'

class Patents:
    def __init__(self):
        pass

    def scrap_patent_id_page(self, id_):
        page = requests.get(f"{URL}{id_}/en")
        return BeautifulSoup(page.content, "html.parser")

    def get_claim_by_id(self, patent_id):
        page_data = self.scrap_patent_id_page(patent_id)
        return self.extract_claim_info(page_data)

    def extract_claim_info(self, html_page):
        claims = html_page.find('section', {'itemprop': 'claims'})
        if not claims is None:
            # Handle situation where claims have non-english paragraphs
            if claims.find('span', class_='notranslate') is None:
                claims = claims.text.strip()
            else:
                notranslate = [tag.find(class_='google-src-text') for tag in
                               claims.find_all('span', class_='notranslate')]
                for tag in notranslate:
                    tag.extract()
            index = re.search(r'1\.', claims).start()
            return claims[index:].replace("\n", "").strip().lower(), API_SUCCESS
        else:
            return 'Not Found', API_NOT_FOUND

    @staticmethod
    def get_claim_list(str_: str) -> list[str]:
        claim_list = re.split(BULLETED_REGEX, str_)
        # Remove empty elements and leading/trailing whitespaces
        return [item.strip().lower() for item in claim_list if item.strip()]

    @staticmethod
    def list_to_dict_with_custom_keys(input_list: list[dict]) -> list[dict]:
        return [{"id": index + 1, "name": item} for index, item in enumerate(input_list)]


