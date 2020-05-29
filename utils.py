import random

"""

choice(seq): 从seq序列中（可以是列表，元组，字符串）随机取一个元素返回

choices(population, weights=None, *, cum_weights=None, k=1)：从population中进行K次随机选取，每次选取一个元素（注意会出现同一个元素多次被选中的情况），weights是相对权重值，population中有几个元素就要有相对应的weights值，cum_weights是累加权重值，例如，相对权重〔10, 5, 30，5〕相当于累积权重〔10, 15, 45，50〕。在内部，在进行选择之前，相对权重被转换为累积权重，因此提供累积权重节省了工作。返回一个列表。

sample(population, k)从population中取样，一次取k个，返回一个k长的列表。

"""


def choose_one(seq: list):
    # 随机挑选一个
    if len(seq) > 0:
        return random.choice(seq)
    else:
        return None


def choose(seq: list, n: int):
    # 不重复随机挑选n个
    if len(seq) > 0:
        n = len(seq) if n > len(seq) else n
        return random.sample(seq, n)
    else:
        return None


if __name__ == "__main__":
    for i in range(10):
        s = [1, 2]
        print(choose(s, 3))
