# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import random
import sys
import math

class SimilarityCal(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate(self, set_x, set_y):
        raise NotImplementedError("not implemented error.")
 
    # 重複要素のない集合の生成
    def uniqueSet(self, set_x, set_y):
        x = set(list(set_x))
        y = set(list(set_y))

        return x, y

    # 2値ベクトルの生成
    def binaryVector(self, set_x, set_y):
        # 集合の要素種類数
        set_xy =  set(list(set_x)) | set(list(set_y))

        x = []
        y = []
        
        for v in set_xy:
            if v in set_x:
                x.append(1)
            else:
                x.append(0)

            if v in set_y:
                y.append(1)
            else:
                y.append(0)

        return x, y

    # 1~引数lengthの範囲で重複なしの乱数を引数length分生成 (length = 集合の要素種類数)
    def generateRanNum(self, length):
        samples = random.sample(xrange(length + 1), length + 1)
        r_t = []

        for v in samples:
            if v != 0 and len(r_t) < length:
                r_t.append(v)

        return r_t


# Jaccard係数
class Jaccard(SimilarityCal):
    def calculate(self, set_x, set_y):
        x, y = self.uniqueSet(set_x, set_y)

        try:
            # 積集合/和集合
            result = float(len(x & y)) / len(x | y)
        except ZeroDivisionError:
            result = 0.0

        return result

# MinHash
class MinHash(SimilarityCal):
    def calculate(self, set_x, set_y):
        bagOfX, bagOfY = self.binaryVector(set_x, set_y)

        # 生成するMinHashの数
        k = int(sys.argv[1])
        # k個のハッシュ値のうち, いくつ一致したか
        counter = 0
        # 第一引数kの回数分ハッシュ関数を生成し, 比較する
        for i in xrange(k):
            hashX = []
            hashY = []

            # r(t)テーブルの生成
            r_t = self.generateRanNum(len(bagOfX))

            for i in xrange(len(bagOfX)):
                if bagOfX[i] == 1:
                    hashX.append(r_t[i])
            mh_x = min(hashX)

            for i in xrange(len(bagOfY)):
                if bagOfY[i] == 1:
                    hashY.append(r_t[i])
            mh_y = min(hashY)

            counter = counter + 1 if mh_x == mh_y else counter

        # MinHashを用いたJaccard係数の近似計算の結果を返す
        return float(counter) / k


if __name__ == '__main__':
    set_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 111, 555, 31, 49, 100, 1000, 1111, 111]
    set_y = [2, 3, 4, 6, 11, 22, 33, 44, 55, 111, 1111, 1000, 100, 10]
    print "MinHash", MinHash().calculate(set_x, set_y)
    print "Jaccard", Jaccard().calculate(set_x, set_y)
