#!/usr/bin/env python3
# coding: utf-8
# File: pattern.py
# Author: lhy<lhy_in_blcu@126.com,https://huangyong.github.io>
# Date: 18-7-15

import pymongo
import re
import jieba
from sentence_parser import *

class EventGraph:
    def __init__(self):
        conn = pymongo.MongoClient()
        self.pattern = re.compile(r'(.*)(其次|然后|接着|随后|接下来)(.*)')
        self.col = conn['travel']['doc']
        self.col_insert = conn['travel']['events']
        self.parse_handler = LtpParser()

    '''长句切分'''
    def seg_long_sents(self, content):
        return [sentence for sentence in re.split(r'[？?！!。；;：:\n\r….·]', content.replace(' ','').replace('\u3000','')) if len(sentence) > 5]

    '''短句切分'''
    def process_subsent(self, content):
        return [s for s in re.split(r'[,、，和与及且跟（）~▲．]', content) if len(s)>1]

    '''处理数据库中的文本'''
    def process_doc(self):
        count = 0
        for item in self.col.find():
            content = item['content']
            events_all = self.collect_event(content)
            if events_all:
                data = {}
                data['events'] = events_all
                self.col_insert.insert(data)
            else:
                continue

    '''统计收集EVENT'''
    def collect_event(self, content):
        events_all = []
        sents= self.seg_long_sents(content)
        for sent in sents:
            events = self.event_extract(sent)
            if events:
                events_all.append(events)
        return events_all

    '''顺承事件抽取'''
    def event_extract(self, sent):
        result = self.pattern.findall(sent)
        if result:
            event_seqs = []
            for tmp in result:
                pre = tmp[0]
                post = tmp[2]
                pre_sents = self.process_subsent(pre)
                post_sents = self.process_subsent(post)
                if pre_sents and post_sents:
                    event_seqs += pre_sents
                    event_seqs += post_sents
                else:
                    continue
            '''对事件进行结构化'''
            if event_seqs:
                events = self.extract_phrase(event_seqs)
                return events
            else:
                pass
        return []


    '''将一个长句中的句子进行分解，提取出其中的vob短语'''
    def extract_phrase(self, event_seqs):
        events = []
        for event in event_seqs:
            vobs = self.vob_exract(event)
            if vobs:
                events += vobs
        return events

    '''提取VOB关系'''
    def vob_exract(self, content):
        vobs = []
        words = list(jieba.cut(content))
        if len(words) >= 300:
            return []
        postags = self.parse_handler.get_postag(words)
        tuples, child_dict_list = self.parse_handler.parser_main(words, postags)
        for tuple in tuples:
            rel = tuple[-1]
            pos_verb= tuple[4][0]
            pos_object = tuple[2][0]
            if rel == 'VOB' and (pos_verb, pos_object) in [('v', 'n'), ('v', 'i')]:
                phrase = ''.join([tuple[3], '#', tuple[1]])
                vobs.append(phrase)
        return vobs

handler = EventGraph()
handler.process_doc()