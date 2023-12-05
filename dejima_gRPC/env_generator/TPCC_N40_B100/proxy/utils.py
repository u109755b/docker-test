import numpy as np
import numbers

# オブジェクトの中の数値要素を全て整数か小数第2位まで丸める
def general_round2(obj):
    # 辞書型
    if type(obj) is dict:
        return {k: general_round2(v) for k, v in obj.items()}
    # リスト型
    if type(obj) in [list, np.ndarray]:
        return [general_round2(x) for x in obj]
    # 数値型
    if isinstance(obj, numbers.Number):
        return int(obj) if round(obj, 2)%1==0 else round(obj, 2)
    # 型エラー
    raise TypeError("general_round2: obj must be dict, list, int or float")


# objの数値要素全てについてv=func(v)を実行する
def general_1obj_func(obj, func):
    # 辞書型
    if type(obj) is dict:
        for k in obj:
            if isinstance(obj[k], numbers.Number):
                raise TypeError("general_1obj_func: values must be dict or list")
            else:
                general_1obj_func(obj[k], func)
        return
    # リスト型
    if type(obj) in [list, np.ndarray]:
        for i, x in enumerate(obj):
            if isinstance(x, numbers.Number):
                obj[i] = func(x)
            else:
                general_1obj_func(obj[i], func)
        return
    # 型エラー
    raise TypeError("general_1obj_func: values must be dict or list")


# obj1とobj2が共通で持っている要素についてv1=func(v1,v2)を実行する
def general_2obj_func(obj1, obj2, func):
    # obj2が数値型
    if isinstance(obj2, numbers.Number):
        if type(obj1) is dict:
            obj2 = {k: obj2 for k in obj1}
            general_2obj_func(obj1, obj2, func)
            return
        if type(obj1) in [list, np.ndarray]:
            obj2 = [obj2 for _ in range(len(obj1))]
            general_2obj_func(obj1, obj2, func)
            return
    # 辞書型
    if type(obj1) is dict:
        keys = set(obj1.keys()) & set(obj2.keys())
        for k in keys:
            if isinstance(obj1[k], numbers.Number):
                raise TypeError("general_2obj_func: values of obj1 must be dict or list")
            else:
                general_2obj_func(obj1[k], obj2[k], func)
        return
    # リスト型
    if type(obj1) in [list, np.ndarray]:
        for (i, x), y in zip(enumerate(obj1), obj2):
            if isinstance(x, numbers.Number):
                obj1[i] = func(x, y)
            else:
                general_2obj_func(obj1[i], obj2[i], func)
        return
    # 型エラー
    raise TypeError("general_2obj_func: values of obj1 must be dict or list")