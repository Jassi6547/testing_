import difflib
import logging
import re
from utils.const import *
from source.patents import Patents


class ComparePatents(Patents):

    def __init__(self):
        super().__init__()

    def find_common_words_with_indexes(self, text1: str, text2: str) -> list[tuple[str, int, int]]:
        """
        :Title: Function to find common words between two string with their index numbers
        :param text1: String 1
        :param text2: String 2
        :return: list of tuples containing intersaction words with their locations in both strings.
        """
        logging.debug(f"Inside {self.find_common_words_with_indexes.__name__} function")
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
        logging.debug(f"Moving out from {self.find_common_words_with_indexes.__name__} function")
        return result

    @staticmethod
    def missing_in_first_string(text_: str, word_: str, index_: int = None):
        try:
            return f'{text_}{BOLD_ON}{word_}{BOLD_OFF} ', index_ + 1
        except TypeError:
            return f'{text_}{BOLD_ON}{word_}{BOLD_OFF} '

    @staticmethod
    def missing_in_second_string(text_: str, word_: str, index_: int = None):
        try:
            return f'{text_}{STRIKE_ON}{word_}{STRIKE_OFF} ', index_ + 1
        except TypeError:
            return f'{text_}{STRIKE_ON}{word_}{STRIKE_OFF} '

    def compare_strings_with_strike_and_bold(self, text1: str, text2: str) -> str:
        """
        :Title: Function to compare Two text lines and return a text line showing the difference between both;
                1.) Striking-out words that are missing in 2nd text.
                2.) Making Bold words that are missing in 1st text however present in 2nd Text
        :param text1: Textline 1
        :param text2: Textline 2
        :return: Result line striking out the missing words in 2nd line and bolding the words that are missing in 1st line.
        """
        logging.debug(f"Inside {self.compare_strings_with_strike_and_bold.__name__} function")
        common_words = self.find_common_words_with_indexes(text1, text2)
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
            elif words1[x] in LINE_BREAKERS:
                x += 1
            elif words2[y] in LINE_BREAKERS:
                y += 1
            else:
                ############ We should think about to update this else block as there might be words thay may lay in the
                ########### string but due to that block is going to bold or strike out in next loop where we are checking
                ###########  the length of each string and adding the remaining words.

                ##### so add a new if block for words2 where we check if it is in extra words and a else block that will \
                ##### check in forwarding indexing if the word or sequence of word find than will highlight the
                ##### string accordingly.

                if words1[x] in missing_words:
                    highlighted_text, x = self.missing_in_second_string(highlighted_text, words1[x], x)
                elif words2[y] in extra_words:
                    highlighted_text, y = self.missing_in_first_string(highlighted_text, words2[y], y)
                else:
                    w1_loc_in_w2 = [item[2] for item in common_words if item[0] == words1[x] and item[2] > y]
                    w2_loc_in_w1 = [item[1] for item in common_words if item[0] == words2[y] and item[1] > x]
                    if not len(w1_loc_in_w2):
                        highlighted_text, x = self.missing_in_second_string(highlighted_text, words1[x], x)
                    elif not len(w2_loc_in_w1):
                        highlighted_text, y = self.missing_in_first_string(highlighted_text, words2[y], y)
                    else:
                        if min(w1_loc_in_w2) < min(w2_loc_in_w1):
                            highlighted_text, y = self.missing_in_first_string(highlighted_text, words2[y], y)
                        else:
                            highlighted_text, x = self.missing_in_second_string(highlighted_text, words1[x], x)
                        # pass

            #### Code execute when all words of text1 executed. So it will add with bold words of text2 in output
            #### text variable highlighted_text
            if x >= len(words1):
                highlighted_text, flag = self.missing_in_first_string(highlighted_text, " ".join(words2[y:])), False
                # highlighted_text += f'{BOLD_ON}{(" ").join(words2[y:])}{BOLD_OFF} '
                # flag = False

            #### Code execute when all words of text2 executed. So it will add with bold words of text1 in output
            #### text variable highlighted_text
            if y >= len(words2):
                highlighted_text, flag = self.missing_in_second_string(highlighted_text, " ".join(words1[x:])), False
                # highlighted_text += f'{STRIKE_ON}{(" ").join(words1[x:])}{STRIKE_OFF} '
                # flag = False
        logging.debug(f"Moving out from {self.compare_strings_with_strike_and_bold.__name__} function")
        return highlighted_text

    @staticmethod
    def split_(s):
        """
        Title: Function to split the string with bulleted number
        :param s: string
        :return: list of splited string
        """
        ## Purpose to create this function is to split claims.

        return re.split(' \d. ', s)

    def claim_splitter_in_lines(self):
        pass

    def line_similarity(self, line1, line2):
        """
        :Title: Difflib function that tells the similarity of two string lines by sequence matching.
        :param line1: String 1
        :param line2: String 2
        :return: Matching ratio of both strings
        """
        logging.debug(f"Inside {self.line_similarity.__name__} function")
        similarity = difflib.SequenceMatcher(None, line1, line2).ratio()
        logging.debug(f"Moving out from {self.line_similarity.__name__} function")
        return similarity * 100

    def line_matching(self, line1: str, line2: str) -> (bool, float | int):
        """
        :Title: Function to compare two lines words so that Similarity of lines can be checked.
        :param line1: String 1
        :param line2: String 2
        :return: Matching status and word matching average
        """
        logging.debug(f"Inside {self.line_matching.__name__} function")
        line1 = line1.split()
        line2 = line2.split()
        min_len = min(len(line1), len(line2))
        matching_words = list(set(line1).intersection(set(line2)))
        avg_matching_words = (len(matching_words) / min_len) * 100
        if avg_matching_words > 50:
            logging.debug(f"matching line with matching average: {avg_matching_words}")
            logging.debug(f"Moving out from {self.line_matching.__name__} function")
            return True, avg_matching_words
        logging.debug(f"Moving out from {self.line_matching.__name__} function")
        return False, avg_matching_words

    @staticmethod
    def truncate_string_from_dependent_claims(string_: str) -> str:
        """
        :Title: Function to remove substring from string that tells about the dependand info
        :param string_: Actuall String or Claim
        :return: Actual string or claim after removing of dependand information
        """
        match = re.search(DEPENDENT_REGEX, string_)
        return string_[match.end():] if match else string_

    def find_and_replace(self, string, word_to_find, replacement_word):
        """
        :Title: Function to find and replace the word.
        :param string: String in which we want to find a word.
        :param word_to_find: Word that we want to look into the string.
        :param replacement_word: The word that we want to replace with found word
        :return: String with replaced words
        """
        logging.debug(f"Inside {self.find_and_replace.__name__} function")
        pattern = r'\b' + re.escape(word_to_find) + r'\b'
        replaced_string = re.sub(pattern, replacement_word, string)
        logging.debug(f"Moving out from {self.find_and_replace.__name__} function")
        return replaced_string

    def get_line_difference1(self, string1: str, string2: str) -> str:
        """
        :Title: Function to Compare two strings line by line and highlight the words that are different in both strings.
                1 Green with Bold words: Words that are only in second string.
                2 Red with Strike out: Words that are only in first string.
        :param string1: String 1
        :param string2: String 2
        :return: Compared String
        """
        logging.debug(f"Inside {self.get_line_difference1.__name__} function")
        string1 = self.truncate_string_from_dependent_claims(string1)
        string2 = self.truncate_string_from_dependent_claims(string2)
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
                print(x, y)
                status, avg = self.line_matching(string1_line_list[x], string2_line_list[y])
                check = self.line_similarity(string1_line_list[x], string2_line_list[y])
                if (avg >= 50) | (check >= 50):
                    result.append(
                        f"{x}. {self.compare_strings_with_strike_and_bold(string1_line_list[x], string2_line_list[y])}")
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
        logging.debug(f"Moving out from {self.get_line_difference1.__name__} function")
        return ("; ").join(sorted(result)), self.get_maximum_repeated_values(matching_status)

    def compare_claims(self, claim1_list, claim2_list) -> list[dict]:
        """
        :Title: Function to compare claims of different Patent_ids One by One
        :param claim1_list: List of claims of first Patent_id
        :param claim2_list: List of claims of Second Patent_id
        :return: List of dictionary with Status key that tells about similarity of both claim lists
        """

        matched = {}
        result = []
        for x in range(0, len(claim1_list)):
            for y in range(0, len(claim2_list)):
                if y in matched.values():
                    continue
                print(x, y)
                res_string, status_ = self.get_line_difference1(claim1_list[x], claim2_list[y])
                matched[x] = y
                result.append({"claims": f"claim {x} and claim {y}", "status": status_})
                break
        print(result)
        return result


def split_with_multiple_delimiters(input_string, delimiters):
    pattern = '|'.join(map(re.escape, delimiters))
    return re.split(pattern, input_string)


# def update_new_old_claim_lines(str_, processed, result, status_, hlight_with):
#     str_index = [index for index, items in enumerate(str_)]
#     missed_str = list(set(str_index).difference(set(processed)))
#     for each in missed_str:
#         result.append(f"{each}. <{hlight_with}>{str_[each]}</{hlight_with}>")
#         status_.append("Not Matching")