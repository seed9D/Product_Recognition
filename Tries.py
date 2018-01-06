
class Trie_node:
	'''
	A suffix Trie of all suffixes Node
	'''
	def __init__(self):
		self.child = {}
		self.string = None
		self.count = 0


class Tries:
	def __init__(self):
		self.root = Trie_node()

	def push_node(self, sentence, frequency=0):
		sentence_len = len(sentence)
		if sentence_len == 0:
			return

		temp = self.root
		for index, word in enumerate(sentence):
			# print(word)
			if word not in temp.child:
				temp.child[word] = Trie_node()
			temp = temp.child[word]
			if index + 1 == sentence_len:
				temp.count = frequency

	def search(self, sentence=None):
		'''
		return: Trie_node's count
		'''
		if sentence:
			temp = self.root
			match_word = []
			for index, word in enumerate(sentence):
				if word in temp.child:
					# print(temp.child)
					match_word.append(word)
					temp = temp.child[word]
				else:
					# print('no match')
					return (None, None)
			match_word = ''.join(match_word)
			# print(match_word, temp.count)
			return (match_word, temp)
		else:
			return (None, None)

	def _travel(self, trie_node):
		key_list = []
		if trie_node:
			for pre_k, node in trie_node.child.items():
				# print(pre_k)
				temp_list = self._travel(node)
				key_list.append(pre_k)
				if temp_list:
					for k in temp_list:
						key_list.append(pre_k + k)

		return key_list

	def travel(self):
		key_list = self._travel(self.root)
		# print(len(key_list))
		# for key in key_list:
		# 	print(key)
		return key_list

	def search_word_by_prefix(self, prefix):
		_, temp_node = self.search(prefix)
		word_list = self._travel(temp_node)
		word_list = [prefix + word for word in word_list]
		return word_list

	def delete_by_prefix(self, prefix):
		print(prefix)
		_, pre_node = self.search(prefix)
		if pre_node:
			pre_node.child = {}

	def search_all_prefix_by_sentence(self, sentence):
		prefix_sentence_list = []
		for index in range(len(sentence)):
			st, trie_node = self.search(sentence[:index + 1])
			if st:
				prefix_sentence_list.append((st, trie_node))

		return prefix_sentence_list


class Suffix_Trees:
	def __init__(self, string):
		assert isinstance(string, str) and len(string) > 0
		self.root = Trie_node()
		self.build_Trees(string)

	def build_Trees(self, string):
		for i in range(len(string)):
			substring = string[i:]
			self.insertsuffix(substring)

	def insertsuffix(self, string):
		assert isinstance(string, str) and len(string) > 0
		temp = self.root
		for index, char in enumerate(string):
			if char not in temp.child:
				temp.child[char] = Trie_node()
				temp.child[char].string = string[:index + 1]
			temp = temp.child[char]

	def __countNodesInTree(self, Trienode):
		if Trienode:
			count = 0
			temp = Trienode
			for k, v in temp.child.items():
				count += self.__countNodesInTree(v)
		else:
			return 0
		return 1 + count  # 1: itself

	def countNodesInTree(self):
		return self.__countNodesInTree(self.root)

	def __total_distict_substring(self, Trienode, substing_list):
		if Trienode:
			temp = Trienode
			for k, v in temp.child.items():
				substing_list.append(v.string)
				self.__total_distict_substring(v, substing_list)

	def total_distict_substring(self):
		substing_list = []
		self.__total_distict_substring(self.root, substing_list)
		return substing_list


def build_tries_by_sentence(sentence):
	assert isinstance(sentence, str)
	if not isinstance(sentence, str) and len(sentence) > 0:
		return None

	tries = Tries()
	sf = Suffix_Trees(sentence)
	distict_substring = sf.total_distict_substring()
	for substring in distict_substring:
		tries.push_node(substring,)
	return tries


def find_nodes_by_list(tries, key_list):
	assert isinstance(tries, Tries)
	assert isinstance(key_list, list) and len(key_list) > 0
	return_list = []
	for key in key_list:
		word, node = tries.search(key)
		if node:
			assert(word == key)
			return_list.append((key, node.count))
	return return_list


def build_tries_by_dict(dict_):
	assert isinstance(dict_, dict) and len(dict_.keys()) > 0
	tries = Tries()
	for k, v in dict_.items():
		tries.push_node(k, v)
	return tries


def find_all_prefix_sentence(tries, sentence):
	assert isinstance(tries, Tries)
	assert isinstance(sentence, str) and len(sentence) > 0, 'sentence:{}'.format(sentence)
	prefix_node_list = tries.search_all_prefix_by_sentence(sentence)
	key_fre_pair = []
	for pre_sentence, node in prefix_node_list:
		key_fre_pair.append((pre_sentence, int(node.count)))
	return key_fre_pair


def find_all_suffix_sentence(tries, sentence):
	assert isinstance(tries, Tries)
	assert isinstance(sentence, str) and len(sentence) > 0, 'sentence:{}'.format(sentence)
	suffix_string_list = []
	key_fre_pair = []
	for index in range(len(sentence)):
		suffix_string_list.append(sentence[index:])
	# suffix_string_list = suffix_string_list[::-1]

	for suffix_string in suffix_string_list:
		match_word, node = tries.search(sentence=suffix_string)
		if node:
			assert(match_word == suffix_string)
			key_fre_pair.append((match_word, int(node.count)))

	return key_fre_pair




