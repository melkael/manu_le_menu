import re
from levenshteinautomaton import SparseLevenshteinAutomaton
from nltk.stem.snowball import SnowballStemmer
from unidecode import unidecode


class MessageHandler():

    def __init__(self):
        self.categories_list = []
        self.neighborhoods_list = []

        with open('quartiers.txt', mode='r') as f:
            for word in f.readlines():
                self.neighborhoods_list.append(word.replace('\n', ''))

        with open('categories.txt', mode='r') as f:
            for word in f.readlines():
                self.categories_list.append(word.replace('\n', ''))

    def reduce_lengthening(self, text):
        pattern = re.compile(r"(.)\1{2,}")
        return pattern.sub(r"\1\1", text)

    def remove_diacritics(self, string):
        return unidecode(string)

    def strip_non_letters(self, string):
        return re.sub(r'[^a-zA-Z ]+', '', string)

    def stemmerMatch(self, str1, str2, language):
        stemmer = SnowballStemmer(language)
        return stemmer.stem(str1) == stemmer.stem(str2)

    def levenstheinMatch(self, str1, str2, distance):
        automaton = SparseLevenshteinAutomaton(str1, distance)
        state = automaton.start()
        for letter in list(str2):
            state = automaton.step(state, letter)
            if automaton.can_match(state) is False:
                return False
        return True

    def check_strings_match(self, str1, str2):
        return (self.levenstheinMatch(str1, str2, 1) or
                self.stemmerMatch(str1, str2, 'french') or
                self.stemmerMatch(str1, str2, 'english'))

    def match_word(self, word, lookup_name):
        if lookup_name == 'category':
            lookup_list = self.categories_list
        elif lookup_name == 'neighborhood':
            lookup_list = self.neighborhoods_list
        elif lookup_name == 'price':
            lookup_list = ['abordable', 'modere', 'cher', 'luxueux']

        for lookup_word in lookup_list:
            if self.check_strings_match(word, lookup_word):
                return lookup_word
        return None

    def correct_and_match(self, string, lookup_name):

        string = self.reduce_lengthening(string)
        string = self.remove_diacritics(string)
        string = self.strip_non_letters(string)

        returned_set = set([])

        for word in string.split(' '):
            matched_word = self.match_word(word, lookup_name)
            if matched_word is not None:
                returned_set.add(matched_word)

        return returned_set
