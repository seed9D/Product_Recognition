#!/usr/bin/python3
#-*-coding:utf-8 -*-
import sys
import os
import argparse
from product_recognition import Product_Recognition
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import help_func as hf
sub_dir = 'recognition'


def load_model(model_p, char_vec_index_p, word_vec_inde_p, tag_vob_p):
    frozen_graph_filename = model_p
    char_index_path = char_vec_index_p
    word_index_path = word_vec_inde_p
    tag_index_path = tag_vob_p
    return Product_Recognition(frozen_graph_filename, char_index_path, word_index_path, tag_index_path)


def run_product_recognition(test_file, model_p, char_vec_index_p, word_vec_inde_p, tag_vob_p):
    product_recognition = load_model(
        model_p, char_vec_index_p, word_vec_inde_p, tag_vob_p)
    result_list = product_recognition.run_recognition(test_file)
    return result_list


def load_test_file(file_path):
    with open(file_path, 'r') as f:
        test_list = []
        for line in f.readlines()[-20000:]:
            line = line.strip()
            line = line.split('\t')
            line = [l.split('/')[0] for l in line]
            test_list.append(line)
        return test_list


def load_unrecongnization_file(file_path):
    with open(file_path, mode='r') as rf:
        ur_list = []
        for line in rf.readlines():
            line = line.strip()
            line = line.split(' ')
            ur_list.append(line)
        return ur_list


def write_recongnization_result(path, result_list):
    with open(os.path.join(path), mode='w') as wf:
        for one_line in result_list:
            for token in one_line:
                word, tag = token
                wf.write('{}/{}\t'.format(word, tag))
            wf.write('\n')


def fetch_product_name(result_list):
    product_set = set()
    for one_line in result_list:
        temp_list = []
        for token in one_line:
            word, tag = token
            if tag is 'S':
                product_set.add(word)
            elif tag is 'B':
                temp_list.append(word)
            elif tag is 'I':
                temp_list.append(word)
            elif tag is 'E':
                temp_list.append(word)
                product_set.add(''.join(temp_list))
                temp_list = []
                continue
    print('fetch {} product name'.format(len(product_set)))
    for ele in product_set:
        print(ele, end=' ')
    print()
    return product_set


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test_file',
                        help='the segmented sentence file you want to recognize product name in it',
                        action='store')

    parser.add_argument('--recognize_result',
                        help='output path of recongnized result',
                        action='store',
                        dest='output_recognize_result',
                        default=os.path.join(root_dir, 'usr', sub_dir, 'recognize_result.txt'))
    
    parser.add_argument('--product_name_result',
                        help='output path of recongnized product_name',
                        action='store',
                        dest='output_product_name_result',
                        default=os.path.join(root_dir, 'usr', sub_dir, 'discover_word.txt'))

    parser.add_argument('--frozen_graph',
                        help='recognization model path',
                        action='store',
                        dest='model_path',
                        default=os.path.join(root_dir, 'usr', sub_dir, 'product_model.pbtxt'))
    
    parser.add_argument('--char_vec_index',
                        help='char vector index file path',
                        dest='char_index_path',
                        default=os.path.join(root_dir, 'usr', sub_dir, 'char_vec_index.txt'))
    
    parser.add_argument('--word_vec_index',
                        help='word vector index file path',
                        dest='word_index_path',
                        default=os.path.join(root_dir, 'usr', sub_dir, 'word_vec_index.txt'))
    
    parser.add_argument('--tag_vob',
                        help='tag scheme index path',
                        dest='tag_vob_path',
                        default=os.path.join(root_dir, 'usr', sub_dir, 'tag_vocab.txt'))

    args = parser.parse_args()
    hf.check_dir_exist(args.output_path)

    input_list = load_unrecongnization_file(args.test_file)
    recognition_result_list = run_product_recognition(
        input_list, args.model_path, args.char_index_path, args.word_index_path, args.tag_vob_path)
    
    print('input len :{} output len :{}'.format(
        len(input_list), len(recognition_result_list)))
    product_name_set = fetch_product_name(recognition_result_list)

    hf.write_data(args.output_product_name_result, product_name_set)
    write_recongnization_result(
        args.output_recognize_result, recognition_result_list)
    
# def main(argc, argv):
#     if argc < 3:
#         print("Usage:%s <test file> <recognition_result>" % (argv[0]))
#         sys.exit(1)
#     input_file = argv[1]
#     recognition_result_path = argv[2]
#     input_list = load_unrecongnization_file(input_file)
#     result_list = run_product_recognition(input_list)
#     print('input:{} output:{}'.format(len(input_list), len(result_list)))
#     new_product_set = find_new_product(result_list)

#     write_data('./test_dir/new_product.txt', new_product_set)
#     write_recongnization_result(recognition_result_path, result_list)


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
