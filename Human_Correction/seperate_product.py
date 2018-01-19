#!/usr/bin/python3
#-*-coding:utf-8 -*-
import os
import sys
import argparse
import re
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import help_func as hf
sub_dir = 'human_correction'

def write_file(file_path, data):
    with open(file_path, 'w') as wf:
        for line in data:
            # for l in line:
            wf.write('{}\n'.format(line))
            # wf.write('\n')

def seperate(input_file_p, output_product_p, output_word_p):
    product_list = []
    word_list = []
    with open(input_file_p, 'r') as f:
        for line in f.readlines():
            line = line.strip()
            line = line.split('\t')
        
            key_index = 0
            if line[-1] == 'P':
                product_list.append(line[key_index])
                word_list.append(line[key_index])
            else:
                word_list.append(line[key_index])
    print('product len:{} word len:{}'.format(len(product_list), len(word_list)))
    write_file(output_product_p, product_list)
    write_file(output_word_p, word_list)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        help='the file you want to seperate',
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
    output_product = os.path.join(output_dir, 'product.txt')
    output_word = os.path.join(output_dir, 'word.txt')

    seperate(args.input_file, output_product, output_word)

if __name__ == '__main__':
    main()
