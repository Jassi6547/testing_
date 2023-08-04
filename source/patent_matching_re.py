import re
import requests
from bs4 import BeautifulSoup
from utils.const import *

def compare_strings_with_strike_and_bold(text1: str, text2: str) -> str:
    """
    :Title: Function to compare Two text lines and return a text line showing the difference between both;
            1.) Striking-out words that are missing in 2nd text.
            2.) Making Bold words that are missing in 1st text however present in 2nd Text
    :param text1: Textline 1
    :param text2: Textline 2
    :return: Result line striking out the missing words in 2nd line and bolding the words that are missing in 1st line.
    """
    words1 = text1.split()
    words2 = text2.split()
    highlighted_text = ""
    missing_words = list(set(words1).difference(set(words2)))
    flag = True
    x = y = 0
    #### Condition comparing the words
    while flag:
        if words1[x] == words2[y]:
            highlighted_text += f'{words1[x]} '
            x += 1;
            y += 1
        else:
            if words1[x] in missing_words:
                highlighted_text += f'{STRIKE_ON}{words1[x]}{STRIKE_OFF} '
                x += 1
            else:
                highlighted_text += f'{BOLD_ON}{words2[y]}{BOLD_OFF} '
                y += 1

        #### Code execute when all words of text1 executed. So it will add with bold words of text2 in output
        #### text variable highlighted_text
        if x >= len(words1):
            highlighted_text += f'{BOLD_ON}{(" ").join(words2[y:])}{BOLD_OFF} '
            flag = False

        #### Code execute when all words of text2 executed. So it will add with bold words of text1 in output
        #### text variable highlighted_text
        if y >= len(words2):
            highlighted_text += f'{STRIKE_ON}{(" ").join(words1[x:])}{STRIKE_OFF} '
            flag = False
    return highlighted_text

def get_claims(ids: str) -> str:
    """
    Title: Function to Extract Patent claims by Patent_id
    :param ids: Patent id for which claims to be extracted
    :return: claims string
    """

    page = requests.get(URL + f"{ids}/en")
    soup = BeautifulSoup(page.content, "html.parser")
    claims = soup.find('section', {'itemprop': 'claims'})

    if not claims is None:
        # Handle situation where claims have non-english paragraphs
        if claims.find('span', class_='notranslate') is None:
            claims = claims.text.strip()
        else:
            notranslate = [tag.find(class_='google-src-text') for tag in claims.find_all('span', class_='notranslate')]
            for tag in notranslate:
                tag.extract()
            claims = claims.text.strip()

    else:
        claims = 'Not Found'
    index = re.search(r'1\.', claims).start()
    # Remove characters before the index
    claims = claims[index:]
    claim_str = claims.replace("\n", "").strip()
    return claim_str.lower()


def get_claim_list(str_: str) -> list[str]:
    claim_list = re.split(r'\d+\.', str_)
    # Remove empty elements and leading/trailing whitespaces
    return [item.strip().lower() for item in claim_list if item.strip()]

text1 = get_claims("US3818563A")
import pdb;pdb.set_trace()
all_claims = get_claim_list(text1)
# highlighted = compare_strings_with_strike_and_bold(text1, text2)

