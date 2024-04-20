import re
import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns




def parse_factors(factor_str):
    """解析因子组成字符串，提取量价类因子和基本面因子的百分比"""
    pattern = r'量价类因子：(\d+)%; 基本面因子：(\d+)%'
    match = re.search(pattern, factor_str)
    if match:
        return int(match.group(1)), int(match.group(2))
    else:
        return None, None


def parse_turnover(turnover_str):
    """解析交易频率字符串，提取换手率的数值范围"""
    pattern = r'换手率(\d+)-?(\d+)?倍'
    match = re.search(pattern, turnover_str)
    if match:
        return int(match.group(1)), int(match.group(2)) if match.group(2) else int(match.group(1))
    else:
        return None, None
