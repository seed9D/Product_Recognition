import jieba
import os
import sys
import re
import argparse
from Tag import Token, Tag_BIESO, token2String, write_tag2file, token2String_word_only
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import help_func as hf
sub_dir = 'training_model'

def segment_product(product_list, base_word_list):
	for word in base_word_list:
		jieba.add_word(word)
	product_dict = {}
	for product in product_list:
		# print('{}:'.format(product), end=' ')
		cut = jieba.cut(product, HMM=False)
		product_dict[product] = [ele for ele in cut]
	# for k, v in product_dict.items():
	# 	print(k, v)
	return product_dict


def segment_source(string_list, word_list):
	def segement(string_list):
		for line in string_list:
			# line = line.replace(' ', '')
			split_line = re.split(r'[：；\-\+\(\)\\|，,《》（）【】/、&\s]', line)
			cut_result = [jieba.cut(line) for line in split_line]
			result = [' '.join(cut) for cut in cut_result]
			result = ' '.join(result)
			# for ele in result:
			yield result

	for word in word_list:
		jieba.add_word(word, freq=100)
	# temp = jieba.cut('滑梯质量最好')
	# print(' '.join(temp))
	sentence_one_line = segement(string_list)
	return sentence_one_line


def tag_source(source_list, product_list, word_list):
	def filter_token_list(token_list):
		token_num = len(token_list)
		BIES_tag_num = 0
		if token_num > 0:
			for token in token_list:
				if token.tags in ['B', 'I', 'E', 'S']:
					BIES_tag_num += 1
		if BIES_tag_num > 0:
			return True
		return False

	def find_product(candidate_list, product_dict, cur_index):
		add_candidate = ''
		product_list = []
		break_inedx = 0
		for index, candidate in enumerate(candidate_list):
			add_candidate += candidate
			if add_candidate in product_dict:
				product_list = product_dict[add_candidate]
				break_inedx = index

		break_inedx += cur_index
		return break_inedx, product_list

	def procces_product_token(token_list, product_list):
		if len(product_list) == 1:
			token_list.append(Token(product_list[0], Tag_BIESO.S.name))
		else:
			nn = len(product_list)
			for i in range(nn):
				word = product_list[i]
				if i == 0:
					token_list.append(Token(word, Tag_BIESO.B.name))
				elif i == (nn - 1):
					token_list.append(Token(word, Tag_BIESO.E.name))
				else:
					token_list.append(Token(word, Tag_BIESO.I.name))

	def proccess_line(sentence, product_dict):
		split_sentence = sentence.split(' ')
		split_len = len(split_sentence)
		index = 0
		token_list = []
		while index != split_len:
			break_inedx, product_list = find_product(split_sentence[index:], product_dict, index)
			if product_list:
				procces_product_token(token_list, product_list)
			else:
				if split_sentence[index]:
					token_list.append(Token(split_sentence[index], Tag_BIESO.O.name))

			index = break_inedx + 1

			# if split_sentence[index] not in product_dict:
			# 	token_list.append(Token(split_sentence[index], Tag_BIESO.O.name))
			# 	index += 1
			# else:
			# 	break_inedx, product_list = find_product(split_sentence[index:], product_dict, index)
			# 	procces_product_token(token_list, product_list)
			# 	index = break_inedx

		return token_list

	product_dict = segment_product(product_list, word_list)
	sentences = segment_source(source_list, word_list)

	postive_list = []
	negative_list = []
	segement_list = []
	for sentence in sentences:
		token_list = proccess_line(sentence, product_dict)
		if filter_token_list(token_list):
			postive_list.append(token2String(token_list))
		else:
			negative_list.append(token2String_word_only(token_list))
		segement_list.append(token2String_word_only(token_list, separator=' '))

	print('tag successful len:{}; tag failed len:{}'.format(len(postive_list), len(negative_list)))
	return postive_list, negative_list, segement_list
	# string_one_line = (proccess_line(sentence, product_dict) for sentence in sentences)
	# hf.write_data(os.path.join(data_dir, 'source_tag.txt'), string_one_line)

def start_tag(source_file_p, product_file_p, base_word_file_p, output_dir):

	product_list = hf.read_data(product_file_p)
	word_list = hf.read_data(base_word_file_p)
	source_list = hf.read_data(source_file_p)
	print('product_list len:{}'.format(len(product_list)))
	print('word_list len:{}'.format(len(word_list)))
	print('source_list(wait to be tagged) len:{}'.format(len(source_list)))
	# sentences = segment_source(string_list, word_list)
	# hf.write_data(os.path.join(data_dir, 'source_segement.txt'), sentences)

	postive_list, negative_list, segement_list = tag_source(
		source_list, product_list, word_list)

	hf.write_data(os.path.join(output_dir, 'source_tag.txt'), postive_list)
	hf.write_data(os.path.join(output_dir, 'source_tag_negative.txt'), negative_list)
	hf.write_data(os.path.join(output_dir, 'source_segement.txt'), segement_list)
	write_tag2file(Tag_BIESO, os.path.join(output_dir, 'tag_vocab.txt'))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('source_file',
                     	help='the file you want to tag with product',
                     	action='store',
                    	)
	parser.add_argument('product_file',
                        help='the file contain product name',
                        action='store',
                        )
	parser.add_argument('base_word_file',
                     	help='the file contain base word',
                     	action='store',
                    	)
	
	parser.add_argument('--user_dir',
                        help='user dir path',
                        action='store',
                        dest='user_dir',
                        default=os.path.join(root_dir, 'usr'))

	args = parser.parse_args()
	output_dir = os.path.join(args.user_dir, sub_dir)
	hf.check_dir_exist(output_dir)
	# output_tagged_file_path = os.path.join(output_dir, 'source_tag.txt')
	start_tag(args.source_file, args.product_file, args.base_word_file, output_dir)



if __name__ == '__main__':
	main()
