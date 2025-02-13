"""
Developer:          Anirban Saha. 
Version:            v1.0 (released)
Date:               13.05.2020 
Description:        Takes two texts and returns to them a 11 bit vector. The first 7 spaces indicate the similarity distance. The next 4 spaces indicate whether or not they have the negation word "not"
Documentation Link: [Not there yet]
Dependencies:       Google News Dataset         
Version History:
Version |   Date    |  Change ID |  Changes  
"""

import os
import pickle
from nltk.corpus import stopwords
from gensim.models import KeyedVectors

#from nltk import download
#import urllib.request
#import xml.etree.ElementTree as ET
#download('stopwords')                                       # Download stopwords list.

# define global variables to ensure they are loaded once in the RAM to reduce time and space complexity
model = None
stop_words = None

def load_model():
    stop_words = stopwords.words('english')
    GoogleNews_word2vec_pickle = "../data/similarity/GoogleNews-vectors-negative300.pickle"

    print('-'*50)
    print('Check if pre-trained Word2vec model trained on Google News corpus exists in disk')
    if os.path.exists(GoogleNews_word2vec_pickle): 
        print('\nModel found! Loading...')
        model = pickle.load(open(GoogleNews_word2vec_pickle, 'rb'))
        print('Model loaded.')
        return stop_words, model
    else:
        print('\nModel not found!')
        try:
            """
            Creates a model from the Google News Dataset.
            """ 
            GoogleNews_word2vec_binary = "../data/similarity/GoogleNews-vectors-negative300.bin.gz"
            print('\tCheck if the binary of Google News Dataset present in disk')
            if not os.path.exists(GoogleNews_word2vec_binary):                #this file path needs to change when integrated into main program. 
                raise ValueError("\tERROR: You need to download the google news model")
            print("\tBinary of Google News Dataset found. Now loading...")
            model = KeyedVectors.load_word2vec_format(GoogleNews_word2vec_binary, binary=True)
            print("\tThe Google News Dataset is loaded. Model initialising...")
            model.init_sims(replace=True)
            print("Model loaded.")
            pickle.dump(model, open(GoogleNews_word2vec_pickle, 'wb'))
            print("Model pickled")
            return stop_words, model

        except:
            print("\tThe Google News dataset is not downloaded yet.")

if model is None:
    stop_words, model = load_model()
else:
    print('-'*50)
    print('Model and Stopwords already loaded in RAM!')

"""
Description:    Finds the word movers distance between two pieces of texts. 
Input:          Text A (premise), Text B (hypothesis). 
Output:         word movers distance. 
"""
def find_similarity(text_A, text_B):
    text_A = text_A.lower().split()
    text_B = text_B.lower().split()
    text_A = [w for w in text_A if w not in stop_words]
    text_B = [w for w in text_B if w not in stop_words]
    return model.wmdistance(text_A, text_B)

"""
Description:    Finds out at which positions the word appears in a list of words.
Input:          List of words. 
Output:         Positions where the word appears.  
"""
def find_indexes_in_text(list_words, word):  
    return [i for i in range(len(list_words)) if list_words[i] == word]

"""
Description:    Finds out the ngrams containing the word and returns a list of such phrases.  
Input:          Text, word, and number of words in each phrase.  
Output:         List of phrases
"""
def return_negation_phrases_from_text(text, word, ngram):
    original_word = word
    if ' ' in word: 
        word = word.replace(' ','') 
        text = text.replace(original_word, word) 

    list_words = text.split()
    pad_word = f' {word} '
    return_phrases = []
    phrase = '' 

    if pad_word in text:  
        if ngram % 2 == 0: ngram = ngram + 1
        low_lim = (ngram // 2) * (-1)
        upp_lim = (ngram //2)
        i = low_lim

        indexes_of_word = find_indexes_in_text(list_words, word) 

        for index in indexes_of_word:
            list_words[index] = list_words[index].replace(word, original_word)
            while i<= upp_lim:
                try:
                    phrase = f'{phrase} {list_words[index + i]}'
                except Exception:
                    phrase = phrase
                i = i + 1
            phrase = phrase.strip()
            return_phrases.append(phrase)
            phrase = ''
            i = low_lim
    return return_phrases


"""
Description:    Creates vectors to use in the main program. 
Input:          Text A (premise), Text B (hypothesis), ngram (number of words in ngram) 
Output:         Vector (one hot encoded) 
"""
def get_sim_vector_for_pair(text1, text2, ngram = 4, word = 'not'):
    text1_phrases = return_negation_phrases_from_text(text1, word, ngram)
    text2_phrases = return_negation_phrases_from_text(text2, word, ngram)
    distance = find_similarity(text1, text2) 

    if 0 <= distance <= 0.2:     vector = [1,0,0,0,0,0,0]
    if 0.2 < distance <= 0.4:    vector = [0,1,0,0,0,0,0]
    if 0.4 < distance <= 0.6:    vector = [0,0,1,0,0,0,0]
    if 0.6 < distance <= 0.8:    vector = [0,0,0,1,0,0,0]
    if 0.8 < distance <= 1.0:    vector = [0,0,0,0,1,0,0]
    if distance > 1.0 and distance != 'inf':  vector = [0,0,0,0,0,1,0]
    if distance == 'inf':                     vector = [0,0,0,0,0,0,1] 

    if text1_phrases and text2_phrases:       
        add_vector = [0,0,0,1]
    elif text1_phrases: 
        add_vector = [0,1,0,0]
    elif text2_phrases: 
        add_vector = [0,0,1,0]
    else:                                     
        add_vector = [0,0,0,0] 

    for element in add_vector:
        vector.append(element) 

    return vector