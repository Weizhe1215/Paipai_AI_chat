import re
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


class Parse_recognition:
    def __init__(self):
        self.categorical_features = ['因子挖掘', '模型种类', '选股范围']
        self.number_features =

    @staticmethod
    def parse_factors(factor_str):
        """解析因子组成字符串，提取量价类因子和基本面因子的百分比"""
        pattern = r'量价类因子：(\d+)%; 基本面因子：(\d+)%'
        match = re.search(pattern, factor_str)
        if match:
            return int(match.group(1)), int(match.group(2))
        else:
            return None, None

    @staticmethod
    def parse_turnover(turnover_str):
        """解析交易频率字符串，提取换手率的数值范围"""
        pattern = r'换手率(\d+)-?(\d+)?倍'
        match = re.search(pattern, turnover_str)
        if match:
            return int(match.group(1)), int(match.group(2)) if match.group(2) else int(match.group(1))
        else:
            return None, None

    def parse_one_hot_encoding(self, categorical_features, data):
        data_encoded = pd.get_dummies(data, columns=categorical_features)
        data_encoded = data_encoded.drop(columns=['因子组成','交易频率'])
