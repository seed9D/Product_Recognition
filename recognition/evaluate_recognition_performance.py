import sys
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

def load_file(file_path):
	with open(file_path, 'r') as rf:
		output = []
		for line in rf.readlines():
			line = line.strip()
			line = line.split('\t')
			one_line = []
			for l in line:
				word, tag = l.split('/')
				one_line.append((word, tag))
			output.append(one_line)
	return output


def load_tag_2_index(tag_index_path):
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


def evaluate_performance(true_seq, pre_seq, tag_dict):
	tag_label = list(tag_dict.keys())
	# print(tag_label)
	report = classification_report(true_seq, pre_seq, target_names=tag_label)
	print(report)


def get_sequence_array(true_list, result_list, tag_vob):
	true_sequence = []
	result_sequence = []
	for true_one_line, result_one_line in zip(true_list, result_list):
		word_slince = 0
		tag_slice = 1
		# true_temp = []
		# result_temp = []
		for true_token, result_token in zip(true_one_line, result_one_line):
			if true_token[word_slince] == result_token[word_slince]:
				# true_temp.append(int(tag_vob[true_token[tag_slice]]))
				# result_temp.append(int(tag_vob[result_token[tag_slice]]))
				# true_temp.append(true_token[tag_slice])
				# result_temp.append(result_token[tag_slice])
				true_sequence.append(true_token[tag_slice])
				result_sequence.append(result_token[tag_slice])
			else:
				print(true_token, result_token)

		# true_sequence.append(true_temp)
		# result_sequence.append(result_temp)
	assert(len(true_sequence) == len(result_sequence))
	return true_sequence, result_sequence


def main(argc, argv):
	if argc < 4:
		print("Usage:%s <true file path> <recognition result path> <tag index path>" % (argv[0]))
		sys.exit(1)
	true_file = argv[1]
	recognition_result_path = argv[2]
	tag_index_path = argv[3]
	true_list = load_file(true_file)[-20000:]
	result_list = load_file(recognition_result_path)
	tag_dict = load_tag_2_index(tag_index_path)
	print(len(true_list), len(result_list))
	true_seq, result_seq = get_sequence_array(true_list, result_list, tag_dict)

	evaluate_performance(true_seq, result_seq, tag_dict)

if __name__ == '__main__':
	main(len(sys.argv), sys.argv)