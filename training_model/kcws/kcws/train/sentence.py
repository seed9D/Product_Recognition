#!/usr/bin/env python
# -*- coding:utf-8 -*-

# File: sentence.py
# Project: /e/code/kcws
# Created: Thu Jul 27 2017
# Author: Koth Chen
# Copyright (c) 2017 Koth
#
# <<licensetext>>


class Sentence:
    def __init__(self):
        self.tokens = []
        self.chars = 0

    def addToken(self, t):
        self.chars += len(t)
        self.tokens.append(t)

    def clear(self):
        self.tokens = []
        self.chars = 0

    # label -1, unknown
    # 0-> 'S'  single
    # 1-> 'B'  begin
    # 2-> 'M' middle
    # 3-> 'E'  end
    def generate_tr_line(self, x, y, vob):
        for t in self.tokens:
            if len(t) == 1:  # this token only have one word
                x.append(vob.GetWordIndex(str(t[0].encode("utf8"))))  # find the corresponding vector of the word
                y.append(0)  # S
            else:
                nn = len(t)
                for i in range(nn):
                    x.append(vob.GetWordIndex(str(t[i].encode("utf8"))))
                    if i == 0:
                        y.append(1)  # B
                    elif i == (nn - 1):
                        y.append(3)  # E
                    else:
                        y.append(2)  # M
