import requests
import re

from ankipandas import Collection
from tkinter import filedialog
from nltk.corpus import wordnet
from bs4 import BeautifulSoup


class word_entity:
    def __init__(self, pronunciation, word_meanings, translations):
        self.pronunciation = pronunciation
        self.word_meanings = word_meanings
        self.translations = translations

    def connect_word_meanings_with_translations(self):
        pass


def get_words_from_text_file():
    filepath = filedialog.askopenfilename()
    with open(filepath, encoding='utf-8') as f:
        file_content = f.read()

    words = file_content.split('\n')

    return words


def get_meanings_of_a_word(word):
    meanings = []
    synsets_of_word = wordnet.synsets(word)

    for synset in synsets_of_word:
        meanings.append([synset, synset.definition()])

    return meanings


def get_translation_of_a_word(word, language_code):
    #TODO compare with wiktionary entries and switch to wiktionary if contents are kinda the same

    url = "https://api.mymemory.translated.net/get?q=" + word + "&langpair=" + language_code + "|de"
    response = requests.post(url).json()

    return response['responseData']['translatedText']


def get_english_language_data_from_wiktionary(content_of_page):
    output = []
    h2_element_english_found = False
    for test in content_of_page.children:
        if test == '\n':
            continue

        if test.name == "h2" and h2_element_english_found:
            break

        if h2_element_english_found:
            if len(output) == 0 and test.name != "h3":
                continue

            output.append(test)
            continue

        possible_h2_element_english = test.find("span", class_="mw-headline", id="English")
        if possible_h2_element_english:
            h2_element_english_found = True

    return output


def filter_english_language_data_from_wiktionary(data):
    dict_filtered_information = dict()
    current_set_of_info = []
    current_info_title = ""
    for element in data:
        # TODO replace by adding text of first element to current_info_title and remove element from list
        if len(current_set_of_info) == 0 and current_info_title == "":
            current_info_title = element.text.replace('[edit]', '')
            continue

        if element.name == 'h3':
            dict_filtered_information[current_info_title] = current_set_of_info
            current_set_of_info = []
            current_info_title = element.text.replace('[edit]', '')
            continue

        current_set_of_info.append(element)

        if element == data[-1]:
            dict_filtered_information[current_info_title] = current_set_of_info

    return dict_filtered_information


def remove_unimportant_data_from_filtered_wiktionary_data(data):
    entries_to_remove = [
        'See also',
        'Anagrams',
        'Related terms',
        'Etymology'
    ]

    for element in entries_to_remove:
        if element in data:
            del data[element]

    return data


def get_pronunciation_of_word_from_wiktionary_data(wiktionary_data):
    pronunciation = ""

    for element in wiktionary_data:
        pronunciations = element.text.split('\n')

        for pro_ele in pronunciations:
            if 'UK' not in pro_ele or 'Received Pronunciation' not in pro_ele:
                continue

            indices_pronun = [i for i, x in enumerate(pro_ele) if x == '/']
            pronunciation = pro_ele[indices_pronun[0]:indices_pronun[1]+1]
            break

    return pronunciation


def get_meanings_of_word_from_wiktionary_data(wiktionary_data):
    meanings = []

    for element in wiktionary_data:
        if element.name != 'ol':
            continue

        for test in element:
            if test == '\n':
                continue

            meanings.append(test.text.split('\n')[0])

    return meanings


def get_translations_of_word_from_wiktionary_data(wiktionary_data):
    idx_first_translations_element = 0
    for idx, element in enumerate(wiktionary_data):
        if element.name == 'h4' and 'Translations' in element.text:
            idx_first_translations_element = idx

    translations_elements = wiktionary_data[idx_first_translations_element+1:]
    output = list()

    for idx1, translation_element in enumerate(translations_elements):
        translation_element_class = translation_element.attrs['class'] if 'class' in translation_element.attrs else ''
        translation_element_id = translation_element.attrs['id'] if 'id' in translation_element.attrs else ''

        if translation_element_class != ['NavFrame'] and translation_element_id != '':
            continue

        german_translations = list()
        formatted_translation_list = translation_element.text.split('\n')
        for single_translation in formatted_translation_list:
            if single_translation == '':
                continue

            if 'German' not in single_translation:
                continue

            translations_string = single_translation.replace('German:', '')
            translations_list = [idx1] + translations_string.split(',')

            german_translations.append(translations_list)

        if len(german_translations) == 0:
            continue

        output.append(german_translations)

    return output


def parse_wiktionary_page(word):
    req = requests.get("https://en.wiktionary.org/wiki/" + word)
    soup = BeautifulSoup(req.content, 'html.parser')

    # @TODO check if page exists (API call)
    page_content = soup.find("div", class_="mw-parser-output")

    data_from_wiktionary = get_english_language_data_from_wiktionary(page_content)

    dict_filtered_information = filter_english_language_data_from_wiktionary(data_from_wiktionary)

    dict_filtered_information = remove_unimportant_data_from_filtered_wiktionary_data(dict_filtered_information)

    word_meanings = dict()
    pronunciation = ""
    translations = dict()
    for k,v in dict_filtered_information.items():
        if k in ['Further reading']:
            continue

        if k == "Pronunciation":
            pronunciation = get_pronunciation_of_word_from_wiktionary_data(v)
            continue

        word_meanings[k] = get_meanings_of_word_from_wiktionary_data(v)
        translations[k] = get_translations_of_word_from_wiktionary_data(v)

    return word_entity(pronunciation, word_meanings, translations)


def collect_information_for_words(list_of_words):

    """
    create output list
    for each word:
        get meaning of word
        get translation of word
        get pronunciation of word
        put all information into a list [word_en, word_de, word_pronunciation, word_meaning]
        add new list element to output list
        wait 1 second before making API calls/requests
    return output list
    """


def anki_stuff():
    """
    open collection
    get all cards from target deck
    for each new word - check if note is already list of cards from above
        yes: skip
        no: collect
    add all new notes via add_notes(nmodel, [[word1_en, word1_de, word1_word_pronunciation, word1_meaning], [word2_en, ...]]
    save changes via col.write(add=True)
    """

    # always needed
    col = Collection()

    # adds one new note (function returns an object!) and saves it into the collection
    test = col.notes.add_note('Englisch', ['englisches wort', 'deutsches wort', 'aussprache', 'bedeutung'], inplace=True)
    col.write(add=True)

    # lists all decks with cards in them
    print(col.cards.list_decks())


def main():
    wiktionary_word_entity = parse_wiktionary_page('example')
    print(1231)


if __name__ == '__main__':
    main()