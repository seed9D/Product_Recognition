import tensorflow as tf
import numpy as np
import re
import types
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import help_func as hf

logger = hf.create_log()

class Product_Recognition:
	def __init__(self, frozen_graph_filename, char_index_f, word_index_f, tag_index_f):
		self.seq_max_len = 40
		self.batch_size = 64
		self.max_chars_per_word = 5
		self.frozen_graph_filename = frozen_graph_filename
		self.graph = None
		self.user_dict = None
		self.transitions_matrix = None
		self.unary_score = None

		self.char_2_index = self.load_vector_2_index(char_index_f)
		self.word_2_index = self.load_vector_2_index(word_index_f)
		self.tag_2_index = self.load_tag_2_index(tag_index_f)

		self.load_graph()

	def load_graph(self):
		with tf.gfile.GFile(self.frozen_graph_filename, 'rb') as f:  # import a graph_def protobuf
			graph_def = tf.GraphDef()
			graph_def.ParseFromString(f.read())

		with tf.Graph().as_default() as graph:  # load graph_def into a actual graph
			tf.import_graph_def(graph_def, input_map=None, return_elements=None, name='prefix', op_dict=None, producer_op_list=None)
		self.graph = graph
		# for op in graph.get_operations():
		# 	print(op.name)
		self.sess = tf.Session(graph=self.graph)
		transitions_ = self.graph.get_tensor_by_name('prefix/transitions:0')  # tensor, transition matrix
		self.unary_score = self.graph.get_tensor_by_name('prefix/Reshape_9:0')  # tensor shape: (?, 100, 11) (?, max_sentance_size, tag_num), the word in a sentance's score of tags'
		# self.unary_score = self.graph.get_tensor_by_name('prefix/Reshape_7:0')
		self.w_input = self.graph.get_tensor_by_name('prefix/input_words:0')  # (none, 100)
		self.c_input = self.graph.get_tensor_by_name('prefix/input_chars:0')  # (none, 500)
		# print(self.w_input.get_shape().as_list(), self.c_input.get_shape().as_list())

		self.transitions_matrix = self.sess.run([transitions_])
		self.transitions_matrix = np.squeeze(np.array(self.transitions_matrix), axis=0)
		# print(self.transitions_matrix.shape)

		# writer = tf.summary.FileWriter("output", self.sess.graph)
		# writer.close()
	def load_tag_2_index(self, tag_index_path):
		with open(tag_index_path, 'r', errors='ignore') as f:
			to_index = {}
			for line in f.readlines():
				line = line.strip().split('\t')
				if len(line) != 2:
					continue
				[word, index] = line
				try:
					to_index[word] = int(index)
				except Exception:
					pass
			return to_index

	def load_vector_2_index(self, vec_index_path):
		with open(vec_index_path, 'r', errors='ignore') as f:
			to_index = {}
			for line in f.readlines():
				line = line.strip().split('\t')
				if len(line) != 2:
					continue
				[word, index] = line
				try:
					to_index[word] = int(index)
				except Exception as e:
					print(e)
			return to_index

	def get_word_char_inedx(self, content):
		char_vocab_index = []
		word_vocab_index = []
		for word in content:
			# print(word)
			if word in self.word_2_index:
				word_vocab_index.append(self.word_2_index[word])

			else:
				word_vocab_index.append(1)  # UNK

			char_list = [ch for ch in word]

			nc = len(char_list)
			if nc > self.max_chars_per_word:
				lc = char_list[nc - 1]
				char_list[self.max_chars_per_word - 1] = lc
				nc = self.max_chars_per_word
			for i in range(nc):
				if char_list[i] in self.char_2_index:
					char_index = self.char_2_index[char_list[i]]
					char_vocab_index.append(char_index)
				else:
					char_vocab_index.append(1)  # UNK
			for i in range(nc, self.max_chars_per_word):
				char_vocab_index.append(0)

		for i in range(len(content), self.seq_max_len):  # padding zero
			word_vocab_index.append(0)
			for j in range(self.max_chars_per_word):
				char_vocab_index.append(0)
		return char_vocab_index, word_vocab_index

	def _run_tagging(self, tagging_list):
		assert(isinstance(tagging_list, list))
		assert(len(tagging_list) > 0)

		def word2_index_as_array(content):
			assert(isinstance(content, list))
			char_vocab_index, word_vocab_index = self.get_word_char_inedx(content)
			return np.expand_dims(np.array(char_vocab_index), axis=0), np.expand_dims(np.array(word_vocab_index), axis=0)

		def get_index_array(tagging_list):
			word_index_array_list = []
			char_index_array_list = []
			for content in tagging_list:
				char_vocab_index_array, word_vocab_index_array = word2_index_as_array(content)
				# logger.debug(char_vocab_index_array.shape)
				assert(word_vocab_index_array.shape[1] == self.seq_max_len), word_vocab_index_array.shape
				word_index_array_list.append(word_vocab_index_array)
				char_index_array_list.append(char_vocab_index_array)
			word_index_array = np.concatenate(word_index_array_list, axis=0)
			char_index_array = np.concatenate(char_index_array_list, axis=0)

			assert(char_index_array.shape[1] == self.max_chars_per_word * self.seq_max_len), 'char_index_array shape{}'.format(char_index_array.shape)
			return char_index_array, word_index_array

		result_list = []
		char_index_array, word_index_array = get_index_array(tagging_list)
		seq_len_array = np.count_nonzero(word_index_array, axis=1)

		feed_input = {
			self.w_input: word_index_array,
			self.c_input: char_index_array}
		unary_score_val = self.sess.run(self.unary_score, feed_input)
		for unary_score_val_, segement_words, sequence_len in zip(unary_score_val, tagging_list, seq_len_array):
			assert(isinstance(segement_words, list))
			result = []
			unary_score_val_ = unary_score_val_[:sequence_len]
			tag_seq, _ = tf.contrib.crf.viterbi_decode(unary_score_val_, self.transitions_matrix)
			for tag_index, words in zip(tag_seq, segement_words):
				assert(isinstance(words, str)), words
				assert(tag_index in self.tag_2_index.values())
				tag_name = list(self.tag_2_index.keys())[list(self.tag_2_index.values()).index(tag_index)]
				result.append((words, tag_name))
			result_list.append(result)
		return result_list

	def run_recognition(self, contents):
		'''
		expect run this function after segmentation
		@content:
			a segment string list: ['自然', '語言', '處理']
			a list of segment string list: [['自然', '語言', '處理'], ['自然', '語言', '處理'], ['自然', '語言', '處理']]
		'''
		assert(isinstance(contents, list))

		def handle_input(content):
			content_list = []
			'''check the content type'''

			if isinstance(content[0], str):
				content_list.append(content)
			elif isinstance(content[0], list):
				content_list = content
			for index, ele in enumerate(content_list):
				if len(ele) > self.seq_max_len:
					delimiters = ['。', '！', '？', ',', '，', ';', '；']
					collection = []
					each_sentence = []
					for e in ele:
						if e:  # avoid empty element case
							collection.append(e)
						if e in delimiters:
							if collection:
								# if len(collection) > self.seq_max_len:
								# collection = collection[: self.seq_max_len]
								# assert(len(collection) <= self.seq_max_len), 'seq_len:{}'.format(len(collection))
								each_sentence.append(collection[: self.seq_max_len])
							collection = []
					# split_sentence = re.split(r'([。！？,，;；])', ele)
					# value = split_sentence[::2]
					# delimiters = split_sentence[1::2] + ['']
					# split_sentence_ = []
					# for v, deli in zip(value, delimiters):
					# 	split_sentence_.append(v + deli)
					# each_sentence = split_sentence_
					if collection:
						each_sentence.append(collection[:self.seq_max_len])
				else:
					each_sentence = [ele]
				yield each_sentence

		def tagging(content_iter):
			assert(isinstance(content_iter, types.GeneratorType)), content_iter
			tagged_result = []
			wait_for_tag = []

			def run_tagging_in_wait_for_tag(wait_for_tag):
				# global wait_for_tag
				# global tagged_result
				if wait_for_tag:
					one_batch_tagging_result = self._run_tagging(wait_for_tag)
					tagged_result.extend(one_batch_tagging_result)
				return []

			for index, ele in enumerate(content_iter):
				assert(isinstance(ele, list))
				'''get batch'''
				if len(ele) > 1:
					temp = []
					wait_for_tag = run_tagging_in_wait_for_tag(wait_for_tag)

					'''run long sentence'''
					long_sentence_tagging_result = self._run_tagging(ele)
					'''compose a tagged sentence'''
					for e in long_sentence_tagging_result:
						temp.extend(e)
					tagged_result.append(temp)

				else:
					'''collect batch'''
					wait_for_tag.extend(ele)

				if index % self.batch_size == 0 and index is not 0:
					wait_for_tag = run_tagging_in_wait_for_tag(wait_for_tag)

			wait_for_tag = run_tagging_in_wait_for_tag(wait_for_tag)
			return tagged_result

		content_generator = handle_input(contents)
		tagged_result = tagging(content_generator)
		return tagged_result

