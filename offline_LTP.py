# !/usr/bin/env python2
# -*- coding: utf-8 -*-
from operator import itemgetter
from pyltp import Segmentor
from pyltp import SentenceSplitter
from pyltp import Postagger
import os
from sys import argv

__author__ = '刘宇威'
__date__ = 2017 / 1 / 3

# interrogative_focus = {"哪些", "哪个", "哪几个", "什么"}
interrogative_focus = {"哪", "几", "多", "有", "怎", "咋", "啥"}  # "哪里", "哪儿", "多少"


def process_sentence(sentence):
    """
    预处理句子
    # 英文分号有时候似乎部分替换失败，没有排查出来
    :param sentence:
    :return:
    """
    sentence.replace(';', ',')  # 替换原文中出现的英文分号
    sentence.replace(' ', '')  # 去掉原文中出现的空格
    return sentence.rstrip() # 去掉结尾换行符


def load_sentences(file_loc):
    """
    前置要求：
    读入UTF8格式的句子，每个句子占一行
    数据量相对于可用内存不可过大（没有采用迭代器）
    :param file_loc:
    :return: 处理好的句子句子，用 list 类型保存
    """
    sentences = []
    with open(file_loc, 'r') as read_file:
        sentences = read_file.readlines()
    for i in range(len(sentences)):
        sentences[i] = process_sentence(sentences[i])
    return sentences


def test_pyltp():
    """
    验证 pyltp 的 API
    使用 pytlp 的 一个简单介绍
    :return:
    """
    sent_list = SentenceSplitter.split("开化当地有没有什么特色的小吃，本人比较喜欢吃小吃，有好吃的请推荐下！")  # 分句
    print '\n'.join(sent_list)
    segmentor = Segmentor()
    segmentor.load("D:/ltp-data-v3.3.1/ltp_data/cws.model")
    words = segmentor.segment("(598休闲烂苹果亲子套餐)(预付) 包括哪些项目，我2大1小，是什么价格，1月1日元旦-1月2日。")
    print ' '.join(words)
    segmentor.release()

    postagger = Postagger()  # 初始化实例
    postagger.load('D:/ltp-data-v3.3.1/ltp_data/pos.model')  # 加载模型
    postags = postagger.postag(words)
    print ' '.join(postags)
    postagger.release()


def main():
    """
    前置条件：
        设置读取文件的路径以及文件名
        选择将处理好的句子写入文件的函数
    操作：
        将句子分词 & 标注词性
        根据需要将处理的结果写入文件
    :return: 1 代表出现错误
    """
    # 获得文件路径及文件名
    if len(argv) == 1:
        file_path = 'D:/intern in FIRE/word2vec'
        file_path = 'D:/intern in FIRE/word2vec'
        # file_name = 'allctripreq_demo(trunked).txt'
        # file_name = 'allctripreq_demo.txt'
        # file_name = 'allctripreq_demo_3_15.txt'
        file_name = '数据探索（综合分析指标）.txt'.decode(encoding='utf-8')
    elif len(argv) == 3:
        file_path = argv[1]
        file_name = argv[2]
    else:
        return 1

    # 从文件中读取句子
    sent_list = load_sentences(os.path.join(file_path, file_name))

    segmentor = Segmentor()
    segmentor.load("D:/ltp-data-v3.3.1/ltp_data/cws.model")
    words_list = []  # 元素为list，句子分好词的结果
    for sent in sent_list:
        words_list.append(segmentor.segment(sent))
    segmentor.release()

    postagger = Postagger()  # 初始化实例
    postagger.load('D:/ltp-data-v3.3.1/ltp_data/pos.model')  # 加载模型
    postags_list = []   # 元素为list，句子划分好的词性
    for words in words_list:
        postags_list.append(postagger.postag(words))   # 词性标注
    postagger.release()  # 释放词性模型

    # 将处理的结果写入文件
    write_back(file_path, sent_list, words_list, postags_list)
    # write_csv(file_path, sent_list, words_list, postags_list)
    # sort_by_pos_list(file_path, words_list, postags_list)


def write_back(file_path, sent_list, words_list, postags_list):
    """
    前置条件：设置好写回文件的文件名

        :param file_path: 读写文件的路径
        :param sent_list:
        :param words_list: 每个句子分好词的list
        :param postags_list:每个句子标注完词性的list
        按照格式
            "原句;原句分好词;原句各词词性"
        写入文件
    """
    file_name = "BI_数据探索问句_焦点".decode('utf-8')
    # 写回 "原句;分句1(分好词);分句1各词词性;分句2(分好词);分句2各词词性;..."
    write_file = open(os.path.join(file_path, file_name), 'w')
    for i in range(len(sent_list)):
        sent = sent_list[i]
        words = words_list[i]
        postags = postags_list[i]
        write_file.write("%s;%s;%s\n" %(sent, ' '.join(words), ' '.join(postags)))
    write_file.close()


def write_csv(file_path, sent_list, words_list, postags_list):
    """
        前置条件：设置好写回文件的文件名

        :param file_path: 读写文件的路径
        :param sent_list:
        :param words_list: 每个句子分好词的list
        :param postags_list:每个句子标注完词性的list
        将带有疑问词的多个句子划分为:
            "原句;分句1(分好词);分句1各词词性;分句2(分好词);分句2各词词性;..."
        写入文件
        """
    file_name = "sent;subsent_i words;subsent_i postags"
    for i in range(len(postags_list)):
        postags = postags_list[i]
        postags.append('wp')  # 构造结尾
        state = 0  # 0 ：遇到句子的词汇之前， 1 ：遇到句子的词汇之后 2：在句中遇到标点
        words_sent_with_interrogative = []
        postags_sent_with_interrogative = []

        for j in range(len(postags)):
            # 更新状态机的状态 state = 2 时会立即改变为state = 0
            if state == 0:
                if postags[j] != 'wp':
                    state = 1
            elif state == 1:
                if postags[j] == 'wp':
                    state = 2

            # 根据状态机的状态执行操作
            if state == 1:
                words_sent_with_interrogative.append(words_list[i][j])
                postags_sent_with_interrogative.append(postags_list[i][j])
            elif state == 2:  # 根据标点找到一句完整的子句
                state = 0
                keep_sub_sentence = False
                for word in words_sent_with_interrogative:
                    if word in interrogative_focus:
                        keep_sub_sentence = True
                        break
                if keep_sub_sentence:
                    sent_list[i] += ';' + ' '.join(words_sent_with_interrogative) + ';' + ' '.join(postags_sent_with_interrogative)
                words_sent_with_interrogative = []
                postags_sent_with_interrogative = []
        sent_list[i] += '\n'

    # 写回 "原句;分句1(分好词);分句1各词词性;分句2(分好词);分句2各词词性;..."
    with open(os.path.join(file_path, file_name), 'w') as write_file:
        write_file.writelines(sent_list)


def sort_by_pos_list(file_path, words_list, postags_list):
    """
    前置条件：设置好写回文件的文件名

    按照词性标注的序列对句子排序，并写回文件
    :param file_path: 读写文件的路径
    :param words_list: 每个句子分好词的list
    :param postags_list:每个句子标注完词性的list
    :return:
    """
    file_name = "sent_words;sent_tags(sorted)"

    word_pos_list = []
    for i in range(len(postags_list)):
        postags = postags_list[i]
        postags.append('wp')  # 构造结尾
        state = 0  # 0 ：遇到句子的词汇之前， 1 ：遇到句子的词汇之后 2：在句中遇到标点
        words_sent_with_interrogative = []
        postags_sent_with_interrogative = []

        for j in range(len(postags)):
            # 更新状态机的状态 state = 2 时会立即改变为state = 0
            if state == 0:
                if postags[j] != 'wp':
                    state = 1
            elif state == 1:
                if postags[j] == 'wp':
                    state = 2

            # 根据状态机的状态执行操作
            if state == 1:
                words_sent_with_interrogative.append(words_list[i][j])
                postags_sent_with_interrogative.append(postags_list[i][j])
            elif state == 2:  # 根据标点找到一句完整的子句
                state = 0
                keep_sub_sentence = False
                sort_key = ""   # 用来保存疑问词之后的词性序列
                for k in range(len(words_sent_with_interrogative)):
                    word = words_sent_with_interrogative[k]
                    if keep_sub_sentence:
                        sort_key += postags_sent_with_interrogative[k]
                    if word in interrogative_focus:
                        keep_sub_sentence = True

                if keep_sub_sentence:
                    word_pos_list.append( [sort_key, ' '.join(words_sent_with_interrogative), ' '.join(postags_sent_with_interrogative)] )
                words_sent_with_interrogative = []
                postags_sent_with_interrogative = []

    res = sorted(word_pos_list, key=itemgetter(0))  # 按照第一个元素sort_key来排序

    # 写回排好序的 "分句(分好词); 分句1各词词性";排序所依据的疑问词后的词性序列
    with open(os.path.join(file_path, file_name), 'w') as write_file:
        for item in res:
            write_file.write("%s;%s;%s\n" % (item[1], item[2], item[0]))
            # write_file.write("%s\n" % (item[1]))  # 只输出最后的句子

if __name__ == '__main__':
    # test_pyltp()
    main()
