import sys
import os
from product_reconization import Product_Recognition
from help_func import write_data

def load_model():
	frozen_graph_filename = './model/product_model.pbtxt'
	char_index_path = './model/char_vec_index.txt'
	word_index_path = './model/word_vec_index.txt'
	tag_index_path = './model/tag_vocab.txt'
	return Product_Recognition(frozen_graph_filename, char_index_path, word_index_path, tag_index_path)


def run_product_recognition(test_file):
	product_recognition = load_model()
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


def find_new_product(result_list):
	new_product_set = set()
	for one_line in result_list:
		temp_list = []
		for token in one_line:
			word, tag = token
			if tag is 'S':
				new_product_set.add(word)
			elif tag is 'B':
				temp_list.append(word)
			elif tag is 'I':
				temp_list.append(word)
			elif tag is 'E':
				temp_list.append(word)
				new_product_set.add(''.join(temp_list))
				temp_list = []
				continue
	print('find {} new product'.format(len(new_product_set)))
	for ele in new_product_set:
		print(ele, end=' ')
	print()
	return new_product_set


def main(argc, argv):
	if argc < 3:
		print("Usage:%s <test file> <recognition_result>" % (argv[0]))
		sys.exit(1)
	input_file = argv[1]
	recognition_result_path = argv[2]
	input_list = load_unrecongnization_file(input_file)
	result_list = run_product_recognition(input_list)
	print('input:{} output:{}'.format(len(input_list), len(result_list)))
	new_product_set = find_new_product(result_list)

	write_data('./test_dir/new_product.txt', new_product_set)
	write_recongnization_result(recognition_result_path, result_list)


if __name__ == '__main__':
	main(len(sys.argv), sys.argv)
