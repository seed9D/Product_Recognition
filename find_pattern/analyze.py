#!/usr/bin/python3
#-*-coding:utf-8 -*-

import os 
import sys
from collections import defaultdict
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

def load_alg_file(path):
    all_alg_dict = defaultdict(lambda: {'accept': 0, 'reject': 0})
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            line = line.split('\t')
            if len(line) == 3:
                key, accept, reject = line
                all_alg_dict[key]['accept'] = float(accept)
                all_alg_dict[key]['reject'] = float(reject)
    return all_alg_dict



def load_real_file(path):
    real_set = set()
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            line = line.split('\t')
            if len(line) == 2:
                real_set.add(line[0])
    return real_set


def filter_positive(all_alg_dict):
    positive_dict = {}
    for k, v in all_alg_dict.items():
        # print('{} accept:{} reject {}'.format(k, v['accept'], v['reject']))
        if v['accept'] > v['reject']:
            positive_dict[k] = v
            positive_dict[k]['accept'] = int((v['accept']))
            positive_dict[k]['reject'] = int((v['reject']))
    
    print('total postive record:{}'.format(len(positive_dict.keys())))
    return positive_dict

def compare_real_and_pos(real, alg_guess):
    alg_guess_set = set(alg_guess.keys())
    and_set = real & alg_guess_set
    diff_set = real - alg_guess_set
    # print(diff_set)
    print(diff_set)
    print('real:{} guess:{}'.format(len(real), len(alg_guess_set)))
    print('diff_set {}'.format(len(diff_set)))
    print('precise rate:{:.4f}'.format(len(and_set) / len(alg_guess_set)))
    print('recall rate:{:4f}'.format(len(and_set) / len(real)))

def analyze():
    real_set = load_real_file(os.path.join(root_dir, 'usr', 'word_.txt'))
    all_alg_dict = load_alg_file(os.path.join(root_dir, 'usr', 'all_alg.txt'))
    positive_dict = filter_positive(all_alg_dict)
    compare_real_and_pos(real_set, positive_dict)


if __name__ == '__main__':
    analyze()
