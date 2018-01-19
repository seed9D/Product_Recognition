# -*- coding: utf-8 -*-
# @Author: Koth Chen
# @Date:   2016-07-26 13:48:32
# @Last Modified by:   Koth
# @Last Modified time: 2017-04-07 23:04:45
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np

import tensorflow as tf
import os
from idcnn import Model as IdCNN
from bilstm import Model as BiLSTM
from time import strftime
from datetime import datetime
import shutil
# from sklearn.metrics import precision_recall_fscore_support
FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_bool('delete_log', 'False', 'tensorflow model path')
tf.app.flags.DEFINE_string('train_data_path', "newcorpus/2014_train.txt",
                           'Training data dir')
tf.app.flags.DEFINE_string('test_data_path', "newcorpus/2014_test.txt",
                           'Test data dir')
tf.app.flags.DEFINE_string('log_dir', "logs", 'The log  dir')
tf.app.flags.DEFINE_string("word2vec_path", "newcorpus/vec.txt",
                           "the word2vec data path")

tf.app.flags.DEFINE_integer("max_sentence_len", 100,
                            "max num of tokens per query")
tf.app.flags.DEFINE_integer("embedding_size", 50, "embedding size")
tf.app.flags.DEFINE_integer("num_tags", 24, "tag number")
tf.app.flags.DEFINE_integer("num_hidden", 140, "hidden unit number")
tf.app.flags.DEFINE_integer("batch_size", 50, "num example per mini batch")
tf.app.flags.DEFINE_integer("train_steps", 150000, "trainning steps")
tf.app.flags.DEFINE_float("learning_rate", 0.001, "learning rate")
tf.app.flags.DEFINE_bool("use_idcnn", False, "whether use the idcnn")
tf.app.flags.DEFINE_integer("track_history", 6, "track max history accuracy")


def do_load_data(path):
    '''
    get the each word in the sentance's vector index
    '''
    x = []
    y = []
    fp = open(path, "r")
    for line in fp.readlines():
        line = line.rstrip()
        if not line:
            continue
        ss = line.split(" ")
        assert (len(ss) == (FLAGS.max_sentence_len * 2)), 'ss len:{} mex len:{}'.format(len(ss), FLAGS.max_sentence_len * 2)
        lx = []
        ly = []
        for i in range(FLAGS.max_sentence_len):
            lx.append(int(ss[i]))
            ly.append(int(ss[i + FLAGS.max_sentence_len]))
        x.append(lx)
        y.append(ly)
    fp.close()
    return np.array(x), np.array(y)


class Model:
    def __init__(self, embeddingSize, distinctTagNum, c2vPath, numHidden):
        self.embeddingSize = embeddingSize
        self.distinctTagNum = distinctTagNum
        self.numHidden = numHidden
        # let word2vec be a variable in tensorflow, 
        # so in prediciton step, it don't need input whole w2v file again, just input the w2v index
        self.c2v = self.load_w2v(c2vPath, FLAGS.embedding_size)  # word2vec path
        self.words = tf.Variable(self.c2v, name="words")
        layers = [  # iterated dilated CNN's block parameter
            {
                'dilation': 1
            },
            {
                'dilation': 1
            },
            {
                'dilation': 2
            },
        ]
        if FLAGS.use_idcnn:
            self.model = IdCNN(layers, 3, FLAGS.num_hidden, FLAGS.embedding_size,
                               FLAGS.max_sentence_len, FLAGS.num_tags)  # filter is 3x3
        else:
            self.model = BiLSTM(
                FLAGS.num_hidden, FLAGS.max_sentence_len, FLAGS.num_tags)
        self.trains_params = None
        self.inp = tf.placeholder(tf.int32,
                                  shape=[None, FLAGS.max_sentence_len],
                                  name="input_placeholder")
        pass

    def length(self, data):
        used = tf.sign(tf.abs(data))
        length = tf.reduce_sum(used, reduction_indices=1)
        length = tf.cast(length, tf.int32)
        return length

    def inference(self, X, reuse=None, trainMode=True):
        word_vectors = tf.nn.embedding_lookup(self.words, X)
        length = self.length(X)
        reuse = False if trainMode else True
        if FLAGS.use_idcnn:
            word_vectors = tf.expand_dims(word_vectors, 1)
            unary_scores = self.model.inference(word_vectors, reuse=reuse)
        else:
            unary_scores = self.model.inference(
                word_vectors, length, reuse=reuse)
        return unary_scores, length

    def loss(self, X, Y):
        P, sequence_length = self.inference(X)
        self.P = P
        self.realY = Y
        log_likelihood, self.transition_params = tf.contrib.crf.crf_log_likelihood(
            P, Y, sequence_length)
        self.log_likelihood = log_likelihood
        loss = tf.reduce_mean(-log_likelihood)
        return loss

    def load_w2v(self, path, expectDim):
        '''
        return: the first one is all zero, and the last are the average number among the dimension
        '''

        fp = open(path, "r")
        print("load data from:", path)
        line = fp.readline().strip()
        ss = line.split(" ")
        total = int(ss[0])  # how many word vector in the file
        dim = int(ss[1])  # each word-vector's dimension
        assert (dim == expectDim)
        ws = []
        mv = [0 for i in range(dim)]  # initial vector to zero vector
        second = -1
        for t in range(total):
            if ss[0] == '<UNK>':
                second = t
            line = fp.readline().strip()
            ss = line.split(" ")
            assert (len(ss) == (dim + 1))
            vals = []
            for i in range(1, dim + 1):  # doesn' contain the original word, only vector
                fv = float(ss[i])
                mv[i - 1] += fv
                vals.append(fv)
            ws.append(vals)
        for i in range(dim):
            mv[i] = mv[i] / total  # average?
        assert (second != -1)
        # append one more token , maybe useless
        ws.append(mv)
        if second != 1:
            t = ws[1]
            ws[1] = ws[second]
            ws[second] = t
        fp.close()
        return np.asarray(ws, dtype=np.float32)

    def test_unary_score(self):
        ''' unary score: for CRF'''
        P, sequence_length = self.inference(self.inp,
                                            reuse=True,
                                            trainMode=False)
        return P, sequence_length


def read_csv(batch_size, file_name):
    filename_queue = tf.train.string_input_producer([file_name])
    reader = tf.TextLineReader(skip_header_lines=0)
    key, value = reader.read(filename_queue)
    # decode_csv will convert a Tensor from type string (the text line) in
    # a tuple of tensor columns with the specified defaults, which also
    # sets the data type for each column
    decoded = tf.decode_csv(
        value,
        field_delim=' ',
        record_defaults=[[0] for i in range(FLAGS.max_sentence_len * 2)])

    # batch actually reads the file and loads "batch_size" rows in a single
    # tensor
    return tf.train.shuffle_batch(decoded,
                                  batch_size=batch_size,
                                  capacity=batch_size * 50,
                                  min_after_dequeue=batch_size)


def test_evaluate(sess, unary_score, test_sequence_length, transMatrix, inp,
                  tX, tY):
    y_label_dict = {}

    def classify_report():
        # target_names = ['B', 'I', 'E', 'S', 'O']
        for k, v in y_label_dict.items():
            precision = v['TP'] / (v['TP'] + v['FP'])
            recall = v['TP'] / (v['TP'] + v['FN'])
            F1 = 2 * recall * precision / (recall + precision)
            print('{} precision:{:.4f} recall:{:.4f} F1:{:.4f}'.format(k, precision, recall, F1))

    def count_label(y_pre, y_true, label_dict):
        if len(y_pre) != len(y_true):
            print(len(y_pre), len(y_true))
            return
        for index, y_p in enumerate(y_pre):
            y_label_dict.setdefault(y_p, {})
            if y_pre[index] == y_true[index]:  # TP
                y_label_dict[y_p].setdefault('TP', 0)
                y_label_dict[y_p]['TP'] += 1
            else:
                y_label_dict[y_p].setdefault('FP', 0)
                y_label_dict[y_p]['FP'] += 1
                y_label_dict.setdefault(y_true[index], {})
                y_label_dict[y_true[index]].setdefault('FN', 0)  # FN
                y_label_dict[y_true[index]]['FN'] += 1

    totalEqual = 0
    batchSize = FLAGS.batch_size
    totalLen = tX.shape[0]
    numBatch = int((tX.shape[0] - 1) / batchSize) + 1
    correct_labels = 0
    total_labels = 0
    for i in range(numBatch):
        endOff = (i + 1) * batchSize
        if endOff > totalLen:
            endOff = totalLen
        y = tY[i * batchSize:endOff]
        feed_dict = {inp: tX[i * batchSize:endOff]}
        unary_score_val, test_sequence_length_val = sess.run(
            [unary_score, test_sequence_length], feed_dict)

        for tf_unary_scores_, y_, sequence_length_ in zip(
                unary_score_val, y, test_sequence_length_val):
            # print("seg len:%d" % (sequence_length_))
            tf_unary_scores_ = tf_unary_scores_[:sequence_length_]
            y_ = y_[:sequence_length_]
            viterbi_sequence, _ = tf.contrib.crf.viterbi_decode(
                tf_unary_scores_, transMatrix)
            # Evaluate word-level accuracy.
            correct_labels += np.sum(np.equal(viterbi_sequence, y_))
            total_labels += sequence_length_
            # count_label(viterbi_sequence, y_, y_label_dict)
            # print(y_, viterbi_sequence)
    accuracy = 100.0 * correct_labels / float(total_labels)
    # classify_report()
    print("Accuracy: {} curret label:{} total label:{}".format(accuracy, correct_labels, total_labels), flush=True)
    return accuracy


def inputs(path):
    whole = read_csv(FLAGS.batch_size, path)
    features = tf.transpose(tf.stack(whole[0:FLAGS.max_sentence_len]))  # word vector
    label = tf.transpose(tf.stack(whole[FLAGS.max_sentence_len:]))  # the correct label of word vector
    return features, label


def train(total_loss):
    optimizer = tf.train.AdamOptimizer(FLAGS.learning_rate)
    gvs = [v for v in tf.trainable_variables()]
    gvs_gredient = optimizer.compute_gradients(total_loss, var_list=gvs)
    capped_gvs_predict = [(tf.clip_by_norm(grad, 5), var) for grad, var in gvs_gredient if grad is not None]
    return optimizer.apply_gradients(capped_gvs_predict)


def main(unused_argv):
    '''
    call by tf.app.run
    '''
    # if os.path.exists(FLAGS.log_dir):
    #     shutil.rmtree(FLAGS.log_dir)

    curdir = os.path.dirname(os.path.realpath(__file__))
    trainDataPath = tf.app.flags.FLAGS.train_data_path
    if not trainDataPath.startswith("/"):
        trainDataPath = curdir + "/../../" + trainDataPath
    graph = tf.Graph()
    with graph.as_default():
        model = Model(FLAGS.embedding_size, FLAGS.num_tags,
                      FLAGS.word2vec_path, FLAGS.num_hidden)
        print("train data path:", trainDataPath)
        X, Y = inputs(trainDataPath)
        tX, tY = do_load_data(tf.app.flags.FLAGS.test_data_path)  # test data
        total_loss = model.loss(X, Y)
        train_op = train(total_loss)
        test_unary_score, test_sequence_length = model.test_unary_score()
        sv = tf.train.Supervisor(graph=graph, logdir=FLAGS.log_dir)
        with sv.managed_session(master='') as sess:
            # actual training loop
            training_steps = FLAGS.train_steps
            trackHist = 0
            bestAcc = 0
            for step in range(training_steps):
                if sv.should_stop():
                    break
                try:
                    _, trainsMatrix = sess.run(
                        [train_op, model.transition_params])
                    # real_X, real_Y, unary_score, log_likelihood, loss, transition = sess.run([X, model.realY, model.P, model.log_likelihood, total_loss, model.transition_params])
                    # print(loss)
                    # for unary_score_, y_ in zip(unary_score, real_Y):

                        # viterbi_sequence, _ = tf.contrib.crf.viterbi_decode(unary_score_, trainsMatrix)
                        # print(viterbi_sequence, y_)
                    # for debugging and learning purposes, see how the loss
                    # gets decremented thru training steps
                    now_time = datetime.now().strftime('%H:%M:%S')
                    if (step + 1) % 100 == 0:
                        print('{} [{}] loss: {}'.format(now_time, step + 1, sess.run(total_loss)), flush=True)
                    if (step + 1) % 1000 == 0 or step == 0:
                        acc = test_evaluate(sess, test_unary_score,
                                            test_sequence_length, trainsMatrix,
                                            model.inp, tX, tY)
                        if acc > bestAcc:
                            if step:
                                sv.saver.save(
                                    sess, FLAGS.log_dir + '/best_model')
                            bestAcc = acc
                            trackHist = 0
                        elif trackHist > FLAGS.track_history:
                            print(
                                "always not good enough in last %d histories, best accuracy:%.3f"
                                % (trackHist, bestAcc))
                            break
                        else:
                            trackHist += 1
                except KeyboardInterrupt as e:
                    sv.saver.save(sess,
                                  FLAGS.log_dir + '/model',
                                  global_step=(step + 1))
                    raise e
            sv.saver.save(sess, FLAGS.log_dir + '/finnal-model')


if __name__ == '__main__':
    tf.app.run()
