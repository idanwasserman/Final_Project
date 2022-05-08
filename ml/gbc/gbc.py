from .constants import *
import pandas
import re
from itertools import groupby
import collections
import math 
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
import joblib


def create_gbc_model():
    # Read data from files
    print("Reading data from files...")
    df_list = read_data_from_files(FILES_LIST)
    
    # Create a dataframe
    print("Creating a dataframe...")
    dataframe = create_dataframe(df_list)
    
    # Train model
    print("Training model...")
    clf = get_trained_model(dataframe)

    # Save model
    print("Saving model...")
    with open(GB_MODEL_FILE_NAME, 'wb') as f:
        pickle.dump(clf, f)


def get_trained_model(dataframe):
    # Remove unnecessary columns 
    data = dataframe.drop(columns=[RAW_SQL, TYPE, SQL_TOKENS, TOKEN_SEQ])

    labelencoder_y = LabelEncoder()
    sc_X = StandardScaler()

    X = data.values
    y = labelencoder_y.fit_transform(dataframe[TYPE].tolist())
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    X_train = sc_X.fit_transform(X_train)
    X_test = sc_X.transform(X_test)

    return GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=7, random_state=0).fit(X_train, y_train)


def read_data_from_files(files_list):
    # import os
    # for subdir, dirs, files in os.walk('./ml/gbc/training_data/'):
    #     print(f"subdir: {subdir}")
    #     print(f"dirs: {dirs}")
    #     print(f"files: {files}")
    df_list = []
    for file_path in files_list:           
        df = pandas.read_csv(file_path, names=[RAW_SQL], sep='__', header=None, engine=PYTHON)            
        df[TYPE] = PLAIN if PLAIN in file_path else SQLI
        df_list.append(df)

    return df_list


def create_dataframe(df_list):
    # Make dataframe like excel format with pandas
    dataframe = pandas.concat(df_list, ignore_index=True)
    dataframe.dropna(inplace=True)

    # Tokenize raw sql
    dataframe[SQL_TOKENS] = dataframe[RAW_SQL].map(lambda x: Sql_tokenizer(x))

    # Get token sequences
    dataframe[TOKEN_SEQ] = dataframe[SQL_TOKENS].map(lambda x: get_token_seq(x, 3))

    _tokens, _types = zip(*[(token, token_type) for token_list, token_type in zip(dataframe[TOKEN_SEQ], dataframe[TYPE]) for token in token_list])
    tc_dataframe = G_test(pandas.Series(_tokens), pandas.Series(_types))
    tc_dataframe.to_pickle(TC_DF_FILENAME)

    # Now we set real features for machine learning algorithm
    dataframe[TOKEN_LENGTH] =   dataframe[SQL_TOKENS]   .map(lambda x: len(x))
    dataframe[ENTROPY] =        dataframe[RAW_SQL]      .map(lambda x: Entropy(x))
    dataframe[SQLI_G_MEANS] =   dataframe[TOKEN_SEQ]    .map(lambda x: G_means(x, SQLI_GTEST))
    dataframe[PLAIN_G_MEANS] =  dataframe[TOKEN_SEQ]    .map(lambda x: G_means(x, PLAIN_GTEST))

    return dataframe


def Sql_tokenizer(raw_sql):
    sql_regex = re.compile(SQL_REGEX, re.IGNORECASE)

    if sql_regex.search(raw_sql):
        return [tok[0] for tok in groupby([match.lastgroup for match in sql_regex.finditer(raw_sql)])]
    else:
        return [PLAIN.upper]


def get_token_seq(token_list, N):
    token_seq = []
    for n in range(0, N):
        token_seq += zip(*(token_list[i: ] for i in range(n + 1)))
    
    return [str(tuple) for tuple in token_seq]


# Pre-processing to get G-Test score
def G_test(tokens, types):
    tokens_cnt = tokens.value_counts().astype(float)
    types_cnt = types.value_counts().astype(float)
    total_cnt = float(sum(tokens_cnt))

    # Calculate each token counts
    token_cnt_table = collections.defaultdict(lambda : collections.Counter())
    for _tokens, _types in zip(tokens.values, types.values):
        token_cnt_table[_tokens][_types] += 1

    tc_dataframe = pandas.DataFrame(list(token_cnt_table.values()), index=token_cnt_table.keys())
    tc_dataframe.fillna(0, inplace=True)

    # calculate expected, g-score
    for column in tc_dataframe.columns.tolist():
        tc_dataframe[column + '_exp'] = (tokens_cnt / total_cnt) * types_cnt[column]
        tc_dataframe[column + '_GTest'] = [G_test_score(tkn_count, exp) for tkn_count, exp in zip(tc_dataframe[column], tc_dataframe[column+'_exp'])]

    return tc_dataframe


def G_test_score(count, expected):
        if (count == 0):
            return 0
        else:
            return 2.0 * count * math.log(count / expected)


def Entropy(raw_sql):
    p, lns = collections.Counter(str(raw_sql)), float(len(str(raw_sql)))
    return -sum( count/lns * math.log(count/lns, 2) for count in p.values())


def G_means(token_seq, c_name):
    tc_dataframe = pandas.read_pickle(TC_DF_FILENAME)

    try:
        g_scores = [tc_dataframe.loc[token][c_name] for token in token_seq]
    except KeyError:
        return 0
    return sum(g_scores)/len(g_scores) if g_scores else 0 # Average


def load_model():
    return joblib.load(GB_MODEL_FILE_NAME)


def gbc_predict(input):
    _tmp = re.sub(r'(/\*[\w\d(\`|\~|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\-|\_|\=|\+|\[|\{|\]|\}|\\|\:|\;|\'|\"|\<|\>|\,|\.|\?)\s\r\n\v\f]*\*/)', ' ', input)
    _tmp = re.sub(r'(/\*!\d+|\*/)', ' ', _tmp)

    sql_tokens = Sql_tokenizer(_tmp.strip())
    token_seq = get_token_seq(sql_tokens, 3)
    sqli_g_means = G_means(token_seq, SQLI_GTEST)
    plain_g_means = G_means(token_seq, PLAIN_GTEST)
    _X = [[len(sql_tokens), Entropy(input), sqli_g_means, plain_g_means]]
    clf = load_model()
    
    result = clf.predict(_X)[0]
    if result == 1:
        return 1
    else:
        return 0