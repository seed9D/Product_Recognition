import os
import sys
import argparse
import subprocess
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)
import help_func as hf
sub_dir = 'training_model'
kcws_dir = os.path.join(current_dir, 'kcws')


def set_up_kcws(char_vector_p,
                source_tag_p,
                source_seg_p,
                tag_scheme_f,
                output_dir):
    
    kcws_temp_dir = os.path.join(output_dir, 'kcws_temp')
    kcws_temp_dir = os.path.abspath(kcws_temp_dir)
    hf.check_dir_exist(kcws_temp_dir)
    path_dict = {}
    path_dict['kcws_temp_dir'] = kcws_temp_dir
    path_dict['char_vector_p'] = os.path.abspath(char_vector_p)
    path_dict['tag_scheme_f'] = os.path.abspath(tag_scheme_f)
    path_dict['source_tag_p'] = os.path.abspath(source_tag_p)
    path_dict['source_seg_p'] = os.path.abspath(source_seg_p)
    path_dict['output_dir'] = os.path.abspath(output_dir)
    path_dict['word_vec_p'] = os.path.join(kcws_temp_dir, 'word_vec.txt')
    path_dict['save_vocab'] = os.path.join(kcws_temp_dir, 'pre_word_vec.txt')
    path_dict['save_unk_p'] = os.path.join(kcws_temp_dir, 'source_lines_with_unk.txt')
    
    ''' use in training model'''
    '''this two file are defined in generate_ner_train.py'''
    path_dict['train_data_p'] = os.path.join(kcws_temp_dir, 'train_for_train.txt')
    path_dict['test_data_P'] = os.path.join(kcws_temp_dir, 'train_for_test.txt')
    path_dict['log_dir_p'] = os.path.join(kcws_temp_dir, 'log')

    ''' use in freeze model'''
    log_dir_p = path_dict['log_dir_p']
    path_dict['graph_path'] = os.path.join(log_dir_p, 'graph.pb')
    path_dict['checkpoint'] = os.path.join(log_dir_p, 'model.ckpt')
    path_dict['output_graph_p'] = os.path.join(
        output_dir, 'product_model.pbtxt')
    
    '''use in dump vocaborary'''
    output_dir = path_dict['output_dir']
    path_dict['dump_char_vector_p'] = os.path.join(output_dir, 'char_vec_index.txt')
    path_dict['dump_word_vector_p'] = os.path.join(
        output_dir, 'word_vec_index.txt')
    # try:
    #     print('start configure kcws....')
    #     output = subprocess.check_call('{}/configure'.format(kcws_dir))
    #     print('configure kcws done')
    # except subprocess.CalledProcessError:
    #     print('Exception handled')
    return path_dict

def train_w2v(path_dict):
    source_seg_p = path_dict['source_seg_p']
    kcws_temp_dir = path_dict['kcws_temp_dir']
    word_vec_p = path_dict['word_vec_p']
    save_vocab = path_dict['save_vocab']
    save_unk_p = path_dict['save_unk_p']
    dash = '-'
    print('{}start train word to vector{}'.format(dash * 15, dash * 15))
    os.chdir(kcws_dir)
    build_w2v_path = os.path.join('third_party', 'word2vec')

    try:
        output = subprocess.check_output(
            'bazel build {}:word2vec'.format(build_w2v_path), shell=True)
    except subprocess.CalledProcessError as e:
        print('run build word2vec failed')
        raise e

    try:
        output = subprocess.check_output(
            ['bazel-bin/third_party/word2vec/word2vec', '-train', source_seg_p, '-min-count 5', '-save-vocab', save_vocab])
    except subprocess.CalledProcessError as e:
        print('traing w2v failed')
        raise e

    try:
        output = subprocess.check_output(
            ['python', 'kcws/train/replace_unk.py', save_vocab, source_seg_p, save_unk_p])
    except subprocess.CalledProcessError as e:
        print('run replace unk error')
        raise e

    # word_vec_p = os.path.join(kcws_temp_dir, 'word_vec.txt')
    try:
        output = subprocess.check_output(
            ['bazel-bin/third_party/word2vec/word2vec', '-train',
             save_unk_p,
             '-output',
             word_vec_p,
             '-size', '150',
             '-window', '5',
             '-sample', '1e-4',
             '-negative', '5',
             '-hs', '0',
             '-binary', '0',
             '-cbow', '0',
             '-iter', '3',
             '-min-count', '5',
             '-hs', '1'])
    except subprocess.CalledProcessError as e:
        print('training word2vector error')
        raise e

    print(' ')
    print('{}train word to vector end{}'.format(dash * 15, dash * 15))
    os.chdir(root_dir)


def train_model(path_dict):
    char_vector_p = path_dict['char_vector_p']
    word_vector_p = path_dict['word_vector_p']
    tag_scheme_f = path_dict['tag_scheme_f']
    source_tag_p = path_dict['source_tag_p']
    kcws_temp_dir = path_dict['kcws_temp_dir']
    train_data_p = path_dict['train_data_p']
    test_data_P = path_dict['test_data_P']
    log_dir_p = path_dict['log_dir_p']
    dash = '-'
    print('{} start train NER model {}'.format(dash * 15, dash * 15))
    os.chdir(kcws_dir)
    try:
        output = subprocess.check_output(
            'bazel build -c opt kcws/train:generate_ner_train', shell=True)
    except subprocess.CalledProcessError as e:
        print('run build train generate_ner_train error')
        raise e

    try:
        output = subprocess.check_output(
            ['bazel-bin/kcws/train/generate_ner_train',
             char_vector_p,
             word_vector_p,
             tag_scheme_f,
             source_tag_p,
             kcws_temp_dir])
    except subprocess.CalledProcessError as e:
        print('run generate_ner_train error')
        raise e
    
    retunr_code = subprocess.check_call(
        ['python3', 'kcws/train/train_ner.py',
            '--train_data_path', train_data_p,
            '--test_data_path', test_data_P,
            '--log_dir', log_dir_p,
            '--word_word2vec_path', word_vector_p,
            '--char_word2vec_path', char_vector_p,
        ]
    )
    if retunr_code != 0:
        print('run train_ner failed')
        sys.exit(0)
    os.chdir(root_dir)


def freeze_model(path_dict):
    graph_path = path_dict['graph_path']
    checkpoint = path_dict['checkpoint']
    output_graph_p = path_dict['output_graph_p']
    output_model_name = '"transitions,Reshape_9"'
    os.chdir(kcws_dir)
    print(graph_path)
    print(checkpoint)
    command = [
        'python3', 'tools/freeze_graph.py',
        '--input_graph', graph_path,
        '--input_binary=true',
        '--input_checkpoint', checkpoint,
        '--output_node_names', output_model_name,
        '--output_graph', output_graph_p
    ]
    return_code = subprocess.check_call(
        ' '.join(command), shell=True
    )
    if return_code != 0:
        print('freeze graph error')
        sys.exit(0)
    os.chdir(current_dir)


def dump_vector_index(path_dict):
    output_dir = path_dict['output_dir']
    
    dump_char_vector_p = path_dict['dump_char_vector_p']
    dump_word_vector_p = path_dict['dump_word_vector_p']
    word_vec_p = path_dict['word_vec_p']
    char_vector_p = path_dict['char_vector_p']
    os.chdir(kcws_dir)
    return_code = subprocess.check_call(
        ['bazel', 'build', 'kcws/cc:dump_vocab']
    )
    
    if return_code != 0:
        sys.exit(1)
    
    return_code = subprocess.check_call(
        [
            './bazel-bin/kcws/cc/dump_vocab',
            word_vec_p,
            dump_word_vector_p,
        ]
    )
    return_code = subprocess.check_call(
        [
            './bazel-bin/kcws/cc/dump_vocab',
            char_vector_p,
            dump_char_vector_p,
        ]
    )
    os.chdir(current_dir)

def run_kcws(source_seg_p, source_tag_p, tag_scheme_f, char_vector_p, output_dir):
    path_dict = set_up_kcws(char_vector_p, source_tag_p,
                           source_seg_p, tag_scheme_f, output_dir)
    train_w2v(path_dict)
    train_model(path_dict)
    freeze_model(path_dict)
    dump_vector_index(path_dict)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_segment_file',
                        help='the file had been segmented',
                        action='store',
                        )
    parser.add_argument('source_tag_file',
                        help='the file had been tagged accroding to product name',
                        action='store',
                        )
    parser.add_argument('tag_scheme_file',
                        help='the file contain tag scheme',
                        action='store',
                        )
    parser.add_argument('char_vector_path',
                        help='the char vector path',
                        action='store',
                        )
    parser.add_argument('--user_dir',
                        help='user dir path',
                        action='store',
                        dest='user_dir',
                        default=os.path.join(root_dir, 'usr'))

    # parser.add_argument('--kcws_temp_dir',
    #                     help='kcws temp dir',
    #                     action='store',
    #                     dest='kcws_temp_dir',
    #                     default=os.path.join(current_dir, 'current_dir'))

    args = parser.parse_args()
    output_dir = os.path.join(args.user_dir, sub_dir)
    hf.check_dir_exist(output_dir)
    run_kcws(args.source_segment_file,
            args.source_tag_file,
            args.tag_scheme_file,
            args.char_vector_path,
            output_dir)


if __name__ == '__main__':
	main()
