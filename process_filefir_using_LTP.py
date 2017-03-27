# !/usr/bin/env python2
# -*- coding: utf-8 -*-
from pyltp import Segmentor
import os

__author__ = '刘宇威'
__date__ = 2017 / 3 / 16


def get_file_list(cur_dir, file_list):
    """
    存储csv结尾的文件名的绝对路径
    :param cur_dir:
    :param file_list:
    :return:
    """
    if os.path.isfile(cur_dir):
        file_list.append(cur_dir)
    elif os.path.isdir(cur_dir):
        for s in os.listdir(cur_dir):
            # 忽略非txt文件夹
            if s.endswith(".txt") is False:
                continue
            new_dir = os.path.join(cur_dir, s)
            get_file_list(new_dir, file_list)
    return file_list


def process_sentence(sentence):
    """
    替换英文分号，去掉结尾换行符
    :param sentence:
    :return:
    """
    sentence.replace(';', ',')  # 替换原文中出现的英文分号   # 有一部分替换失败了
    sentence.replace(' ', '')  # 去掉原文中出现的空格
    return sentence.rstrip()


def load_sentences(file_loc):
    """
    读入UTF8格式的句子
    每个句子占一行
    返回带有疑问词的子句，以英文分号分隔
    :param file_loc:
    :return: 原句;
    """
    sentences = []
    with open(file_loc,'r') as read_file:
        sentences = read_file.readlines()
    for i in range(len(sentences)):
        sentences[i] = process_sentence(sentences[i])
    return sentences


def main():
    """
    将目录下的句子分词并写回文件
    :return:
    """
    file_path = 'D:/intern in FIRE/intent/CNN'
    file_list = get_file_list(file_path.decode("gbk"), [])
    print(file_list[0].encode("gbk"))

    segmentor = Segmentor()
    segmentor.load("D:/ltp-data-v3.3.1/ltp_data/cws.model")
    for file in file_list:
        file = os.path.basename(file)
        # print(file.encode('utf8'))
        sent_list = load_sentences(os.path.join(file_path, file))
        words_list = []  # 元素为str，句子分好词的结果以空格连接
        for sent in sent_list:
            words_list.append(" ".join(segmentor.segment(sent) ) + '\n' )
        file_loc = os.path.join("D:/intern in FIRE/intent/CNN_segmented", file)
        print(file_loc)
        with open(file_loc, 'w') as write_file:
            write_file.writelines(words_list)

    segmentor.release()


if __name__ == '__main__':
    main()
