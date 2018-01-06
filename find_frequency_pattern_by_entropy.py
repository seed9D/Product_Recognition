#!/usr/bin/python3
#-*-coding:utf-8 -*-
import Tries
import re
from collections import Counter, defaultdict, ChainMap
import math
import jieba
from help_func import write_data
import os
import multiprocessing as mp

split_word = r'[：；\-\+\(\)\\|，,《》（）【】/、&\s]'
max_n_gram = 8
count_threshold = 10
mutual_entropy_threshold = 1e-6
neighbor_entropy_threshold = 0.7
cpu_num = mp.cpu_count()
proccess_num = cpu_num - 1

def read_data():
    split_pat = re.compile(split_word)
    with open('source.txt', 'r') as rf:
        def dedupe(items):
            '''no duplicate'''
            seen = set()
            for item in items:
                if item not in seen:
                    yield item
                    seen.add(item)
        string_list = []
        readlines = dedupe(rf.readlines())
        for line in readlines:
            line = line.strip()
            split_line = split_pat.split(line)
            split_line = list(filter(None, split_line))
            split_line = list(filter(lambda x: not x.isdigit(), split_line))
            string_list.extend(split_line)
        return string_list


def write_detail(dict_):
    sorted_key = sorted(dict_.keys())
    with open(os.path.join('./usr', 'detail_information.txt'), 'w') as wf:
        # for k, v in dict_.items():
        for k in sorted_key:
            v = dict_[k]
            # key, joint_probability, mutual entropy, left_entropy, right_entropy
            wf.write('{}\t{:.6f}\t{:.6f}\t{:6f}\t{:6f}\n'.format(k, v[0][0], v[0][1], v[0][2], v[0][3]))
            for left, write, left_pro, right_pro, pro_multiply, MI in v[1:]:
                wf.write('\t{}\t{}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\n'.format(
                    left, write, left_pro, right_pro, pro_multiply, MI))
        
def approcimate_total_world_num(string_list):
    total_word_num = 0
    for string in string_list:
        cut = jieba.cut(string)
        total_word_num += len([ele for ele in cut])
    return total_word_num


def get_all_distinct_substring(string_list, n_gram=5):
    assert len(string_list) > 0
    batch_size = 40

    def get_distinct_substring(sentence):
	    sf = Tries.Suffix_Trees(sentence)
	    return sf.total_distict_substring()

    string_list_len = len(string_list)
    print('total string list len:{}'.format(string_list_len))
    distict_substring_list = []
    for i in range(string_list_len):
        distict_substring = get_distinct_substring(string_list[i])
        distict_substring = list(
            filter(None, distict_substring))  # filter none
        distict_substring = list(filter(lambda x: n_gram >= len(
            x) > 0, distict_substring))  # filter length below n_gram
        distict_substring = list(
            filter(lambda x: not x.isdigit(), distict_substring))  # filter englich substring
        distict_substring_list.extend(distict_substring)
        if i % batch_size == 0 and i is not 0:
            yield distict_substring_list
            distict_substring_list = []
    yield distict_substring_list


def count_pattern_frequency(n_gram_list):
    pattern_dict = Counter()
    for one_line in n_gram_list:
        # approximate_total_word += len(segment_sentence(one_line))
        pattern_dict.update(one_line)
    return pattern_dict


def combine_detail_information(detail_dict, entropy_dict):
    for key in entropy_dict.keys():
        if key in detail_dict:
            left_ent, right_ent = entropy_dict[key]
            detail_dict[key][0].extend([left_ent, right_ent])

def calculate_mutual_entropy(dict_, approcimate_total_word_num):
    def word_probability(word):
        # assert(word_len_statistic), 'word:{} frequency:{} len_statistic:{}'.format(word, dict_[word], word_len_statistic)
        return (dict_[word] + 1) / approcimate_total_word_num
    MI_dict = {}
    detail_dict = defaultdict(list)
    for k, v in dict_.items():
        if v > count_threshold and len(k) > 1:        
            marginal_probability = [word_probability(
                k[:index]) * word_probability(k[index:]) for index in range(1, len(k))]
            marginal_probability = list(
                filter(lambda x: x > 0, marginal_probability))          
            if marginal_probability:
                min_marginal_probability = min(marginal_probability)
                join_probability = word_probability(k)
                '''mutual entropy'''
                mutual_entropy = sum(map(
                    lambda x: join_probability * math.log(join_probability / x), marginal_probability))
                if mutual_entropy > mutual_entropy_threshold:
                    MI_dict[k] = mutual_entropy

                    '''for detail'''
                    # print('{} {:.4f}'.format(k, mutual_entropy))
                    detail_dict[k].append([join_probability, mutual_entropy])
                    for index in range(1, len(k)):
                        left_pro = word_probability(k[:index])
                        right_pro = word_probability(k[index:])
                        pro_multpy = left_pro * right_pro
                        MI = join_probability * math.log(join_probability / pro_multpy)
                        detail_dict[k].append(
                            [k[:index], k[index:],  left_pro, right_pro, pro_multpy, MI])
                    #   print('\t {} {} {:.6f}'.format(k[:index], k[index:], MI))
                    # print()

    print('len MI:{}'.format(len(MI_dict.keys())))
    return MI_dict, detail_dict


def count_neighbor_entropy(key, mapping_list):
    def entropy(list_):
        count_dict = Counter(list_)
        conditional_prob = [v / len(list_) for v in count_dict.values()]
        entropy = (-1) * sum(
            map(lambda x: x * math.log(x), conditional_prob))
        return entropy
    match_list = []
    for string in mapping_list:
        # match one word left and right
        match = re.findall(r'(.){}(.)'.format(key), string)
        for m in match:
            match_list.append(m)
    left_entropy = entropy([m[0] for m in match_list])
    right_entropy = entropy([m[1] for m in match_list])
    # print(key, min(left_entropy, right_entropy))
    return (key, left_entropy, right_entropy)


def run_batch(*argc):
    assert(len(argc) == 2)
    key_list, string_list = argc

    def key_mappping():
        for key in key_list:
            mapping_list = []
            for string in string_list:
                if string.find(key) > 0:
                    mapping_list.append(string)
            yield key, mapping_list
    curerent_process = mp.current_process().name
    result_dict = {}
    for index, (key, mapping_list) in enumerate(key_mappping()):
        k, left_entropy, right_entropy = count_neighbor_entropy(
            key, mapping_list)
        result_dict[k] = (left_entropy, right_entropy)
        if index % 250 == 0:
            print('process: {} {}/{}'.format(curerent_process, index, len(key_list)))
    return result_dict

def calculate_free_degree(string_list, dict_):
    def key_mappping():  # find string containing key could reduce computation
        for key in dict_.keys():
            mapping_list=[]
            for string in string_list:
                if string.find(key) > 0:
                    mapping_list.append(string)
            yield key, mapping_list

    def get_batch(batch_size):
        key_list = []
        for key in dict_.keys():
            key_list.append(key)
            if len(key_list) == batch_size:
                yield key_list
                key_list = []
        yield key_list

    def multi_core(mapping_dict_gen):
        print('multi_core mode, proccess_num {}'.format(proccess_num))
        pool = mp.Pool(processes=proccess_num)
        total_computation = len(dict_.keys())
        batch_size = total_computation // proccess_num
        print('total_computation: {}, batch size: {}'.format(
            total_computation, batch_size))
        multi_result = []
        for batch_list in get_batch(batch_size):
            assert(isinstance(batch_list, list))
            multi_result.append(pool.apply_async(
                run_batch, args=(*(batch_list, string_list), )))
        pool.close()
        pool.join()
        entropy_dict = ChainMap(*[result.get() for result in multi_result])
        return entropy_dict


    entropy_dict = {}
    print('computation complexity: key len  {} string list {}'.format(
        len(dict_.keys()), len(string_list)))
    mapping_dict_gen = key_mappping()

    # for key, mapping_list in mapping_dict_gen:
    #     k, free_degree = count_neighbor_entropy(key, mapping_list)
    #     # if neighbor_entropy_threshold < free_degree:
    #     entropy_dict[k] = free_degree
    entropy_dict = multi_core(mapping_dict_gen)
    print('len free degree', len(entropy_dict.keys()))
    return entropy_dict


def find_frequency_pattern():
    string_list = read_data()
    # approcimate_total_word_num = approcimate_total_world_num(string_list)
    approcimate_total_word_num = len(string_list)
    print('total world len', approcimate_total_word_num)
    distict_substring_list_gen = get_all_distinct_substring(
        string_list, max_n_gram)
    pattern_dict = count_pattern_frequency(distict_substring_list_gen)
    MI_dict, detail_dict = calculate_mutual_entropy(
        pattern_dict, approcimate_total_word_num)
    sort_entropy = sorted(MI_dict.items(), key=lambda x: x[1], reverse=True)
    write_data(os.path.join('./usr', 'word_mutual_entropy.txt'), ('\t'.join([key, str(ent)]) for key, ent in list(sort_entropy)))

    entropy_dict = calculate_free_degree(string_list, MI_dict)
    sort_entropy = sorted(entropy_dict.items(), key=lambda x: x[1], reverse=True)
    write_data(os.path.join('./usr', 'word_entropy.txt'), ('\t'.join([key, str(left), str(right)]) for key, (left, right) in list(sort_entropy)))

    del string_list, pattern_dict, sort_entropy
    combine_detail_information(detail_dict, entropy_dict)
    write_detail(detail_dict)

if __name__ == '__main__':
    find_frequency_pattern()
