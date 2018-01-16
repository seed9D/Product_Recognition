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


def read_reference_file(reference_path):
    with open(reference_path, 'r') as rf:
        string_list = []
        for line in rf.readlines():
            line = line.strip()
            # split_line = re.split(r'[（）\[\]【】《》\(\).\\、|，,\/\s-]', line)
            split_line = re.split(r'[：；\-\+\(\)\\|，,《》（）【】/、&\s]', line)
            # print(split_line)
            split_line = list(filter(None, split_line))
            split_line = list(filter(lambda x: not x.isdigit(), split_line))
            string_list.extend(split_line)
    return string_list


def read_product_name(input_path):
    with open(input_path, 'r',) as rf:
        product_list = []
        for line in rf.readlines():
            line = line.strip()
            product_list.append(line)
    return product_list


def find_reference(reference_list, key):
    for reference in reference_list:
        find = reference.find(key)
        if find is not -1:
            return reference


def write_reference(output_path, product_reference_list):
    with open(output_path, 'w') as wf:
        for product_reference in product_reference_list:
            key, *v, reference = product_reference
            wf.write('{}\t'.format(key))
            for v_ in v:
                wf.write('{}\t'.format(v_))
            
            wf.write('{}\n'.format(reference))

def add_reference(input_path, reference_path, output_path):
    reference_list = read_reference_file(reference_path)
    product_list = read_product_name(input_path)
    product_list_len = len(product_list)
    product_reference_list = []

    for index, product in enumerate(product_list):
        key, *v = product.split('\t')
        reference = find_reference(reference_list, key)
        product_reference_list.append((key, *v, reference))
        if index % 250 == 0:
            print('{}/{}'.format(index, product_list_len))
    print('{}/{}'.format(index, product_list_len))
    product_reference_list = sorted(product_reference_list, reverse=False)
    write_reference(output_path, product_reference_list)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file',
                        help='the file you want to add reference',
                        action='store',
                        )
    parser.add_argument('reference_file',
                        help='the reference sentence file',
                        action='store',
                        )
    parser.add_argument('--user_dir',
                        help='user dir path',
                        action='store',
                        dest='user_dir',
                        default=os.path.join(root_dir, 'usr'))
    # parser.add_argument('--output',
    #                     help='the output path after adding reference',
    #                     action='store',
    #                     dest='output_path',
    #                     default=os.path.join(
    #                         root_dir, 'usr', sub_dir, 'product_reference.txt')
    #                     )
    # add_reference()
    args = parser.parse_args()
    output_path = os.path.join(
        args.user_dir, sub_dir, 'recognition_reference.txt')
    hf.check_dir_exist(os.path.join(args.user_dir, sub_dir))
    add_reference(args.input_file, args.reference_file, output_path)

if __name__ == '__main__':
    main()
