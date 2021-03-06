import glob
from sklearn.model_selection import train_test_split
import numpy as np 

import collections
import itertools

import torch

from torch import nn
from torch import optim
import sys



NUMBER_OF_SENTENCES = 100

Token = collections.namedtuple("Token", ["index", "word"])
SOS = Token(0, "<sos>")
EOS = Token(1, "<eos>")
PAD = Token(2, "<pad>")

def load_from_big_file(file):
    s = []
    
    with open(file) as f:
        lines = f.readlines()
    
        for line in lines[:NUMBER_OF_SENTENCES]:
            line = line.strip()
            line = line.rstrip(".")
            words = line.split()
            for i in range(len(words)):
                words[i] = words[i].strip(',"')
            if len(words) >= 10:
                sent = " ".join(words[:10])
                sent += " ."
            else:
                sent = " ".join(words)
                sent += " ."
                sent += (" "+PAD.word) * (10 - len(words)) 
            s.append(sent)
    
    s_train, s_test= train_test_split(s, shuffle = True, test_size=0.1, random_state=42)
    return s_train, s_test[:2]

def fetch_vocab(DATA_GERMAN, DATA_ENGLISH, DATA_GERMAN2): # -> typing.Tuple[typing.List[str], typing.Dict[str, int]]:
    """Determines the vocabulary, and provides mappings from indices to words and vice versa.
    
    Returns:
        tuple: A pair of mappings, index-to-word and word-to-index.
    """
    # gather all (lower-cased) words that appear in the data
    all_words = set()
    for sentence in itertools.chain(DATA_GERMAN, DATA_ENGLISH, DATA_GERMAN2):
        all_words.update(word.lower() for word in sentence.split(" ") if word != PAD.word) 
    
    # create mapping from index to word
    idx_to_word = [SOS.word, EOS.word, PAD.word] + list(sorted(all_words))
    
    # create mapping from word to index
    word_to_idx = {word: idx for idx, word in enumerate(idx_to_word)}
   
    return idx_to_word, word_to_idx

def generate_sentence_from_id(idx_to_word, input_ids, file_name, header = ''):
    sentence = []
    out_file = open(file_name, 'a')
    sep = ''
    out_file.write(header + ':')
    for id in input_ids:
        sentence.append(idx_to_word[id])
        out_file.write(sep + idx_to_word[id])
        sep = ' '
    out_file.write('\n')
    out_file.close()
    return sentence

def generate_real_data(input_file, batch_size, generated_num, positive_file, idx_to_word, word_to_idx):
    train_sen, _ = load_from_big_file(input_file)
    generated_index = np.random.choice(len(train_sen), generated_num)
    
    out_file = open(positive_file, "w")
    for i in generated_index:
        sent = train_sen[i].split(' ')
        new_sent_id = []
        sep = ''
        for word in sent:
           out_file.write(sep + str(word_to_idx[word.lower()]))
           sep = ' '
        out_file.write('\n')

