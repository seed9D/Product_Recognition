# -*- coding: utf-8 -*-
# get each word or char's vector index in word_vec.txt and char.txt
# outfile contains vector index instead of word vector
import sys
import os
import w2v


class Token:
	def __init__(self, words, tag):
		self.words = words
		self.chars = []
		ustr = unicode(words.decode('utf8'))
		for c in ustr:
			self.chars.append(c)
		self.tag = tag


class Generate_train():
	def __init__(self, char_vob, word_vob, tag_vob):
		self.char_vob = char_vob
		self.word_vob = word_vob
		self.tag_vob = tag_vob
		self.MAX_LEN = 40
		self.MAX_CHAR_IN_WORD = 5
		self.total_line = 0
		self.long_line = 0

	def _generate_train_line(self, token_list):
		def split_long_token():
			index_list = []
			split_token_list = []
			for index, ele in enumerate(token_list):
				if ele.token in ['。', '！', '？']:
					index_list.append(index)
			for i, split_index in enumerate(index_list):
				if i == 0:
					split_tokens = self.tokens[:split_index + 1]
				else:
					split_tokens = self.tokens[index_list[i - 1]:split_index + 1]
				split_token_list.append(split_tokens)
			return split_token_list
		nl = len(token_list)
		split_token_list = []
		wordi = []
		chari = []
		labeli = []

		if nl < 3:  # todo
			return None
		if nl > self.MAX_LEN:
			split_token_list = split_long_token()
			# self.long_line += 1
		else:
			split_token_list.append(token_list)

		for tokens in split_token_list:
			nnl = len(tokens)
			nnl = self.MAX_LEN if nnl > self.MAX_LEN else nnl
			for token in tokens:
				idx = self.word_vob.GetWordIndex(token.words)
				wordi.append(str(idx))
				labeli.append(str(token.tag))

				nc = len(token.chars)
				if nc > self.MAX_CHAR_IN_WORD:
					token.chars[self.MAX_CHAR_IN_WORD - 1] = token.chars[nc - 1]
					nc = self.MAX_CHAR_IN_WORD

				for i in range(nc):
					idx = self.char_vob.GetWordIndex(str(token.chars[i].encode("utf8")))
					# if idx == 1:
					# 	print(token.chars[i])

					chari.append(str(idx))

				for i in range(nc, self.MAX_CHAR_IN_WORD):
					'''padding zero'''
					chari.append('0')
		for i in range(nl, self.MAX_LEN):
			wordi.append('0')
			labeli.append('0')
			for ii in range(self.MAX_CHAR_IN_WORD):
				chari.append(str('0'))

		line = ' '.join(wordi)
		line += ' '
		line += ' '.join(chari)
		line += ' '
		line += ' '.join(labeli)
		return line

	def process(self, corpusPath):
		self.total_line = 0
		self.long_line = 0
		with open(corpusPath, 'r') as fp:
			total = fp.readlines()
			self.total_line = len(total)
			processed_lines_gen = (self._processline(line.strip()) for line in total)

		return processed_lines_gen

	def _processline(self, line):
		token_list = []
		line = line.split('\t')
		for token in line:
			result = self._processToken(token, token_list)

		if result and len(token_list) > 0:
			string_line = self._generate_train_line(token_list)
		else:
			string_line = ''
		# self.total_line += 1
		return string_line

	def _processToken(self, token, token_list):
		split_token = token.split('/')
		assert(len(split_token) == 2)
		tag = split_token[1]
		word = split_token[0]

		if tag in self.tag_vob:
			word = word.strip()
			token_list.append(Token(word, self.tag_vob[tag]))
			return True
		else:
			return False


def loadtagVob(path):
	vob = {}
	with open(path, 'r') as rf:
		for line in rf.readlines():
			line = line.strip()
			if line:
				line = line.split('\t')
				assert(len(line) == 2)
				vob[line[0]] = line[1]

	return vob


def write_train_data(out_path, data_iter, total_line):
	test_out = open(os.path.join(out_path, 'train_for_test.txt'), 'w')
	train_out = open(os.path.join(out_path, 'train_for_train.txt'), 'w')
	for index, line in enumerate(data_iter):
		if not line:
			continue

		if index < (total_line * 8) // 10:
			train_out.write('{}\n'.format(line))

		else:
			test_out.write('{}\n'.format(line))


def main(argc, argv):
	if argc != 6:
		print('Usage:{} <vec_vob> <char_vob> <tag_vob> <corpus> <output>'.format(argv[0]))
		sys.exit(1)
	wvobPath = argv[1]
	cvobPath = argv[2]
	tagvobPath = argv[3]
	corpusPath = argv[4]
	outputPath = argv[5]
	'''load word2vector'''
	word_vob = w2v.Word2vecVocab()
	char_vob = w2v.Word2vecVocab()
	word_vob.Load(wvobPath)
	char_vob.Load(cvobPath)
	tag_vob = loadtagVob(tagvobPath)

	generate_train = Generate_train(char_vob, word_vob, tag_vob)
	processed_lines_gen = generate_train.process(corpusPath)
	print('total line:{}'.format(generate_train.total_line))
	write_train_data(outputPath, processed_lines_gen, generate_train.total_line)


if __name__ == '__main__':
	main(len(sys.argv), sys.argv)