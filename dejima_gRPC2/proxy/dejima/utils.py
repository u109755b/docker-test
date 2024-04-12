import numbers
import copy
import numpy as np
from collections import defaultdict

# 便利関数
def divide(x, y, d=None):
    if y != 0: return x / y
    if d: return d
    return x
def round2(x):
    rounded_x = round(x, 2)
    if rounded_x % 1: return rounded_x
    return int(rounded_x)


# 型判定の関数
def is_dict(obj): return type(obj) in [dict, defaultdict]
def is_list(obj): return type(obj) in [list, np.ndarray]
def is_value(obj): return isinstance(obj, numbers.Number) or type(obj) is str   # isinstance also matches subclasses


# objのvalue要素全てについてv=func(v)を実行する
def general_1obj_func(_obj, func, save=False):
    if save == True: obj = _obj
    else: obj = copy.deepcopy(_obj)
    # 辞書型
    if is_dict(obj):
        for k, v in obj.items():
            if is_value(v): obj[k] = func(v)
            else: general_1obj_func(obj[k], func, True)
    # リスト型
    elif is_list(obj):
        for i, x in enumerate(obj):
            if is_value(x): obj[i] = func(x)
            else: general_1obj_func(obj[i], func, True)
    # 型エラー
    else:
        raise TypeError("general_1obj_func: {} is not supported".format(type(obj)))
    return obj


# obj1とobj2が共通で持っているvalue要素についてv1=func(v1,v2)を実行する
# もしassign_v2_value=True ならv1の方に要素がない場合v2の要素を代入する
def general_2obj_func(_obj1, obj2, func, save=False, assign_v2_value=False):
    if save == True: obj1 = _obj1
    else: obj1 = copy.deepcopy(_obj1)
    # obj2がvalue型
    if is_value(obj2):
        if is_dict(obj1): obj2 = {k: obj2 for k in obj1}
        if is_list(obj1): obj2 = [obj2 for _ in range(len(obj1))]
        general_2obj_func(obj1, obj2, func, True, assign_v2_value)
    # 辞書型
    elif is_dict(obj1):
        if assign_v2_value:
            keys = set(obj2.keys())
        else:
            keys = set(obj1.keys()) & set(obj2.keys())
        for k in keys:
            if k not in obj1:
                obj1[k] = copy.deepcopy(obj2[k])
            else:
                if is_value(obj1[k]): obj1[k] = func(obj1[k], obj2[k])
                else: general_2obj_func(obj1[k], obj2[k], func, True, assign_v2_value)
    # リスト型
    elif is_list(obj1):
        if assign_v2_value:
            index_list = range(len(obj2))
        else:
            index_list = range(min(len(obj1), len(obj2)))
        for i in index_list:
            if i >= len(obj1):
                obj1.append(copy.deepcopy(obj2[i]))
            else:
                if is_value(obj1[i]): obj1[i] = func(obj1[i], obj2[i])
                else: general_2obj_func(obj1[i], obj2[i], func, True, assign_v2_value)
    # 型エラー
    else:
        raise TypeError("general_2obj_func: {} is not supported".format(type(obj1)))
    return obj1


# オブジェクトの中の数値要素を全て整数か小数第2位まで丸める
def general_round2(obj, save=False):
    round2 = lambda x: int(x) if round(x, 2)%1==0 else round(x, 2)
    if isinstance(obj, numbers.Number): return round2(obj)
    if is_dict(obj) or is_list(obj): return general_1obj_func(obj, round2, save)
    raise TypeError("general_round2: {} is not supported".format(type(obj)))


# NをK人で分ける
class BaseDivider:
    def __init__(self, N, K):
        self.N = N
        self.K = K
        self.k_quotient = N // K
        self.k_remainder = N % K
        self.n_quotient = K // N
        self.n_remainder = K % N

    def check_k_validity(self, k):
        if k < 1 or self.K < k:
            raise IndexError("BaseDiviser: k must be 1 <= k <= K")

    def get_range_size(self, k):
        if self.N >= self.K:
            n_range_size = self.k_quotient + (self.k_remainder >= k)
        else:
            n_range_size = 1
        return n_range_size

    def get_start(self, k, offset=0):
        self.check_k_validity(k)
        if self.N >= self.K:
            start_n = self.k_quotient * (k-1) + min(self.k_remainder, k-1) + 1
        else:
            if k <= (self.n_quotient+1) * self.n_remainder:
                start_n = (k-1) // (self.n_quotient+1) + 1
            else:
                k2 = k - (self.n_quotient+1) * self.n_remainder
                start_n = (k2-1) // self.n_quotient + 1 + self.n_remainder
        return start_n + offset

    def get_end(self, k, offset=0):
        end_n = self.get_start(k) + self.get_range_size(k)
        return end_n + offset

    def get_range(self, k, offset=0):
        start_n = self.get_start(k, offset)
        end_n = self.get_end(k, offset)
        n_range = list(range(start_n, end_n))
        return n_range


# NをK人で分ける
class NDivider:
    def __init__(self, N, K):
        self.N, self.K = N, K
        self.divider = BaseDivider(N, K)
        self.rdivider = BaseDivider(K, N)

    def get_n_range_size(self, k):
        return self.divider.get_range_size(k)

    def get_start_n(self, k, offset=0):
        return self.divider.get_start(k, offset)

    def get_end_n(self, k, offset=0):
        return self.divider.get_end(k, offset)

    def get_n_range(self, k, offset=0):
        return self.divider.get_range(k, offset)

    def get_k_range(self, n, offset=0):
        return self.rdivider.get_range(n, offset)

    def get_both_range(self, k, n_offset=0, k_offset=0):
        """
        return n_range, k_range
        - n_range: list of n which the specified k corresponds to
        - k_range: list of k which n_range corresponds to
        """
        n_range = self.get_n_range(k, n_offset)
        if self.N >= self.K:
            k_range = [k+k_offset]
        else:
            k_range = self.get_k_range(n_range[0]-n_offset, k_offset)
        return n_range, k_range
