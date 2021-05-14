from __future__ import annotations

import os, json, math
from collections import defaultdict, Counter
from typing import Union, List, Dict
from nltk.util import ngrams
from wechaty import (
    Message,
    Contact,
    Room
)

from wechaty_puppet import get_logger

logger = get_logger('Utils')


def conversation_object(message: Message) -> Union[Contact, Room]:
    """get conversation object"""
    room = message.room()
    if room:
        return room
    return message.talker()



class SupportSet:

    P_VALUE = 'P_VALUE'

    def __init__(self, support_sets: Dict[str, List[str]]): 
        logger.info('init support sets ...')
        self.confidence_score = 0.5
        support_set_info = [f"LABEL<{label}> -> {len(sets)}" for label, sets in support_sets.items()]
        logger.info('\n'.join(support_set_info))

        self._support_sets: Dict[str, List[str]] = support_sets
    
    @classmethod
    def from_file(cls, file: str) -> SupportSet:
        """from_file: create support from file

        Args:
            file (str): the file of support sets
        """
        with open(file, 'r+', encoding='utf-8') as f:
            support_sets = json.load(f)
        return SupportSet(support_sets)
    
    @classmethod
    def from_files(cls, files: List[str]) -> SupportSet:
        support_sets = defaultdict(list)
        for file in files:
            with open(file, 'r+', encoding='utf-8') as f:
                sub_sets = json.load(f)
                for label, sets in sub_sets.items():
                    support_sets[label].extend(sets)

        return SupportSet(support_sets)

    def add_set(self, label: str, sets: List[str]):
        """add_set: 手动往类中添加支撑集

        Args:
            label (str): 标签名称
            sets (List[str]): 支撑集的数量
        """
        if label not in self._support_sets:
            self._support_sets[label] = set()

        for support_set in sets:
            self._support_sets[label].add(support_set)

    def is_match(self, text: str, sets: List[str]) -> bool:
        """is_match: 判断文本是否和sets匹配

        Args:
            text (str): 待判断的文本
            sets (List[str]): support sets
        """
        NGRAM = 2

        def get_character_level_tuples_nosentences(text):
            if not text: return None
            text = text.lower()

            ng = ngrams(list(text), NGRAM)

            return list(ng)

        def cosine_similarity_ngrams(a, b):
            vec1 = Counter(a)
            vec2 = Counter(b)
            
            intersection = set(vec1.keys()) & set(vec2.keys())
            numerator = sum([vec1[x] * vec2[x] for x in intersection])

            sum1 = sum([vec1[x]**2 for x in vec1.keys()])
            sum2 = sum([vec2[x]**2 for x in vec2.keys()])
            denominator = math.sqrt(sum1) * math.sqrt(sum2)

            if not denominator:
                return 0.0
            return float(numerator) / denominator

        def get_similarity_score(text_a, text_b) -> float:

            gram_a = get_character_level_tuples_nosentences(text_a)
            gram_b = get_character_level_tuples_nosentences(text_b)
            return cosine_similarity_ngrams(gram_a,gram_b)

        for support_item in sets:
            score = get_similarity_score(text, support_item)
            if score >= self.confidence_score:
                return True
        return False

    def predict_labels(self, text: str) -> List[str]:
        """predict_labels: 通过给定的文本来预测对应的标签类别

        Args:
            text (str): 待预测的文本类别
        """
        labels = []
        for label, support_sets in self._support_sets.items():
            is_match_label = self.is_match(text, support_sets)
            if is_match_label:
                labels.append(label)
        return labels