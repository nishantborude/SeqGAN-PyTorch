import glob
from sklearn.model_selection import train_test_split
import numpy as np 

import collections
import itertools
# import typing

import torch
# import transformer

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

def generate_sentence_from_id(idx_to_word, input_ids, file_name = None, header = ''):
    sentence = []
    if file_name:
        out_file = open(file_name, 'a')
        out_file.write(header + ':')

    sep = ''
    for id in input_ids:
        sentence.append(idx_to_word[id])
        if file_name:
            out_file.write(sep + idx_to_word[id])
            sep = ' '
    if file_name:
        out_file.write('\n')
        out_file.close()
    return sentence

def generate_file_from_sentence(sentences, out_file, word_to_idx, generated_num = 0):
    if generated_num:
        generated_index = np.random.choice(len(sentences), generated_num)
    else:
        generated_index = np.arange(0, len(sentences))

    out_file = open(out_file, "w")
    for i in generated_index:
        sent = sentences[i].split(' ')
        new_sent_id = []
        sep = ''
        for word in sent:
           out_file.write(sep + str(word_to_idx[word.lower()]))
           sep = ' '
        out_file.write('\n')

def generate_real_data(input_file, batch_size, generated_num, idx_to_word, word_to_idx, train_file, test_file = None):
    train_sen, test_sen = load_from_big_file(input_file)

    generate_file_from_sentence(train_sen, train_file, word_to_idx, generated_num)
    if test_file:
        generate_file_from_sentence(test_sen, test_file, word_to_idx)



def save_vocab(checkpoint, idx_to_word, word_to_idx, vocab_size):
    """
    out_file = open(checkpoint+'idx_to_word.pkl', "wb")
    pickle.dump(idx_to_word, out_file)
    out_file.close()
    
    out_file = open(checkpoint+'word_to_idx.pkl', "wb")
    pickle.dump(word_to_idx, out_file)
    out_file.close()

    out_file = open(checkpoint+'vocab_size.pkl', "wb")
    pickle.dump(vocab_size, out_file)
    out_file.close()
    """
    torch.save(idx_to_word, checkpoint+'idx_to_word.info')
    torch.save(word_to_idx, checkpoint+'word_to_idx.info')
    torch.save(vocab_size, checkpoint+'vocab_size.info')

def load_vocab(checkpoint):
    idx_to_word = torch.load(checkpoint+'idx_to_word.info')
    word_to_idx = torch.load(checkpoint+'word_to_idx.info')
    vocab_size  = torch.load(checkpoint+'vocab_size.info')
    return idx_to_word, word_to_idx, vocab_size
   
