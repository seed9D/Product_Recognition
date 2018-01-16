#!/usr/bin/python3
#-*-coding:utf-8 -*-
import os
import sys
import argparse
import re
import jieba
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import help_func as hf

sub_dir = 'human_correction'


def read_file(input_p):
    word_set = set()
    with open(input_p, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            word_set.add(line)
    return list(word_set)

def decompose(input_p, output_p):
    word_list = read_file(input_p)
    len_of_two_and_three = [w for w in word_list if len(w) in [2, 3]]

    for word in len_of_two_and_three:
        jieba.add_word(word)
    
    result_set = set()
    for word in word_list:
        w = jieba.cut(word)
        for ele in w:
            result_set.add(ele)
    
    hf.write_data(output_p, result_set)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        help='the file you want to decompose',
                        action='store',
                        )
    parser.add_argument('--user_dir',
                        help='user dir path',
                        action='store',
                        dest='user_dir',
                        default=os.path.join(root_dir, 'usr'))
    args = parser.parse_args()

    output_dir = os.path.join(
        args.user_dir, sub_dir)
    hf.check_dir_exist(output_dir)
    output_bw = os.path.join(output_dir, 'base_word.txt')
   
    decompose(args.input_file, output_bw)


if __name__ == '__main__':
    main()
