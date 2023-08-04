from utils.const import *
from typing import Protocol
from dataclasses import dataclass
import logging


@dataclass
class CompareStrings:
    text1: str
    text2: str


class Texts_(Protocol):
    @property
    def text1(self) -> str:
        ...

    @property
    def text2(self) -> str:
        ...


# def compare_strings_with_strike_and_bold(text1: str, text2: str) -> str:\
def validate_strings(texts: Texts_) -> bool:
    if None in (texts.text1, texts.text2):
        logging.error("Missing value to compare")
        return False
    if not (isinstance(texts.text1, str) and isinstance(texts.text2, str)):
        logging.error("Passing values are not of string types")
        return False
    return True


def compare_strings_with_strike_and_bold(texts: Texts_) -> str:
    """
    :Title: Function to compare Two text lines and return a text line showing the difference between both;
            1.) Striking-out words that are missing in 2nd text.
            2.) Making Bold words that are missing in 1st text however present in 2nd Text
    :param text1: Textline 1
    :param text2: Textline 2
    :return: Result line striking out the missing words in 2nd line and bolding the words that are missing in 1st line.
    """
    logging.debug(f"Text1: {texts.text1}")
    logging.debug(f"Text2: {texts.text2}")
    words1 = texts.text1.split()
    words2 = texts.text2.split()
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
    logging.debug(f"Comparing Result: {highlighted_text}")
    return highlighted_text


if __name__ == '__main__':
    # text1 = "a connector body including one or more terminals supported therein"
    # text2 = "a connector body including one or more terminals supported therein"
    logging.basicConfig(level=logging.DEBUG)
    compare = CompareStrings(
        text1="a spring two seat coupled to a shorting member",
        text2="a spring seat coupled to a shorting member support and a shorting member coupled to the shorting member support"
    )

    result = validate_strings(compare)
    if result:
        highlighted = compare_strings_with_strike_and_bold(compare)
        # print(compare.text1)
        # print(compare.text2)
        # print(highlighted)
