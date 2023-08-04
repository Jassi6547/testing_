from utils.const import *
import logging
from source.patent_matching import missing_in_second_string, missing_in_first_string


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


def find_common_words_with_indexes(text1, text2):
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
    return result

import difflib

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
            formatted_text1.append(' '.join(words1[start1:end1]))
            formatted_text2.append(' '.join(words2[start2:end2]))
            result.append(' '.join(words1[start1:end1]))
        elif opcode == 'replace':
            # Strikeout words that are in text1 but not in text2
            formatted_text1.append('<strike>' + ' '.join(words1[start1:end1]) + '</strike>')
            formatted_text2.append('<b>' + ' '.join(words2[start2:end2]) + '</b>')
            result.append('<strike>' + ' '.join(words1[start1:end1]) + '</strike>')
            result.append('<b>' + ' '.join(words2[start2:end2]) + '</b>')
        elif opcode == 'delete':
            # Strikeout words that are in text1 but not in text2
            result.append('<strike>' + ' '.join(words1[start1:end1]) + '</strike>')
        elif opcode == 'insert':
            # Bold words that are in text2 but not in text1
            result.append('<b>' + ' '.join(words2[start2:end2]) + '</b>')

    return ' '.join(result)

# Example usage:




if __name__ == '__main__':
    text2 = "A method of changing out a finger on a poultry defeathering apparatus comprising the steps of"
    text1 = "A poultry defeathering apparatus consisting of"
    formatted_text1 = format_text_difference(text1, text2)
    print("Formatted text1:", formatted_text1)
    import pdb;pdb.set_trace()
    highlighted = compare_strings_with_strike_and_bold(text1, text2)
    print(highlighted)
