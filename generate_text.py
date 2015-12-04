import sys
import os
import numpy as np
import unicodedata
import json


PUNCTUATION_TRANSLATE_TABLE = {i: None for i in range(sys.maxunicode)
    if (unicodedata.category(unichr(i)).startswith('P') and unichr(i) != '.')}


def normalize_text(text):
    text = text.lower().translate(PUNCTUATION_TRANSLATE_TABLE)
    return text


def add_words(text, two_words, three_words):
    words = normalize_text('.' + text + '.').replace('.', ' . ').split()
    (second, third) = words[0:2]

    for word in words[2:]:
        (first, second, third) = (second, third, word)
        if (first != '.' and second != '.'):
            three_words.setdefault(first, {}).setdefault(second, {})
            three_words[first][second].setdefault(third, 0)
            three_words[first][second][third] += 1

        if (first != '.' or second != '.'):
            two_words.setdefault(first, {}).setdefault(second, 0)
            two_words[first][second] += 1


def compute_statistics(directory):
    two_words = dict()
    three_words = dict()

    for doc in os.listdir(directory):
        text = open(directory + '/' + doc).read().decode('utf8')
        add_words(text, two_words, three_words)

    for first in three_words:
        for second in three_words[first]:
            total_count = sum(three_words[first][second].values())
            for third in three_words[first][second]:
                three_words[first][second][third] *= 1. / total_count

    for first in two_words:
        total_count = sum(two_words[first].values())
        for second in two_words[first]:
            two_words[first][second] *= 1. / total_count

    return {'two_words': two_words, 'three_words': three_words}


def generate_random_word(distribution):
    return np.random.choice(distribution.keys(), 1, distribution.values())[0]


def generate_text(statistics, words_count):
    two_words = statistics['two_words']
    three_words = statistics['three_words']

    text = []
    current_words_count = 0

    while (current_words_count < words_count):
        first = generate_random_word(two_words['.'])
        second = generate_random_word(two_words[first])

        text.extend([first.title(), second])
        current_words_count += 1

        while (second != '.'):
            third = generate_random_word(three_words[first][second])
            text.append(third)
            current_words_count += 1
            (first, second) = (second, third)

        if (np.random.randint(5) == 4):
            text.append('\n')

    return ' '.join(text).replace(' .', '.').replace(' \n ', '\n')


def save_statistics(statistics, output_file):
    f = open(output_file, 'w')
    f.write(json.dumps(statistics).encode('utf8'))
    f.close()


def read_statistics(input_file):
    f = open(input_file, 'r')
    json_text = f.read().decode('utf8')
    return json.loads(json_text)


statistics_file = 'statistics.txt'
save_statistics(compute_statistics('corpus'), statistics_file)
text = generate_text(read_statistics(statistics_file), 10000)

f = open('result.txt', 'w')
f.write(text.encode('utf8'))
