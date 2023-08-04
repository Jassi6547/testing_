TEST_BOLD_ON = "\033[1m"
TEST_BOLD_OFF = "\033[0m"

TEST_STRIKE_ON = "\x1B[9m"
TEST_STRIKE_OFF = "\x1B[0m"

BOLD_ON = "<b>"
BOLD_OFF = "</b>"

STRIKE_ON = "<s>"
STRIKE_OFF = "</s>"

URL = "https://patents.google.com/patent/"

DEPENDENT_REGEX = r'(claim)(\s+)?\d(\,|\s+?\,)?\s?'
BULLETED_REGEX = r'\d+\.'


LINE_BREAKERS = [';', ',', ':']

API_NOT_FOUND = 404
API_SUCCESS = 200