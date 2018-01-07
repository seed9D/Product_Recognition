#!/usr/bin/python3
#-*-coding:utf-8 -*-
import os
import sys
from collections import defaultdict
from find_frequency_pattern_by_entropy import write_detail
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
import Tries as Tries



class Mutual_Entropy:
    def __init__(self, left_word, right_world, MI):
        self.left_word = left_word
        self.right_word = right_world
        self.MI_entropy = MI

class Trie_node(Tries.Trie_node):
    def __init__(self, left=0, right=0, MI=0):
        super().__init__()
        self.left_entropy = left
        self.right_entropy = right
        self.MI_entropy = MI  # sum of MI here
        self.component_list = []

    def append(self, left_word, right_world, MI):
        new = Mutual_Entropy(left_word, right_world, MI)
        self.component_list.append(new)

class Tree(Tries.Tries):
    def __init__(self):
        super().__init__()

    def push_node(self, sentence, node):
        '''
		add by node
		'''
        if not node or len(sentence) == 0:
            return
        sentence_len = len(sentence)
        temp = self.root
        for index, word in enumerate(sentence):
            if index + 1 == sentence_len:
                temp.child[word] = node
            elif word not in temp.child:
                temp.child[word] = Trie_node()
            temp = temp.child[word]



class ALG():
    def __init__(self, tries, reversed_tries):
        self.tries = tries # build based on prefix-word
        self.reversed_tries = reversed_tries # build based on suffix-word
        self._reject_dict = defaultdict(int)
        self._accept_dict = defaultdict(int)
        self.LOW_mutual_entropy_threshold = 1e-3  # reject
        self.HIGH_mutual_entropy_threshold = 1e-2
        self.LOW_neighbor_entropy_threshold = 0.3  # reject
        self.HIGH_neighbor_entropy_threshold = 1.1
        
        self.traversal_leaf_key()

    def _accept(self, key):
        self._accept_dict[key] += 1

    def _reject(self, key):
        self._reject_dict[key] += 1
    
    def traversal_leaf_key(self):
        leaf_key_list = self.tries.find_leaf_string()
        leaf_key_list = sorted(leaf_key_list)
        for key in leaf_key_list:
            _, node = self.tries.search(key)
            if not node:
                continue
            self.threshold_step(key, node)
            self.traversal_prefix(key)

    def traversal_prefix(self, key):
        prefix_key_list = [key[:i] for i in range(len(key))]  # from short to long
        node_list = []
        for k in prefix_key_list:
            _, n = self.tries.search(k)
            if n:
                node_list.append(k, n)
        for key, node in node_list:
            self.threshold_step(key, node)
            self.traversal_component(key)
        self.compare_prefix_step(node_list)

    def traversal_component(self, key):
        w, node = self.tries.search(key)
        assert(w == key)
        if not node:
            return
        # min_one = min(node.component_list, key=lambda x: x.MI_entropy)
        sort_component = sorted(node.component_list,
                                key=lambda x: x.MI_entropy)
        min_one = None
        for ele in sort_component:
            min_one = ele
            if len(min_one.left_word) > 1 and len(min_one.right_word) > 1:
                break

        if min_one:
            _, left_MI_node = self.tries.search[min_one.left_word]
            _, right_MI_node = self.tries.search[min_one.right_word]
            self.traversal_prefix_and_suffix(min_one.left_word)
            self.traversal_prefix_and_suffix(min_one.right_word)

            self.detect_compound_word_step(
                key, min_one.left_word, min_one.right_word)

    def traversal_prefix_and_suffix(self, key):
        self.compare_component_predix_step(key)
        self.compare_component_suffix_step(key)

    def detect_compound_word_step(self, key, left_node, right_node):
        if not left_node or not right_node:
            return
        # left (prefix)
        if left_node.right_entropy > self.HIGH_neighbor_entropy_threshold:
            # right (suffix)
            if right_node.left_entropy > self.HIGH_neighbor_entropy_threshold:
                self._accept(key)
            elif right_node.left_entropy < self.LOW_neighbor_entropy_threshold:
                self._reject(key)
        elif left_node.right_entropy < self.LOW_neighbor_entropy_threshold:
            self._reject(key)

    def compare_component_suffix_step(self, key):
        '''
        I want to find out the suffix word list of the key
        so I first reverse the key and traversal the tries which is build by reversed keys
        Actually, suffix in key is prefix in reversed key
        '''
        reversed_key = key[::-1]  # reverse a sting
        prefix_word_list = self.reversed_tries.search_word_by_prefix(
            reversed_key)
        node_list = [self.tries.search(word) for word in prefix_word_list]
        key_count = 0
        for node in node_list:
            sort_component = sorted(node.component_list,
                                    key=lambda x: x.MI_entropy)
            min_one = None
            for ele in sort_component:
                min_one = ele
                if len(min_one.left_word) > 1 and len(min_one.right_word) > 1:
                    break
            if min_one:
                if min_one.left_word is reversed_key:
                    key_count += 1

        if key_count > len(node_list):
            self._accept(key)
        elif len(node_list) * (0.5) > key_count:
            self._reject(key)

    def compare_component_predix_step(self, key):
        '''
        compare key's MI entropy in its group of prefix word
        '''
        
        # compare prefix
        prefix_word_list = self.tries.search_word_by_prefix(key)
        node_list = [self.tries.search(word) for word in prefix_word_list]
        key_count = 0
        for node in node_list:
            sort_component = sorted(node.component_list,
                                    key=lambda x: x.MI_entropy)
            min_one = None
            for ele in sort_component:
                min_one = ele
                if len(min_one.left_word) > 1 and len(min_one.right_word) > 1:
                    break
            if min_one:
                if min_one.left_word is key:
                    key_count += 1
        
        if key_count > len(node_list):
            self._accept(key)
        elif len(node_list) * (0.5) > key_count:
            self._reject(key)

    def threshold_step(self, key, node):
        if not node:
            return
        if node.MI_entropy < self.LOW_mutual_entropy_threshold:
            self._reject(key)
        elif node.MI_entropy > self.HIGH_mutual_entropy_threshold:
            self._accept(key)

        if min(node.left_entropy, node.right_entropy) < self.LOW_neighbor_entropy_threshold:
            self._reject(key)
        elif node.left_entropy > self.HIGH_neighbor_entropy_threshold and node.right_entropy > self.HIGH_neighbor_entropy_threshold:
            self._accept(key)
    
   
    def compare_prefix_step(self, node_list):
        def feature_zero_free_degree(entropy_list):
            flag = False
            for key, entropy in entropy_list:
                if flag:
                    self._accept(key)
                    flag = False
                if entropy < 0.001:
                    self._reject(key)
                    flag = True

        right_entropy_list = [(ele[0], ele[1].right_entropy)
                              for ele in node_list if ele[1]]
        left_entropy_list = [(ele[0], ele[1].left_entropy)
                             for ele in node_list if ele[1]]
        feature_zero_free_degree(right_entropy_list)
        feature_zero_free_degree(left_entropy_list)

    

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
    tries = Tree()
    for k, v in entropy_dict_.items():
        #v[0][0] is joint_probability
        MI_ent = v[0][1]
        left_ent = v[0][2]
        right_ent = v[0][3]
        new_node = Trie_node(MI_ent, left_ent, right_ent)

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
    write_detail(reversed_entropy_dict, os.path.join(root_dir, 'usr', 'reversed_detail_information.txt'))
    return build_prefix_tree(reversed_entropy_dict)

def run_alg():
    entropy_dict_ = load_entropy_information(os.path.join(
        root_dir, 'usr', 'detail_information.txt'))
    tries = build_prefix_tree(entropy_dict_)
    reversed_tries = build_reverse_prefix_tree(entropy_dict_)
    del entropy_dict_
if __name__ == '__main__':
    run_alg()
