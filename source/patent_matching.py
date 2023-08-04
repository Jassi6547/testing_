import logging
from typing import Tuple
from source.compare import split_with_multiple_delimiters
import requests
import re
import difflib
from utils.const import *
# import spacy
from bs4 import BeautifulSoup


# from rake_nltk import Rake

#  python -m spacy download en_core_web_lg

# rake_nltk_var = Rake()
#

# DEPENDENT_REGEX = r'(claim)(\s+)?\d(\,|\s+?\,)?\s?'
def format_text_difference(text1, text2):
    words1 = text1.split()
    words2 = text2.split()

    # Compare the words using difflib
    matcher = difflib.SequenceMatcher(None, words1, words2)
    differences = list(matcher.get_opcodes())

    formatted_text1 = []
    formatted_text2 = []
    result = []
    for opcode, start1, end1, start2, end2 in differences:
        if opcode == 'equal':
            result.append(' '.join(words1[start1:end1]))
        elif opcode == 'replace':
            # Strikeout words that are in text1 but not in text2
            result.append('<s>' + ' '.join(words1[start1:end1]) + '</s>')
            result.append('<b>' + ' '.join(words2[start2:end2]) + '</b>')
        elif opcode == 'delete':
            # Strikeout words that are in text1 but not in text2
            result.append('<s>' + ' '.join(words1[start1:end1]) + '</s>')
        elif opcode == 'insert':
            # Bold words that are in text2 but not in text1
            result.append('<b>' + ' '.join(words2[start2:end2]) + '</b>')

    return ' '.join(result)

def find_common_words_with_indexes(text1: str, text2: str) -> list[tuple[str, int, int]]:
    """
    :Title: Function to find common words between two string with their index numbers
    :param text1: String 1
    :param text2: String 2
    :return: list of tuples containing intersaction words with their locations in both strings.
    """
    logging.debug(f"Inside {find_common_words_with_indexes.__name__} function")
    words1 = text1.split()
    words2 = text2.split()
    common_words = list(set(words1) & set(words2))
    result = []
    for word in common_words:
        str1_indexes = [index for index, w in enumerate(words1) if w == word]
        str2_indexes = [index for index, w in enumerate(words2) if w == word]

        for index1 in str1_indexes:
            for index2 in str2_indexes:
                if index1 != index2:
                    result.append((word, index1, index2))
    logging.debug(f"Moving out from {find_common_words_with_indexes.__name__} function")
    return result


def missing_in_second_string(text_: str, word_: str, index_: int = None):
    try:
        return f'{text_}{STRIKE_ON}{word_}{STRIKE_OFF} ', index_ + 1
    except TypeError:
        return f'{text_}{STRIKE_ON}{word_}{STRIKE_OFF} '


def missing_in_first_string(text_: str, word_: str, index_: int = None):
    try:
        return f'{text_}{BOLD_ON}{word_}{BOLD_OFF} ', index_ + 1
    except TypeError:
        return f'{text_}{BOLD_ON}{word_}{BOLD_OFF} '


def compare_strings_with_strike_and_bold(text1: str, text2: str) -> str:
    """
    :Title: Function to compare Two text lines and return a text line showing the difference between both;
            1.) Striking-out words that are missing in 2nd text.
            2.) Making Bold words that are missing in 1st text however present in 2nd Text
    :param text1: Textline 1
    :param text2: Textline 2
    :return: Result line striking out the missing words in 2nd line and bolding the words that are missing in 1st line.
    """
    logging.debug(f"Inside {compare_strings_with_strike_and_bold.__name__} function")
    common_words = find_common_words_with_indexes(text1, text2)
    logging.debug(f"Line 1: {text1}")
    logging.debug(f"Line 2: {text2}")
    words1 = text1.split()
    words2 = text2.split()
    highlighted_text = ""
    missing_words = list(set(words1).difference(set(words2)))
    extra_words = list(set(words2).difference(set(words1)))
    flag = True
    x = y = 0
    #### Condition comparing the words
    while flag:
        if words1[x] == words2[y]:
            highlighted_text += f'{words1[x]} '
            x += 1
            y += 1
        elif words1[x] in [';', ',', ':']:
            x += 1
        elif words2[y] in [';', ',', ':']:
            y += 1
        else:
            ############ We should think about to update this else block as there might be words thay may lay in the
            ########### string but due to that block is going to bold or strike out in next loop where we are checking
            ###########  the length of each string and adding the remaining words.

            ##### so add a new if block for words2 where we check if it is in extra words and a else block that will \
            ##### check in forwarding indexing if the word or sequence of word find than will highlight the
            ##### string accordingly.

            if words1[x] in missing_words:
                highlighted_text, x = missing_in_second_string(highlighted_text, words1[x], x)
            elif words2[y] in extra_words:
                highlighted_text, y = missing_in_first_string(highlighted_text, words2[y], y)
            else:
                w1_loc_in_w2 = [item[2] for item in common_words if item[0] == words1[x] and item[2] > y]
                w2_loc_in_w1 = [item[1] for item in common_words if item[0] == words2[y] and item[1] > x]
                if not len(w1_loc_in_w2):
                    highlighted_text, x = missing_in_second_string(highlighted_text, words1[x], x)
                elif not len(w2_loc_in_w1):
                    highlighted_text, y = missing_in_first_string(highlighted_text, words2[y], y)
                else:
                    if min(w1_loc_in_w2) < min(w2_loc_in_w1):
                        highlighted_text, y = missing_in_first_string(highlighted_text, words2[y], y)
                    else:
                        highlighted_text, x = missing_in_second_string(highlighted_text, words1[x], x)
                    # pass

        #### Code execute when all words of text1 executed. So it will add with bold words of text2 in output
        #### text variable highlighted_text
        if x >= len(words1):
            highlighted_text, flag = missing_in_first_string(highlighted_text, " ".join(words2[y:])), False
            # highlighted_text += f'{BOLD_ON}{(" ").join(words2[y:])}{BOLD_OFF} '
            # flag = False

        #### Code execute when all words of text2 executed. So it will add with bold words of text1 in output
        #### text variable highlighted_text
        if y >= len(words2):
            highlighted_text, flag = missing_in_first_string(highlighted_text, " ".join(words1[x:])), False
            # highlighted_text += f'{STRIKE_ON}{(" ").join(words1[x:])}{STRIKE_OFF} '
            # flag = False
    logging.debug(f"Moving out from {compare_strings_with_strike_and_bold.__name__} function")
    return highlighted_text


# def get_keywords(text_: str) -> list:
#     """
#     :Title: Function to Extract Keywords from Text.
#     :param text_: Text from which keywords supposed to be fetched.
#     :return: list of extracted Keywords
#     """
#     rake_nltk_var.extract_keywords_from_text(text_)
#     return list(set(rake_nltk_var.get_ranked_phrases()))


def find_and_replace(string, word_to_find, replacement_word):
    """
    :Title: Function to find and replace the word.
    :param string: String in which we want to find a word.
    :param word_to_find: Word that we want to look into the string.
    :param replacement_word: The word that we want to replace with found word
    :return: String with replaced words
    """
    logging.debug(f"Inside {find_and_replace.__name__} function")
    pattern = r'\b' + re.escape(word_to_find) + r'\b'
    replaced_string = re.sub(pattern, replacement_word, string)
    logging.debug(f"Moving out from {find_and_replace.__name__} function")
    return replaced_string


def split_(s):
    """
    Title: Function to split the string with bulleted number
    :param s: string
    :return: list of splited string
    """
    ## Purpose to create this function is to split claims.

    return re.split(' \d. ', s)


def get_claims(ids: str) -> tuple[str, int]:
    """
    Title: Function to Extract Patent claims by Patent_id
    :param ids: Patent id for which claims to be extracted
    :return: claims string
    """
    logging.debug(f"Inside {get_claims.__name__} function")
    page = requests.get(URL + f"{ids}/en")
    soup = BeautifulSoup(page.content, "html.parser")
    claims = soup.find('section', {'itemprop': 'claims'})
    if claims is not None:
        # Handle situation where claims have non-english paragraphs
        if claims.find('span', class_='notranslate') is None:
            claims = claims.text.strip()
        else:
            no_translate = [tag.find(class_='google-src-text') for tag in claims.find_all('span', class_='notranslate')]
            for tag in no_translate:
                tag.extract()
            claims = claims.text.strip()
        index = re.search(r'1\.', claims).start()
        # Remove characters before the index and trimming the string
        logging.debug(f"Moving out from {get_claims.__name__} function")
        return claims[index:].replace("\n", "").strip().lower(), API_SUCCESS
    else:
        logging.debug(f"Moving out from {get_claims.__name__} function")
        return '', API_NOT_FOUND


def get_claim_list(str_: str) -> list[str]:
    """
    :Title: Function is used to split a string into lines respectively with Bulleted Number
    :param str_: String input.
    :return: list of string lines.
    """
    # import pdb;pdb.set_trace()
    claim_list = re.split(r'\d+\.\s', str_)
    # Remove empty elements and leading/trailing whitespaces
    return [item.strip().lower() for item in claim_list if item.strip()]


def list_to_dict_with_custom_keys(input_list: list[str]) -> list[dict]:
    """
    :Title: Function to add id field to line of string
    :param input_list: list of strings lines
    :return: list of dictionary with id and name key where id represents line number and name represent the string line.
    """

    return [{"id": index + 1, "name": item} for index, item in enumerate(input_list)]


def line_matching(line1: str, line2: str) -> (bool, float | int):
    """
    :Title: Function to compare two lines words so that Similarity of lines can be checked.
    :param line1: String 1
    :param line2: String 2
    :return: Matching status and word matching average
    """
    logging.debug(f"Inside {line_matching.__name__} function")
    line1 = line1.split()
    line2 = line2.split()
    min_len = min(len(line1), len(line2))
    matching_words = list(set(line1).intersection(set(line2)))
    avg_matching_words = (len(matching_words) / min_len) * 100
    if avg_matching_words > 50:
        logging.debug(f"matching line with matching average: {avg_matching_words}")
        logging.debug(f"Moving out from {line_matching.__name__} function")
        return True, avg_matching_words
    logging.debug(f"Moving out from {line_matching.__name__} function")
    return False, avg_matching_words


def line_similarity(line1, line2):
    """
    :Title: Difflib function that tells the similarity of two string lines by sequence matching.
    :param line1: String 1
    :param line2: String 2
    :return: Matching ratio of both strings
    """
    logging.debug(f"Inside {line_similarity.__name__} function")
    similarity = difflib.SequenceMatcher(None, line1, line2).ratio()
    logging.debug(f"Moving out from {line_similarity.__name__} function")
    return similarity * 100


def truncate_string_with_regex(original_string, regex_pattern):
    match = re.search(regex_pattern, original_string)
    if match:
        return original_string[match.end():]
    return original_string


def get_line_difference(string1: str, string2: str) -> str:
    """
    :Title: Function to Compare two strings line by line and highlight the words that are different in both strings.
            1 Green with Bold words: Words that are only in second string.
            2 Red with Strike out: Words that are only in first string.
    :param string1: String 1
    :param string2: String 2
    :return: Compared String
    """
    logging.debug(f"Inside {get_line_difference.__name__} function")
    sub_string = r'(claim)(\s+)?\d(\,|\s+?\,)?\s?'
    string1 = truncate_string_with_regex(string1, sub_string)
    string2 = truncate_string_with_regex(string2, sub_string)
    string1_line_list = re.split(r'[;|:]', re.sub(r"\;\s+(and|or)", ' and', string1))
    string2_line_list = re.split(r'[;|:]', re.sub(r"\;\s+(and|or)", ' and', string2))
    string1_line_list = [item.strip().lower() for item in string1_line_list if item.strip()]
    string2_line_list = [item.strip().lower() for item in string2_line_list if item.strip()]

    matched = {}
    result = []
    processed_x = []
    processed_y = []
    """
        Trying to refine the below logic
    """

    for x in range(00, len(string1_line_list)):
        for y in range(00, len(string2_line_list)):
            if y in matched.values():
                continue
            check = line_similarity(string1_line_list[x], string2_line_list[y])
            if (check >= 90):
                # result.append({"id": x, "value": f"{x}. {compare_strings_with_strike_and_bold(string1_line_list[x], string2_line_list[y])}"})
                result.append({"id": x, "value": f"{x}. {format_text_difference(string1_line_list[x], string2_line_list[y])}"})
                matched[x] = y
                processed_x.append(x)
                processed_y.append(y)
                break

    not_processed_x = [i for i, v in enumerate(string1_line_list) if i not in processed_x]
    not_processed_y = [i for i, v in enumerate(string2_line_list) if i not in processed_y]
    for x in not_processed_x:
        for y in not_processed_y:
            if y in matched.values():
                continue
            status, avg = line_matching(string1_line_list[x], string2_line_list[y])
            if (avg >= 50):
                # result.append({"id": x, "value":f"{x}. {compare_strings_with_strike_and_bold(string1_line_list[x], string2_line_list[y])}"})
                result.append({"id": x, "value":f"{x}. {format_text_difference(string1_line_list[x], string2_line_list[y])}"})
                matched[x] = y
                processed_x.append(x)
                processed_y.append(y)
                break

    if len(processed_x) != len(string1_line_list):
        string1_index = [index for index, fruit in enumerate(string1_line_list)]
        missed_string1 = list(set(string1_index).difference(set(processed_x)))
        for each in missed_string1:
            result.append({"id":each, "value": f"{each}. <s>{string1_line_list[each]}</s>"})

    if len(processed_y) != len(string2_line_list):
        string2_index = [index for index, fruit in enumerate(string2_line_list)]
        missed_string2 = list(set(string2_index).difference(set(processed_y)))
        for each in missed_string2:
            result.append({"id": each, "value": f"{each}. <b>{string2_line_list[each]}</b>"})

    logging.info(f"final output is:\n\n\n{[item for item in result]}")
    logging.debug(f"Moving out from {get_line_difference.__name__} function")
    result.sort(key=lambda k: k['id'])
    return ";<br/> ".join([each['value'] for each in result])


def get_line_difference1(string1: str, string2: str) -> tuple[str, str]:
    """
    :Title: Function to Compare two strings line by line and highlight the words that are different in both strings.
            1 Green with Bold words: Words that are only in second string.
            2 Red with Strike out: Words that are only in first string.
    :param string1: String 1
    :param string2: String 2
    :return: Compared String
    """
    logging.debug(f"Inside {get_line_difference.__name__} function")
    sub_string = r'(claim)(\s+)?\d(\,|\s+?\,)?\s?'
    string1 = truncate_string_with_regex(string1, sub_string)
    string2 = truncate_string_with_regex(string2, sub_string)
    string1_line_list = re.split(r'[;]', re.sub(r"\;\s+(and|or)", ' and', string1))
    string2_line_list = re.split(r'[;]', re.sub(r"\;\s+(and|or)", ' and', string2))
    string1_line_list = [item.strip().lower() for item in string1_line_list if item.strip()]
    string2_line_list = [item.strip().lower() for item in string2_line_list if item.strip()]

    # check_matching = line_similarity(string1_line_list[2], string2_line_list[2])
    matched = {}
    result = []
    processed_x = []
    processed_y = []
    matching_status = []
    for x in range(0, len(string1_line_list)):
        for y in range(0, len(string2_line_list)):
            if y in matched.values():
                continue
            status, avg = line_matching(string1_line_list[x], string2_line_list[y])
            check = line_similarity(string1_line_list[x], string2_line_list[y])
            if (avg >= 50) | (check >= 50):
                result.append(
                    f"{x}. {compare_strings_with_strike_and_bold(string1_line_list[x], string2_line_list[y])}")
                matched[x] = y
                processed_x.append(x)
                processed_y.append(y)
                matching_status.append("Matching")
                break
            else:
                matching_status.append("Not Matching")

    if len(processed_x) != len(string1_line_list):
        string1_index = [index for index, fruit in enumerate(string1_line_list)]
        missed_string1 = list(set(string1_index).difference(set(processed_x)))
        for each in missed_string1:
            result.append(f"{each}. <s>{string1_line_list[each]}</s>")
            matching_status.append("Not Matching")

    if len(processed_y) != len(string2_line_list):
        string2_index = [index for index, fruit in enumerate(string2_line_list)]
        missed_string2 = list(set(string2_index).difference(set(processed_y)))
        for each in missed_string2:
            result.append(f"{each}. <b>{string2_line_list[each]}</b>")
            matching_status.append("Not Matching")

    logging.debug(f"final output is:\n\n\n{[item for item in result]}")
    logging.debug(f"Moving out from {get_line_difference.__name__} function")
    return ("; ").join(sorted(result)), get_maximum_repeated_values(matching_status)


def get_maximum_repeated_values(input_list):
    count_yes = input_list.count("Matching")
    count_no = input_list.count("Not Matching")
    return "Matching" if count_yes >= count_no else "Not Matching"


def compare_claims(claim1, claim2):
    matched = {}
    result = []
    for x in range(0, len(claim1)):
        for y in range(0, len(claim2)):
            if y in matched.values():
                continue
            res_string, status_ = get_line_difference1(claim1[x], claim2[y])
            matched[x] = y
            if status_ == "Matching":
                result.append(f"Claim {x + 1} ->  Claim {y + 1}")
            break

    return result
