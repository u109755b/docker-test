import numpy as np
import numbers
import copy

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
def is_dict(obj): return type(obj) is dict
def is_list(obj): return type(obj) in [list, np.ndarray]
def is_value(obj): return isinstance(obj, numbers.Number) or type(obj) is str


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
def general_2obj_func(_obj1, obj2, func, save=False):
    if save == True: obj1 = _obj1
    else: obj1 = copy.deepcopy(_obj1)
    # obj2がvalue型
    if is_value(obj2):
        if is_dict(obj1): obj2 = {k: obj2 for k in obj1}
        if is_list(obj1): obj2 = [obj2 for _ in range(len(obj1))]
        general_2obj_func(obj1, obj2, func, True)
    # 辞書型
    elif is_dict(obj1):
        keys = set(obj1.keys()) & set(obj2.keys())
        for k in keys:
            if is_value(obj1[k]): obj1[k] = func(obj1[k], obj2[k])
            else: general_2obj_func(obj1[k], obj2[k], func, True)
    # リスト型
    elif is_list(obj1):
        index_list = range(min(len(obj1), len(obj2)))
        for i in index_list:
            if is_value(obj1[i]): obj1[i] = func(obj1[i], obj2[i])
            else: general_2obj_func(obj1[i], obj2[i], func, True)
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


# 関数内の時間を計測するためのデコレータ
# def trace_func(tracer, name):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             with tracer.start_as_current_span(name) as span:
#                 return func(*args, **kwargs)
#         return wrapper
#     return decorator