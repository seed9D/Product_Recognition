#!/usr/bin/python3
#-*-coding:utf-8 -*-

import re
import sys
import operator
from Tries import *


def read_data():
	with open('source.txt', 'r') as rf:
		string_list = []
		for line in rf.readlines():
			line = line.strip()
			# split_line = re.split(r'[（）\[\]【】《》\(\).\\、|，,\/\s-]', line)
			split_line = re.split(r'[+\(\)\\|，,《》（）【】/、&\s]', line)

			# print(split_line)
			split_line = list(filter(None, split_line))
			split_line = list(filter(lambda x: not x.isdigit(), split_line))
			string_list.extend(split_line)
		return set(string_list)


def write_data(_dict, file_name):
	print('dict len:{}'.format(len(_dict.keys())))
	with open(file_name, 'w') as wf:
		sorted_ = sorted(_dict.items(), key=operator.itemgetter(1), reverse=True)
		for k, v in sorted_:
			wf.write('{}\t{}\n'.format(k, v))
		# for k, v in pattern_dict.items():
		# 	wf.write('{}\t{}\n'.format(k, v))


def read_frequency_pattern():
	pattern_dict = {}
	with open('frequency_pattern.txt', mode='r') as rf:
		for line in rf.readlines():
			line = line.strip()
			key, value = line.split('\t')
			pattern_dict[key] = value

	return pattern_dict


def get_distinct_substring(sentence):
	sf = Suffix_Trees(sentence)
	return sf.total_distict_substring()


def build_tries_by_sentence(pattern_dict, sentence):
	'''
	for test
	'''
	tries = Tries()
	sf = Suffix_Trees(sentence)
	distict_substring = sf.total_distict_substring()
	for substring in distict_substring:
		if substring in pattern_dict:
			fre = pattern_dict[substring]
			tries.push_node(substring, fre)

	# diff = [substring for substring in distict_substring if substring not in key_list]
	# key_list = sorted(key_list, key=lambda x: len(x), reverse=True)

	return tries


def get_longest_sentence(substring_list):
	assert len(substring_list) > 0 and isinstance(substring_list, list)
	substring_len_list = [len(substring) for substring in substring_list]
	longest_index = [index for index, sl in enumerate(substring_len_list[1:]) if substring_len_list[index + 1] < substring_len_list[index]]
	longest_index.append(len(substring_len_list) - 1)  # append the last one
	longest_sentence = [substring_list[index] for index in longest_index]

	return longest_sentence


def empty_nodes_by_pefix(tries, key_fre_pair):
	'''
	the length of key are ordered in ASC
	'''
	def set_node_count(tries, key):
		assert isinstance(key, str)
		match_word, node = tries.search(key)
		assert(match_word == key)
		if node:
			node.count = 0

	if not key_fre_pair:
		return

	for index, (current_key, current_fre) in enumerate(key_fre_pair):
		next_key, next_fre = key_fre_pair[index + 1]
		if abs(current_fre - next_fre) < current_fre * 0.1:  # similar
			set_node_count(tries, current_key)  # empty the key which is the shorter one

		elif current_fre > next_fre and abs(current_fre - next_fre) > 0.4 * next_fre:
			set_node_count(tries, next_key)

		if index + 2 == len(key_fre_pair):
			break
	# print(key_fre_pair)
	# print('')


def empty_node_by_suffix(tries, key_fre_pair):
	'''
	the length of key are ordered in DESC
	'''
	def set_node_count(tries, key):
		match_word, node = tries.search(key)
		assert(match_word == key)
		if node:
			node.count = 0
	if not key_fre_pair:
		return
	# print(key_fre_pair)
	pre_fre = key_fre_pair[0][1]  # first key's frequency
	for index, (key, fre) in enumerate(key_fre_pair):
		if index == 0:
			continue
		if abs(pre_fre - fre) < fre * 0.1:
			set_node_count(tries, key)

		elif abs(pre_fre - fre) * 0.4 > pre_fre:
			previous_key, previous_fre = key_fre_pair[index - 1]
			set_node_count(tries, previous_key)
		pre_fre = fre


def filter_frequency_pattern():
	def filter_dict(_dict):
		if not isinstance(_dict, dict):
			return {}
		return_dict = {}
		for k, v in _dict.items():
			match = re.search('[a-zA-Z0-9]', k)  # key contain number or alphabet
			if match:
				continue
			if v == 0:
				continue
			return_dict[k] = int(v)
		return return_dict

	def print_prefix_sentence_fre(tries, sentence=None):
		key_fre_list = find_all_prefix_sentence(tries, sentence)
		print(key_fre_list)
	

	def print_suffix_sentence_fre(tries, sentence=None):
		key_fre_list = find_all_suffix_sentence(tries, sentence)
		print(key_fre_list)

	pattern_dict = read_frequency_pattern()
	# print(pattern_dict['胶套'])
	# print('pattern_dict length:', len(pattern_dict.keys()))
	tries = build_tries_by_dict(pattern_dict)
	key_list = tries.travel()
	longest_sentence_list = get_longest_sentence(key_list)
	test_sentence = '游乐设备充'
	test_sentence = '厂家定做'
	print_prefix_sentence_fre(tries, test_sentence)
	'''step 1'''
	for longest_sentence in longest_sentence_list:
		subpre_sentence_key_fre_pair = find_all_prefix_sentence(tries, longest_sentence)
		# print(subpre_sentence_key_fre_pair)
		empty_nodes_by_pefix(tries, subpre_sentence_key_fre_pair)
		# subpre_sentence_key_fre_pair = find_all_prefix_sentence(tries, longest_sentence)
		# print(subpre_sentence_key_fre_pair)
		# print('')

	print_prefix_sentence_fre(tries, test_sentence)
	print_suffix_sentence_fre(tries, test_sentence)
	'''step 2'''
	for longest_sentence in longest_sentence_list:
		suffix_key_fre_pair = find_all_suffix_sentence(tries, longest_sentence)

		empty_node_by_suffix(tries, suffix_key_fre_pair)

	print_suffix_sentence_fre(tries, test_sentence)


	'''tries to dict'''
	result_dict = {}
	key_fre_pair = find_nodes_by_list(tries, key_list)
	for key, fre in key_fre_pair:
		result_dict[key] = int(fre)
	result_dict = filter_dict(result_dict)
	print('胶套:', result_dict['胶套'])
	write_data(result_dict, 'product_name.txt')


def find_frequency_pattern():
	batch_size = 40  # batch how many string in string list
	threshold = 5  # the threshold for filtering the pattern frequency
	clean_interval = 1000  # how often to clean patten frequency under threshold
	# clean_size = 10000

	def get_all_distinct_substring(string_list):
		assert len(string_list) > 0
		string_list_len = len(string_list)
		print('total string list len:{}'.format(string_list_len))
		distict_substring_list = []
		for i in range(string_list_len):
			distict_substring = get_distinct_substring(string_list[i])
			distict_substring = list(filter(None, distict_substring))
			distict_substring = list(filter(lambda x: len(x) > 1, distict_substring))
			distict_substring = list(filter(lambda x: not x.isdigit(), distict_substring))
			distict_substring_list.extend(distict_substring)
			if i % batch_size == 0 and i is not 0:
				yield distict_substring_list
				distict_substring_list = []
		yield distict_substring_list

	def clean_under_threshold(pattern_dict, threshold):
		# print('len of dictionary {}'.format(len(pattern_dict.keys())))
		pattern_dict = dict((k, v) for k, v in pattern_dict.items() if v > threshold)
		return pattern_dict

	def count_pattern_frequency(pattern_dict, distict_substring_list_gen):
		for index, distict_substring_list in enumerate(distict_substring_list_gen):
			# print(len(distict_substring_list))
			for substring in distict_substring_list:
				pattern_dict.setdefault(substring, 0)
				pattern_dict[substring] += 1
			if index % clean_interval == 0 and index is not 0:
				print('index ', index)
				# if len(pattern_dict.keys()) > clean_size:
				pattern_dict = clean_under_threshold(pattern_dict, threshold)
				# if index % clean_interval == 0 and index is not 0:

		pattern_dict = clean_under_threshold(pattern_dict, 15)
		return pattern_dict

	pattern_dict = {}
	string_list = list(read_data())
	distict_substring_list_gen = get_all_distinct_substring(string_list)
	pattern_dict = count_pattern_frequency(pattern_dict, distict_substring_list_gen)
	write_data(pattern_dict, 'frequency_pattern.txt')


if __name__ == '__main__':
	# find_frequency_pattern()
	filter_frequency_pattern()


	# string_list = read_data()

	# st = STree(string_list[:2])
	# print(st.lcs())

	# string = 'ababa'
	# tree = Suffix_Trees(string)
	# print(tree.countNodesInTree())
	# substing_list = tree.total_distict_substring()
	# print(substing_list)