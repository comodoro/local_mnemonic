import os
import datetime
import re
import unicodedata
from nltk.corpus.reader.plaintext import PlaintextCorpusReader
from nltk.probability import FreqDist

ADJECTIVES = ''
NOUNS = 'JT'
SUBSTANTIVES = 'ZUHPM'
CORPUS_DIR = 'build/corpus'
WORD_COUNT=2048
ALL = False
SUBSTS_ONLY = True
DIACRITICS = True
FILTER = 'foreign.jl'

def pseudo_hamming(s1, s2):
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))

def keep_distance(words, frequencies):
    filtered_words = []
    for word in words:
        filtered_words.append(word)
        for old_word in filtered_words:
            if (old_word[:5] == word[:5] or (old_word[0] == word[0] and
                pseudo_hamming(old_word, word) < 2)) and not word == old_word:
                if frequencies[word] > frequencies[old_word]:
                    filtered_words.remove(old_word)
                    print('%s filtered' % old_word)
                else:
                    filtered_words.remove(word)
                    print('%s filtered' % word)
                break
    return filtered_words

def get_spellcheck_candidates():
    hun_candidates = {
    'adjectives': set(),
    'substantives': set(),
    'nouns': set()
    }
    with open(CORPUS_DIR+'/cs_CZ.dic', encoding='utf8') as hunspell_file:
        for line in hunspell_file:
            chunks = line.split('/')
            if len(chunks) != 2:
                continue
            flags = chunks[1]
            if[f for f in flags if f in ADJECTIVES]:
                hun_candidates['adjectives'].add(chunks[0])
            if[f for f in flags if f in NOUNS]:
                hun_candidates['nouns'].add(chunks[0])
            if[f for f in flags if f in SUBSTANTIVES]:
                hun_candidates['substantives'].add(chunks[0])
    return hun_candidates

def filter_word_list(word_list, filter_list):
    for word in word_list:
        if word in filter_list:
            word_list.remove(word)

def load_filter_list(json_file):
    filter_list = []
    with open(json_file, 'r', encoding='utf8') as filter_file:
        for line in filter_file:
            filter_list.append(json.loads(line)['word'])
    return sorted(filter_list)

start = datetime.datetime.now()

assert os.path.isdir(CORPUS_DIR)

newcorpus = PlaintextCorpusReader(CORPUS_DIR, '.*\.txt')
print ('Corpus begins with {}'.format(newcorpus.words()[:10]))
frequencies = FreqDist(newcorpus.words())
print('Samples: %d' % frequencies.N())
print('Words: %d' % frequencies.B())
pattern = '^[a-zěščřžýáýíéóďťňúů]*$' if DIACRITICS else '^[a-z]*$'
candidates = {word: freq for (word, freq) in frequencies.most_common()
    if 6 < len(word) < 9 and re.match(pattern,word)}
print('Candidates: %d' % len(candidates))
print ((datetime.datetime.now() - start).total_seconds())
spell = get_spellcheck_candidates()
print('Spellchck candidates:\nAdjectives %d\nSubstantives %d\nNouns %d'
    % (len(spell['adjectives']), len(spell['substantives']), len(spell['nouns'])))
print ((datetime.datetime.now() - start).total_seconds())
substs = [word for word in candidates.keys() if word in spell['substantives']]
substs.sort(key=lambda subst : -candidates[subst])
adjs = [word for word in candidates.keys() if word in spell['adjectives']]
adjs.sort(key=lambda adj : -candidates[adj])
nouns = [word for word in candidates.keys() if word in spell['nouns']]
nouns.sort(key=lambda noun : -candidates[noun])
print ((datetime.datetime.now() - start).total_seconds())
print('All words: substantives %d, adjectives %d, nouns %d' % (len(substs), len(adjs), len(nouns)))

filter_list = load_filter_list(FILTER)
substs = [x for x in substs if not x in filter_list]
adjs = [x for x in adjs if not x in filter_list]
nouns = [x for x in nouns if not x in filter_list]
print('Filtered words: substantives %d, adjectives %d, nouns %d' % (len(substs), len(adjs), len(nouns)))
substs = keep_distance(substs, candidates)
adjs = keep_distance(adjs, candidates)
nouns = keep_distance(nouns, candidates)
print('Filtered words: substantives %d, adjectives %d, nouns %d' % (len(substs), len(adjs), len(nouns)))

if ALL:
    words = sorted(sum([substs, adjs, nouns],[]), key=lambda w : -candidates[w])
elif SUBSTS_ONLY:
    words = substs
print('Chosen words: %d' % len(words))

if not ALL and not SUBSTS_ONLY:
    words = (adjs[:512] + nouns[:512] + substs)[:2048]
else:
    words = words[:2048]
words.sort(key=lambda word: unicodedata.normalize('NFKD', word))
with open('build/wordlist', 'w', encoding='utf8') as wordlist:
    for word in words:
        wordlist.write(word+'\n')
print ((datetime.datetime.now() - start).total_seconds())
