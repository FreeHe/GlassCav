# ----------------------------------
# author : FreeHe
# github : https://github.com/FreeHe
# ----------------------------------
import pickle
import os

dic = {
    'dir': ''
}


def write_pickle(v, DIR):
    with open(DIR + '/conf.pkl', 'wb') as f:
        dic['dir'] = v
        pickle.dump(dic, f)


def read_pickle(DIR):
    if not os.path.isfile(DIR + '/conf.pkl'):
        write_pickle('', DIR)
        return DIR
    with open(DIR + '/conf.pkl', 'rb') as f:
        s = pickle.load(f)
        return s['dir'] if isinstance(s, dict) else ''
