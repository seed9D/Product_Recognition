from enum import Enum


class Token:
	def __init__(self, words, tag):
		self.words = words
		self.tags = tag


class Tag_BIESO(Enum):
	B = 0
	I = 1
	E = 2
	S = 3
	O = 4


def token2String(token_list, separator='\t'):
	assert(isinstance(token_list, list))
	list_temp = []
	for token in token_list:
		list_temp.append('/'.join([token.words, token.tags]))

	tokens_string = separator.join(list_temp)
	return tokens_string


def token2String_word_only(token_list, separator='\t'):
	assert(isinstance(token_list, list))
	list_temp = []
	for token in token_list:
		list_temp.append(token.words)
	tokens_string = separator.join(list_temp)
	return tokens_string


def write_tag2file(Tag_scheme, path):
	with open(path, 'w') as wf:
		taglist = []
		for tag_name, tag_member in Tag_scheme.__members__.items():
			# print(tag_name, tag_member, tag_member.value)
			taglist.append((tag_member.value, tag_name))
		for value, name in taglist:
			wf.write('{}\t{}\n'.format(name, value))


if __name__ == '__main__':
	write_tag2file(Tag_BIESO, './usr/tag_vocab.txt')
