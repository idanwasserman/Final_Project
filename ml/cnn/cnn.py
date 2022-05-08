from keras.models import load_model
import pickle
import re


MODEL_PATH = "./ml/cnn/my_model.h5"
VECTORIZER_PATH = "./ml/cnn/vectorizer"

cnn_model = load_model(MODEL_PATH)
vectorizer = pickle.load(open(VECTORIZER_PATH, 'rb'))


def clean_data(input_val):    

    input_val=input_val.replace('\n', '')
    input_val=input_val.replace('%20', ' ')
    input_val=input_val.replace('=', ' = ')
    input_val=input_val.replace('((', ' (( ')
    input_val=input_val.replace('))', ' )) ')
    input_val=input_val.replace('(', ' ( ')
    input_val=input_val.replace(')', ' ) ')
    input_val = replace_numbers_with_keyword(input_val, 'numeric')
    
    return input_val


def replace_numbers_with_keyword(input, key):
    return re.sub('[0-9]+', key, input)


def cnn_predict(input):

    input = clean_data(input)

    input = [ input ]

    input = vectorizer.transform(input).toarray()

    result = cnn_model.predict(input)

    if result > 0.5:
        return 1
    else:
        return 0 
