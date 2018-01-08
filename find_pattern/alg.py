#!/usr/bin/python3
#-*-coding:utf-8 -*-
import os
import sys
from collections import defaultdict
from find_frequency_pattern_by_entropy import write_detail
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import Tries as Tries
import help_func as hf

logger = hf.create_log()


class Mutual_Entropy:
    def __init__(self, left_word, right_world, MI):
        self.left_word = left_word
        self.right_word = right_world
        self.MI_entropy = float(MI)


class Trie_node(Tries.Trie_node):
    def __init__(self, left=0, right=0, MI=0):
        super().__init__()
        self.left_entropy = float(left)
        self.right_entropy = float(right)
        self.MI_entropy = float(MI)  # sum of MI here
        self.component_list = []

    def append(self, left_word, right_world, MI):
        new = Mutual_Entropy(left_word, right_world, MI)
        self.component_list.append(new)
    
    def copy_node(self, new_node):
        assert(isinstance(new_node, Trie_node))
        self.left_entropy = new_node.left_entropy
        self.right_entropy = new_node.right_entropy
        self.MI_entropy = new_node.MI_entropy
        self.component_list = new_node.component_list

class Tree(Tries.Tries):
    def __init__(self):
        super().__init__()
    
    def push_node(self, sentence, new_node):
        '''
		add by node
        insert problem
		'''
        _, node = self.search(sentence)  # check if this senetence already exist in tree
        if node:
           node.copy_node(new_node)
        else:
            '''
            not exit case
            '''
            temp = self.root
            for index, word in enumerate(sentence):
                if word not in temp.child:
                    temp.child[word] = Trie_node()
                temp = temp.child[word]
            temp.copy_node(new_node)  # add new node at tail

class ALG():
    def __init__(self, tries, reversed_tries):
        self.tries = tries  # build based on prefix-word
        self.reversed_tries = reversed_tries  # build based on suffix-word
        self._score_dict = defaultdict(lambda: {'accept': 0, 'reject': 0})
        # self._reject_dict = defaultdict(int)
        # self._accept_dict = defaultdict(int)
        self.LOW_mutual_entropy_threshold = 1e-3  # reject
        self.HIGH_mutual_entropy_threshold = 2e-2
        self.MIDDLE_mutual_entropy_threshold = (self.LOW_mutual_entropy_threshold + self.HIGH_mutual_entropy_threshold) / 2
        self.LOW_neighbor_entropy_threshold = 0.6  # reject
        self.HIGH_neighbor_entropy_threshold = 2.1
        self.MIDDLE_neighbor_entropy_threshold = (self.LOW_neighbor_entropy_threshold + self.HIGH_neighbor_entropy_threshold) / 2
        self.ratio_neighbor_entropy_threshold = 3
        
        self.mutual_entropy_score_para = 1000
        self.neighbor_entropy_score_para = 100
        self.threshold_step_visted_set = set()  # record visited key
        self.compare_min_component_step_visited_set = set()
        
        self.debug_key = '积木玩具儿童'
        # self.traversal_leaf_key()

    def run(self):
        self.traversal_leaf_key()

    def _accept(self, key, score=1):
        self._score_dict[key]['accept'] += score

    def _reject(self, key, score=1):
        self._score_dict[key]['reject'] += score

    def traversal_leaf_key(self):
        leaf_key_list = self.tries.find_leaf_string()
        leaf_key_list = sorted(leaf_key_list)
        logger.debug('leaf_key_list len {}'.format(len(leaf_key_list)))
        # if self.debug_key not in leaf_key_list:
        #     logger.debug('debug key {} not in leaf key list'.format(self.debug_key))
        for key in leaf_key_list:
            _, node = self.tries.search(key)
            if not node:
                continue
            # self.threshold_step(key, node)
            self.traversal_prefix(key)

    def traversal_prefix(self, key):
        '''
        traversal prefix list such as:
            瓶车
            瓶车价
            瓶车价格
        '''
        prefix_key_list = [key[:i + 1]
                           for i in range(len(key))]  # from short to long
        # if key == self.debug_key:
        #     logger.debug(key)
        #     logger.debug(prefix_key_list)
        node_list = []
        for k in prefix_key_list:
            _, n = self.tries.search(k)
            if n:
                node_list.append((k, n))
        for key, node in node_list:
            self.threshold_step(key, node)
            self.traversal_component(key)

        self.compare_prefix_list_neighbor_entropy_step(node_list)

    def traversal_component(self, key):
        w, node = self.tries.search(key)
        assert(w == key)
        if not node:
            return
        self.compare_component_step(key, node)
        sort_component = sorted(node.component_list,
                                key=lambda x: x.MI_entropy)
        min_one = None
        for ele in sort_component:
            min_one = ele
            if len(min_one.left_word) > 1 and len(min_one.right_word) > 1:
                break
        if min_one:
            if key == self.debug_key:
                logger.debug('min component:{} {}'.format(min_one.left_word, min_one.right_word))
            _, left_MI_node = self.tries.search(min_one.left_word)
            _, right_MI_node = self.tries.search(min_one.right_word)
          
            self.traversal_min_component_prefix_and_suffix(min_one.left_word)
            self.traversal_min_component_prefix_and_suffix(min_one.right_word)

            self.detect_compound_word_step(
                key, left_MI_node, right_MI_node)

    def traversal_min_component_prefix_and_suffix(self, key):
        if key in self.compare_min_component_step_visited_set:
            return
        self.compare_min_component_prefix_step(key)
        self.compare_min_component_suffix_step(key)
        self.compare_min_component_step_visited_set.add(key)
    
    def detect_compound_word_step(self, key, left_node, right_node):
        '''
        inorder to find out valid compound word
        principle:
            left component's right neighgor entropy is high
            right component's left neighbor entropy is high
        '''
        if len(key) in [2, 3]:
            return 
        if not left_node or not right_node:
            return
        if left_node.right_entropy > self.HIGH_neighbor_entropy_threshold and right_node.left_entropy > self.HIGH_neighbor_entropy_threshold:
            
            if left_node.left_entropy > self.HIGH_neighbor_entropy_threshold and right_node.right_entropy > self.HIGH_neighbor_entropy_threshold:
                add_score = right_node.left_entropy + \
                    left_node.right_entropy + left_node.left_entropy + right_node.right_entropy
                self._accept(key, add_score)
            elif left_node.left_entropy < self.LOW_neighbor_entropy_threshold or right_node.right_entropy < self.LOW_neighbor_entropy_threshold:
                self._reject(key)
            elif left_node.left_entropy > self.MIDDLE_neighbor_entropy_threshold and right_node.right_entropy > self.MIDDLE_neighbor_entropy_threshold:
                self._accept(key)
            else:
                pass
        elif left_node.right_entropy < self.LOW_neighbor_entropy_threshold and right_node.left_entropy < self.LOW_neighbor_entropy_threshold:
            reject_score = (
                self.HIGH_neighbor_entropy_threshold - min((left_node.right_entropy, right_node.left_entropy)))
            self._reject(key, reject_score)
        else:
            self._reject(key)

    
        if key == self.debug_key:
            logger.debug('left left ent {}'.format(left_node.left_entropy))
            logger.debug('right right ent {}'.format(right_node.right_entropy))
            logger.debug('{}: {}'.format(self.debug_key, self._score_dict[self.debug_key]))

    def _compare_min_component_step(self, key, tries):
        assert(isinstance(tries, Tree))
        word_list = tries.search_word_by_prefix(key)
        node_list = []
        left_component_list = []
        for word in word_list:
            # skip word len 2 and 3
            if len(word) in [2, 3]:
                continue
            _, node = tries.search(word)
            if node:
                node_list.append(node) 
        
        for node in node_list:
            sort_component = sorted(node.component_list,
                                    key=lambda x: x.MI_entropy)
            min_one = None
            for ele in sort_component:
                min_one = ele
                if len(min_one.left_word) > 1 and len(min_one.right_word) > 1:
                    break
            if min_one:
                left_component_list.append(min_one.left_word)
        return left_component_list

    def compare_min_component_suffix_step(self, key):
        '''
        I want to find out the suffix word list of the key
        so I first reverse the key and traversal the tries which is build by reversed keys
        Actually, suffix in key is prefix in reversed key
        '''
        reversed_key = key[::-1]  # reverse a string
        component_list = self._compare_min_component_step(reversed_key, self.reversed_tries)
        key_count = 0
        for component_word in component_list:
            if component_word == reversed_key:
                key_count += 1

        if key_count > len(component_list) * 0.5:
            self._accept(key)
        elif len(component_list) * (0.2) > key_count:
            self._reject(key)
        if key == self.debug_key:
            logger.debug(self._score_dict[self.debug_key])

    def compare_min_component_prefix_step(self, key):
        '''
        compare key's MI entropy in its group of prefix word
        '''
        component_list = self._compare_min_component_step(
            key, self.reversed_tries)
        key_count = 0
        for component_word in component_list:
            if component_word == key:
                key_count += 1

        if key_count > len(component_list) * 0.5:
            self._accept(key)
        elif len(component_list) * (0.2) > key_count:
            self._reject(key)
        
        if key == self.debug_key:
            logger.debug('key_count:{} node list len:{}'.format(
                key_count, len(component_list)))
            logger.debug(self._score_dict[key])

    def threshold_step(self, key, node):
        # if key == self.debug_key:
        #     logger.debug(key)
        if key in self.threshold_step_visted_set or not node:
            return
        def compare_neighbor_entropy(add_score, reject_score):
            if min(node.left_entropy, node.right_entropy) < self.LOW_neighbor_entropy_threshold:
                reject_score += self.LOW_neighbor_entropy_threshold
            elif node.left_entropy > self.HIGH_neighbor_entropy_threshold and node.right_entropy > self.HIGH_neighbor_entropy_threshold:
                '''
                high confidence
                '''
                add_score += (node.left_entropy + node.right_entropy)
            
            return add_score, reject_score

        def compare_mutual_entropy(add_score, reject_score):
            if node.MI_entropy < self.LOW_mutual_entropy_threshold:
                reject_score += ((self.HIGH_mutual_entropy_threshold -
                                 node.MI_entropy ) * self.mutual_entropy_score_para)
            elif node.MI_entropy > self.HIGH_mutual_entropy_threshold:
                '''
                high confidence
                '''
                add_score += (node.MI_entropy * self.mutual_entropy_score_para)
            return add_score, reject_score
        add_score = reject_score = 0
        add_score, reject_score = compare_mutual_entropy(add_score, reject_score)
        add_score, reject_score = compare_neighbor_entropy(add_score, reject_score)
        self._accept(key, add_score)
        self._reject(key, reject_score)

        self.threshold_step_visted_set.add(key)
        if key == self.debug_key:
            logger.debug(self._score_dict[self.debug_key])

    def compare_prefix_list_neighbor_entropy_step(self, key_node_pair):
        '''
        compare prefix list such as:
            瓶车
            瓶车价
            瓶车价格
        '''
        def compare(main_key_entropy_pair, vise_key_entropy_pair):
            previous_key, previous_entropy = main_key_entropy_pair[0]
            for main, vise in zip(main_key_entropy_pair, vise_key_entropy_pair):
                key, entropy = main
                vise_key, vise_entropy = vise
                assert(key == vise_key)
                # if ratio > self.ratio_neighbor_entropy_threshold:
                if min((vise_entropy, entropy)) > self.MIDDLE_neighbor_entropy_threshold:
                    if abs(entropy) > self.ratio_neighbor_entropy_threshold * abs(previous_entropy):
            
                        self._accept(key, entropy)
                        self._reject(previous_key, abs(entropy - previous_entropy))

                previous_entropy = entropy
                if key == self.debug_key:
                    # logger.debug(entropy / previous_entropy)
                    logger.debug(self._score_dict[self.debug_key])
        
        right_entropy_list = [(ele[0], ele[1].right_entropy)
                              for ele in key_node_pair if ele[1]]
        left_entropy_list = [(ele[0], ele[1].left_entropy)
                             for ele in key_node_pair if ele[1]]   
        
        compare(right_entropy_list, left_entropy_list)
        compare(left_entropy_list, right_entropy_list)

    def compare_component_step(self, key, node):
        '''
        compare key's each component
        the principle is
            if key node's left entropy is below some thresold, its componet's left entropy should not make sense
        reject based
        '''
        assert(isinstance(node, Trie_node)), type(node)
        component_list = node.component_list
        # left
        if node.left_entropy < self.LOW_neighbor_entropy_threshold:
            for component in component_list:
                _, component_node = self.tries.search(component.left_word)
                assert(_ == component.left_word), 'search word {} not match {}'.format(
                    _, component.left_word)
                if not component_node:
                    continue
                if component_node.left_entropy < self.LOW_neighbor_entropy_threshold:
                    score = self.LOW_neighbor_entropy_threshold * self.neighbor_entropy_score_para
                    self._reject(component.left_word, score)
                elif component_node.left_entropy < self.MIDDLE_neighbor_entropy_threshold:
                    self._reject(component.left_word)
                
                if component.left_word == self.debug_key:
                    logger.debug('word:{} left entropy:{}'.format(
                        component.left_word, component_node.left_entropy))

                    logger.debug(self._score_dict[self.debug_key])
                
        elif self.HIGH_neighbor_entropy_threshold > node.left_entropy > self.LOW_neighbor_entropy_threshold:
            pass
        else:
            pass

        # right
        if node.right_entropy < self.LOW_neighbor_entropy_threshold:
            for component in component_list:
                _, component_node = self.tries.search(component.right_word)
                if not component_node:
                    continue
                if component_node.right_entropy < self.LOW_neighbor_entropy_threshold:
                    score = self.LOW_neighbor_entropy_threshold * self.neighbor_entropy_score_para
                    self._reject(component.right_word, score)
                elif component_node.right_entropy < self.MIDDLE_neighbor_entropy_threshold:
                    self._reject(component.right_word)
                if component.right_word == self.debug_key:
                    logger.debug('word:{} right entropy:{}'.format(component.right_word, component_node.right_entropy))
                    logger.debug(self._score_dict[self.debug_key])

        elif self.HIGH_neighbor_entropy_threshold > node.left_entropy > self.LOW_neighbor_entropy_threshold:
            pass
        else:
            pass

    def debug(self):
        _, node = self.tries.search(self.debug_key)
        print(self.debug_key, node.left_entropy)
   
    def decision(self):
        pass

    def final(self):
        # for k, v in self._score_dict.items():
        #     print('{} accept:{} reject {}'.format(k, v['accept'], v['reject']))
        print('total record:{}'.format(len(self._score_dict.keys())))
        return self._score_dict
    
    def print_postive(self):
        postive_dict = {}
        for k, v in self._score_dict.items():
            # print('{} accept:{} reject {}'.format(k, v['accept'], v['reject']))
            if v['accept'] > v['reject'] and v['accept'] > 3:
                postive_dict[k] = v
                postive_dict[k]['accept'] = int(v['accept'])
                postive_dict[k]['reject'] = int(v['reject'])
        # for k, v in postive_dict.items():
            # print('{} accept:{} reject {}'.format(k, int(v['accept']), int(v['reject'])))
           
        print('total postive record:{}'.format(len(postive_dict.keys())))
        return postive_dict

def load_entropy_information(file_path):
    with open(file_path, 'r') as rf:
        entropy_dict_ = defaultdict(list)
        key = ''
        for line in rf:
            if line.startswith('\t'):
                line = line.strip().split('\t')
                assert(len(line) == 6)
                left, write, left_pro, right_pro, pro_multiply, MI = line
                entropy_dict_[key].append(
                    (left, write, left_pro, right_pro, pro_multiply, MI))
            else:
                line = line.strip().split('\t')
                assert(len(line) == 5), line
                key, joint_probability, mutual_entropy, left_entropy, right_entropy = line
                entropy_dict_[key].append((joint_probability,
                                           mutual_entropy, left_entropy, right_entropy))
    return entropy_dict_


def build_prefix_tree(entropy_dict_):
    '''
    please sort before buiding tree
    '''
    tries = Tree()
    for k, v in entropy_dict_.items():
        #v[0][0] is joint_probability
        MI_ent = v[0][1]
        left_ent = v[0][2]
        right_ent = v[0][3]
        new_node = Trie_node(left_ent, right_ent, MI_ent)

        for left, right, _, _, _, MI in v[1:]:
            new_node.append(left, right, MI)
        tries.push_node(k, new_node)
    return tries


def build_reverse_prefix_tree(entropy_dict_):
    def reverse_dict():
        reversd_entropy_dict = defaultdict(list)  # final return dict
        reversed_compount_entropy_dict = defaultdict(list)  # middle temp dict
        for k, v in entropy_dict_.items():
            reversed_key = k[::-1]  # reverse a sting
            joint_probability, mutual_entropy, left_entropy, right_entropy = v[0]
            '''卡通服装 to 裝服通卡 '''
            reversd_entropy_dict[reversed_key].append(
                (joint_probability, mutual_entropy, right_entropy, left_entropy))

            for left, right, left_pro, right_pro, pro_multiply, MI in v[1:]:
                left_reversed = left[::-1]  # reverse a sting
                right_reversed = right[::-1]  # reverse a sting
                '''卡通 服装 to 裝服 通卡 '''
                reversed_key = ''.join([right_reversed, left_reversed])
                reversed_compount_entropy_dict[reversed_key].append(
                    [right_reversed, left_reversed, right_pro, right_pro, pro_multiply, MI])

        '''append reversed_compount_entropy_dict to reversd_entropy_dict'''

        for k, v in reversed_compount_entropy_dict.items():
            if k in reversd_entropy_dict:
                reversd_entropy_dict[k].extend(v)
            else:
                print('key {} not in reversd_entropy_dict'.format(k))
        return reversd_entropy_dict
    reversed_entropy_dict = reverse_dict()
    # write_detail(reversed_entropy_dict, os.path.join(root_dir, 'usr', 'reversed_detail_information.txt'))
    return build_prefix_tree(reversed_entropy_dict)

def write_dict(dict_, path):
    with open(path, 'w') as wf:
        for k in sorted(dict_.keys()):
            v = dict_[k]
            wf.write('{}\t{}\t{}\n'.format(k, v['accept'], v['reject']))

def run_alg():
    entropy_dict_ = load_entropy_information(os.path.join(
        root_dir, 'usr', 'detail_information.txt'))
    tries = build_prefix_tree(entropy_dict_)
    reversed_tries = build_reverse_prefix_tree(entropy_dict_)
    logger.debug('entropy_dict_ len:{}'.format(len(entropy_dict_.keys())))
    del entropy_dict_
    alg = ALG(tries, reversed_tries)
    alg.run()
    # alg.debug()
    all_dict = alg.final()
    positive_dict = alg.print_postive()
    write_dict(all_dict, os.path.join(root_dir, 'usr', 'all_alg.txt'))
    write_dict(positive_dict, os.path.join(root_dir, 'usr', 'postive_alg.txt'))
if __name__ == '__main__':
    run_alg()
