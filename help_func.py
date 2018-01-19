import logging
import os

def check_dir_exist(path):
	if not os.path.exists(path):
		os.makedirs(path)
		print('makdir {}'.format(path))

def create_log():
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(levelname)s:[%(filename)s %(funcName)s:%(lineno)d] %(message)s')
	console.setFormatter(formatter)
	logger.addHandler(console)
	return logger


def read_data(path):
	with open(path, 'r') as rf:
		def dedupe(items):
			seen = set()
			for item in items:
				if item not in seen:
					yield item
					seen.add(item)
		string_list = []
		readlines = dedupe(rf.readlines())
		for line in readlines:
			line = line.strip()
			string_list.append(line)
		return string_list


def read_word_fre(path):
	string_list = read_data(path)
	word_fre_pair = []
	for string in string_list:
		string_split = string.split('\t')
		word_fre_pair.append((string_split[0], string_split[1]))

	return word_fre_pair


def write_data(path, list_iter):
	with open(path, 'w') as wf:
		for ele in list_iter:
			if ele:
				wf.write('{}\n'.format(ele))
