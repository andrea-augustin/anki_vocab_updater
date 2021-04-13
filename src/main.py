import requests

from ankipandas import Collection
from tkinter import filedialog
from nltk.corpus import wordnet, cmudict


cmu_to_ipa_dict = dict()


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
    url = "https://api.mymemory.translated.net/get?q=" + word + "&langpair=" + language_code + "|de"
    response = requests.post(url).json()

    return response['responseData']['translatedText']


def get_pronunciation_of_a_word(word):

    print(1231)


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


def init_cmu_to_ipa_dict():
    global cmu_to_ipa_dict

    with open('cmu_to_ipa.txt', 'r', encoding='utf-8') as f:
        file_content = f.read()

    lines = file_content.split('\n')
    for pronunciation_entry in lines:
        pron = pronunciation_entry.split('\t')
        cmu_to_ipa_dict[pron[0]] = pron[1]


def main():
    init_cmu_to_ipa_dict()
    #get_pronunciation_of_a_word('dogma')
    print(1231)


if __name__ == '__main__':
    main()