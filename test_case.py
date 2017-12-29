#-*-coding:utf-8 -*-
from Tries import *
import find_frequency_pattern as ffp
import help_func as hf
import re
import math
import os
import jieba
import sys
from collections import defaultdict
import json
sys.path.append('../segmentation')
# from seg import ChineseSegment


def test_pruning_tries():
	pattern_dict = ffp.read_frequency_pattern()
	sentence = '迷你桌球迷你台球游戏'
	tries = ffp.build_tries_by_sentence(pattern_dict, sentence)
	distict_substring = ffp.get_distinct_substring(sentence)
	longest_sentence = ffp.get_longest_sentence(distict_substring)

	# for l_s in longest_sentence:
	# 	subpre_sentence_key_fre_pair = find_all_prefix_sentence(tries, l_s)
	# 	print(subpre_sentence_key_fre_pair)

	for l_s in longest_sentence:
		subpre_sentence_key_fre_pair = find_all_prefix_sentence(tries, l_s)
		ffp.empty_nodes_by_pefix(tries, subpre_sentence_key_fre_pair)

	for l_s in longest_sentence:
		suffix_key_fre_pair = find_all_suffix_sentence(tries, l_s)

		ffp.empty_node_by_suffix(tries, suffix_key_fre_pair)

	for l_s in longest_sentence:
		subpre_sentence_key_fre_pair = find_all_prefix_sentence(tries, l_s)
		print(subpre_sentence_key_fre_pair)


def add_reference():
	def read_reference_file():
		with open('source.txt', 'r') as rf:
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

	def read_product_name():
		with open('product_name.txt', 'r',) as rf:
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

	def write_reference(product_reference_list):
		with open('product_reference.txt', 'w') as wf:
			for product_reference in product_reference_list:
				key, fre, reference = product_reference
				wf.write('{}\t{}\t{}\n'.format(key, fre, reference))

	reference_list = read_reference_file()
	product_list = read_product_name()
	product_list_len = len(product_list)
	product_reference_list = []

	for index, product in enumerate(product_list):
		key, fre = product.split('\t')
		reference = find_reference(reference_list, key)
		product_reference_list.append((key, fre, reference))
		if index % 250 == 0:
			print('{}/{}'.format(index, product_list_len))
	print('{}/{}'.format(index, product_list_len))
	product_reference_list = sorted(product_reference_list, reverse=False)
	write_reference(product_reference_list)


def split_file():
	with open('product_reference.txt', 'r',) as rf:
		batch_size = 3
		total = rf.readlines()
		total_len = len(total)
		split_len = math.ceil(total_len / batch_size)

	for index in range(batch_size):
		split_line = total[index * split_len: (index + 1) * split_len]

		with open('product_name_' + str(index + 1) + '.txt', 'w') as wf:
			for line in split_line:
				wf.write(line)


def combine_and_seperate():
	def write_file(file_path, file):
		with open(file_path, 'w') as wf:
			for line in file:
				wf.write('{}\n'.format(line))

	file_dir = './usr'
	list_file = os.listdir(file_dir)
	list_file = [file for file in list_file if file.endswith('_P.txt')]
	list_file = list(filter(lambda x: not x.startswith('.'), list_file))
	product_list = []
	word_list = []
	'''read file from list file'''
	for file in list_file:
		with open(os.path.join(file_dir, file), 'r') as rf:
			for line in rf.readlines():
				line = line.strip()
				line = line.split('\t')
				if len(line) == 4:  # contain P tag
					product_list.append(line[0])
					word_list.append('{}\t{}'.format(line[0], line[1]))
				if len(line) == 3:
					word_list.append('{}\t{}'.format(line[0], line[1]))

	print(len(product_list), len(word_list))
	'''store word list'''
	write_file(os.path.join(file_dir, 'word.txt'), word_list)
	write_file(os.path.join(file_dir, 'product.txt'), product_list)


def delete_word_from_file():
	delete_word_list = hf.read_data(os.path.join('./usr', 'delete_product.txt'))
	word_fre_pair = hf.read_word_fre(os.path.join('./usr', 'word.txt'))
	print('before delete word len', len(word_fre_pair))
	word_fre_pair = [(w, fre) for w, fre in word_fre_pair if w not in delete_word_list]
	print('after delete word len', len(word_fre_pair))
	hf.write_data(os.path.join('./usr', 'word_.txt'), ('{}\t{}'.format(w, fre) for w, fre in word_fre_pair))


def word_decompose():
	# def build_model():
	# 	'''use neural network'''
	# 	dir_path = '../segmentation/'
	# 	frozen_graph_filename = os.path.join(dir_path, 'models/seg_model_140.pbtxt')
	# 	vocab_path = os.path.join(dir_path, 'dictionary/basic_vocab.txt')
	# 	user_dict_path = os.path.join('./usr', 'word_two_three.txt')
	# 	seg = ChineseSegment(frozen_graph_filename, vocab_path, user_dict_path)

	# 	return seg
	source_file = os.path.join('./usr', 'word_.txt')
	word_fre_pair = hf.read_word_fre(source_file)
	word_list = [w for w, fre in word_fre_pair]
	two_three_len_word_list = [w for w in word_list if len(w) in [2, 3]]
	hf.write_data(os.path.join('./usr', 'word_two_three.txt'), ('{}\t{}'.format(w, int(1000)) for w in two_three_len_word_list))

	# seg = build_model()
	# result = seg.segment(word_list)
	# for ele in result:
	# 	print(ele)

	print(len(two_three_len_word_list), len(word_list))
	'''add word into jieba'''
	for word in two_three_len_word_list:
		jieba.add_word(word)

	result_set = set()
	for word in word_list:
		w = jieba.cut(word)
		for ele in w:
			result_set.add(ele)
	hf.write_data(os.path.join('./usr', 'short_word.txt'), result_set)


def word_mapping():
	def write_jsonfile(data):
		target_file = os.path.join('./usr', 'product_title_map.json')
		with open(target_file, mode='w', encoding='utf8') as wf:
			json.dump(data, wf, ensure_ascii=False, indent=4, sort_keys=True)

	product_file = os.path.join('./usr', 'product.txt')
	source_file = os.path.join('./usr', 'source.txt')

	product_title = hf.read_data(source_file)
	products = hf.read_data(product_file)
	product_title_map_dict = defaultdict(list)

	for product in products:
		count = 0
		for title in product_title:
			if title.find(product) >= 0:
				product_title_map_dict[product].append(title)
				count += 1
		print('{}: {}'.format(product, count))
	write_jsonfile(product_title_map_dict)





if __name__ == '__main__':
	# test_pruning_tries()
	# split_file()
	# add_reference()
	# combine_and_seperate()
	# delete_word_from_file()
	# word_decompose()
	word_mapping()
