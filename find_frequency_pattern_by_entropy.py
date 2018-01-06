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
max_n_gram = 5
count_threshold = 10
mutual_entropy_threshold =1e-4
neighbor_entropy_threshold = 0.8
cpu_num = mp.cpu_count()
proccess_num = cpu_num - 1 if cpu_num > 3 else cpu_num

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


def count_mutual_entropy(dict_, approcimate_total_word_num):
    def word_probability(word):
        # assert(word_len_statistic), 'word:{} frequency:{} len_statistic:{}'.format(word, dict_[word], word_len_statistic)
        return (dict_[word] + 1) / approcimate_total_word_num

    MI_dict = {}
    for k, v in dict_.items():
        if v > count_threshold and len(k) > 1:
            marginal_probability = [word_probability(
                k[:index]) * word_probability(k[index:]) for index in range(1, len(k))]
            marginal_probability = list(
                filter(lambda x: x > 0, marginal_probability))
            # print(marginal_probability)
            # for index in range(1, len(k)):
            #     mulply = word_probability(k[:index], each_gram_num) * word_probability(k[index:], each_gram_num)
            #     print(k[:index], k[index:], mulply)
            if marginal_probability:
                min_marginal_probability = min(marginal_probability)
                join_probability = word_probability(k)
                '''mutual entropy'''
                mutual_entropy = sum(map(
                    lambda x: join_probability * math.log(join_probability / x), marginal_probability))

                if mutual_entropy > mutual_entropy_threshold:
                    MI_dict[k] = mutual_entropy
                # print('{} {:.4f}'.format(k, mutual_entropy))
    print('len MI:{}'.format(len(MI_dict.keys())))
    return MI_dict


def count_neighbor_entropy(*argc):
    key, mapping_list = argc

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
    return (key, (min(left_entropy, right_entropy)))

def run_batch(batch_dict):
    assert(isinstance(batch_dict, dict))
    curerent_process = mp.current_process().name
    result_dict = {}
    print('process: {}, batch_size: {}'.format(
        curerent_process, len(batch_dict.keys())))
    for key, mapping_list in batch_dict.items():
        k, free_degree = count_neighbor_entropy(key, mapping_list)
        result_dict[k] = free_degree
    return result_dict

def calculate_free_degree(string_list, dict_):
    def key_mappping():  # find string containing key could reduce computation
        for key in dict_.keys():
            mapping_list=[]
            for string in string_list:
                if string.find(key) > 0:
                    mapping_list.append(string)
            yield key, mapping_list

    def get_batch(batch_size, input_data):
        '''
        @input_data: a generator
        '''
        ele_dict = defaultdict(list)
        for ele in input_data:
            key, mapping_list = ele
            ele_dict[key] = mapping_list
            if len(ele_dict.keys()) >= batch_size:
                yield ele_dict
                ele_dict = defaultdict(list)
        yield ele_dict

    def multi_core(mapping_dict_gen):
        print('multi_core mode, proccess_num {}'.format(proccess_num))
        pool = mp.Pool(processes=proccess_num)
        total_computation = len(dict_.keys())
        batch_size = total_computation // proccess_num
        print('total_computation: {}, batch size: {}'.format(
            total_computation, batch_size))
        multi_result = []
        for batch_dict in get_batch(batch_size, mapping_dict_gen):
            assert(isinstance(batch_dict, dict))
            multi_result.append(pool.apply_async(
                run_batch, args=(batch_dict, )))
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
    
    # multi_result = [pool.apply_async(calculate_free_degree, args=(*(key, mapping_list), )) for key, mapping_list in mapping_dict_gen]
    # match_list = []
    # for string in mapping_list:
    #     # match one word left and right
    #     match = re.findall(r'(.){}(.)'.format(key), string)
    #     for m in match:
    #         match_list.append(m)
    # left_entropy = entropy([m[0] for m in match_list])
    # right_entropy = entropy([m[1] for m in match_list])
    # entropy_dict[key] = int(min(left_entropy, right_entropy))
    # print(key, min(left_entropy, right_entropy))
    # pool.close()
    # pool.join()
    # for result in multi_result:
    #     k, v = result.get()
    #     entropy_dict[k] = v
    print('len free degree', len(entropy_dict.keys()))
    return entropy_dict

def find_frequency_pattern():
    string_list = read_data()
    approcimate_total_word_num = approcimate_total_world_num(string_list)
    print('total world len', approcimate_total_word_num)
    distict_substring_list_gen = get_all_distinct_substring(
        string_list, max_n_gram)
    pattern_dict = count_pattern_frequency(
    distict_substring_list_gen)
    MI_dict = count_mutual_entropy(pattern_dict, approcimate_total_word_num)
    sort_entropy = sorted(MI_dict.items(),
                          key=lambda x: x[1], reverse=True)
    write_data(os.path.join('./usr', 'word_mutual_entropy.txt'),
               ('\t'.join([key, str(ent)]) for key, ent in list(sort_entropy)))
    entropy_dict = calculate_free_degree(string_list, MI_dict)
    sort_entropy = sorted(entropy_dict.items(), key=lambda x: x[1], reverse=True)
    write_data(os.path.join('./usr', 'word_entropy.txt'),
                ('\t'.join([key, str(ent)]) for key, ent in list(sort_entropy)))

if __name__ == '__main__':
    find_frequency_pattern()
