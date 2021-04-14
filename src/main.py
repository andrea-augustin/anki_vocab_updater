import requests

from ankipandas import Collection
from tkinter import filedialog
from nltk.corpus import wordnet
from bs4 import BeautifulSoup


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


def parse_wiktionary_page(word):
    req = requests.get("https://en.wiktionary.org/wiki/" + word)
    soup = BeautifulSoup(req.content, 'html.parser')

    stuff = parse_wiktionary_page(soup)

    # @TODO check if page exists (API call)
    page_content = soup.find("div", class_="mw-parser-output")
    h2_english_found = False
    elements_i_need = []
    # TODO create function: returns elements_i_need
    for test in page_content.children:
        if test == '\n':
            continue

        if test.name == "h2" and h2_english_found:
            break

        if h2_english_found:
            if len(elements_i_need) == 0 and test.name != "h3":
                continue

            elements_i_need.append(test)
            continue

        specific_thingie = test.find("span", class_="mw-headline", id="English")
        if specific_thingie:
            h2_english_found = True

    # TODO create function: returns dict_sorted_information
    dict_sorted_information = dict()
    current_set_of_info = []
    current_info_title = ""
    for element in elements_i_need:
        # TODO replace by adding text of first element to current_info_title and remove element from list
        if len(current_set_of_info) == 0 and current_info_title == "":
            current_info_title = element.text.replace('[edit]', '')
            continue

        if element.name == 'h3':
            dict_sorted_information[current_info_title] = current_set_of_info
            current_set_of_info = []
            current_info_title = element.text.replace('[edit]', '')
            continue

        current_set_of_info.append(element)

        if element == elements_i_need[-1]:
            dict_sorted_information[current_info_title] = current_set_of_info

    # TODO create function: elements to remove inside a list and iterate over list, returns cleaned dict_sorted_information
    if 'See also' in dict_sorted_information:
        del dict_sorted_information['See also']

    if 'Anagrams' in dict_sorted_information:
        del dict_sorted_information['Anagrams']

    if 'Related terms' in dict_sorted_information:
        del dict_sorted_information['Related terms']

    if 'Etymology' in dict_sorted_information:
        del dict_sorted_information['Etymology']

    return dict_sorted_information


def get_pronunciation_of_a_word(raw_data_from_wiktionary):
    # get pronuncation from wiktionary
    pass


def collect_information_for_words(list_of_words):

    """
    create output list
    for each word:
        get meaning of word
        get translation of word
        get pronunciation of word
        put all information into a list [word_en, word_de, word_pronunciation, word_meaning]
        add new list element to output list
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
    parse_wiktionary_page('dogma')
    print(1231)


if __name__ == '__main__':
    main()