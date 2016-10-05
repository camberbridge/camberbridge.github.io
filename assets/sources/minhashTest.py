# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import random
import sys
import math
import seaborn as sns

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
    def calculate(self, set_x, set_y, kNum):
        bagOfX, bagOfY = self.binaryVector(set_x, set_y)

        # 生成するMinHashの数
        k = kNum
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
    # sketchの個数
    kNum = 100
    # 集合の個数
    n = 150
    # n個の集合
    sets = []
    # 要素の値域を[1, 400]つまり要素の種類数dを400にする
    d = 400
    # 集合の要素数を確率的に決める
    prob = 0.3
    
    # n個の集合を生成
    for i in xrange(n):
        ary = [v for v in xrange(1, d + 1) if random.random() < prob]
        sets.append(ary)

    # setsのうち20%をクエリ, 80%をDBにする
    pivot = int(math.ceil(len(sets)*0.2))
    query = sets[:pivot]
    db = sets[pivot:]

    # クエリとDBのJaccard係数を計算して値の昇順にソート
    aryJaccard = []
    for set_x in query:
        for set_y in db:
            dictJaccard = {}
            dictJaccard["Set"] = set_y
            dictJaccard["Score"] = Jaccard().calculate(set_x, set_y)
            aryJaccard.append(dictJaccard)
    # 種類数 = query数 * db数
    aryJaccard = sorted(aryJaccard, key = lambda x:x["Score"])

    # Jaccard係数が大きい上位20件のDBを正解データとして使う
    if len(aryJaccard) > 20:
        aryJaccard = aryJaccard[-20:]

    plotDataSets_x = []
    plotDataSets_y = []
    plotDataSets_label = []

    while kNum <= 10000:
        aryMinHash = []
        for set_x in query:
            for set_y in db:
                dictMinHash = {} 
                dictMinHash["Set"] = set_y
                dictMinHash["Score"] = MinHash().calculate(set_x, set_y, kNum)
                aryMinHash.append(dictMinHash)

        # 種類数 = query数 * db数
        aryMinHash = sorted(aryMinHash, key = lambda x:x["Score"])

        # MinHashによる近似Jaccard係数が大きい上位x(1~100)件
        plotData_x = []
        plotData_y = []
        for x in xrange(1, 101):
            MinHashResultStat = aryMinHash[-x:]

            # MinHashとJaccardの結果で一致する数をカウント
            counter = 0
            for dict_M in MinHashResultStat:
                MinHashResult = set(dict_M["Set"])
                countFlag = False
                for dict_J in aryJaccard:
                    JaccardResult = set(dict_J["Set"])
                    if len(MinHashResult) == len(JaccardResult):
                        counter = counter + 1 if len(MinHashResult & JaccardResult) == len(MinHashResult) else counter
                        countFlag = True
                    if countFlag:
                        break
                if counter >= 20:
                    break

            print x, ",",  kNum, ",", counter,  ",", (float(counter)/x), ",", (float(counter)/20)

            plotData_x.append(float(counter)/20)
            plotData_y.append(float(counter)/x)

        # interpolated precision
        for i in xrange(1, len(plotData_y)):
            if plotData_y[len(plotData_y)-i] > plotData_y[len(plotData_y)-(i+1)]:
                plotData_y[len(plotData_y)-(i+1)] = plotData_y[len(plotData_y)-i]

        plotDataSets_x.append(plotData_x)
        plotDataSets_y.append(plotData_y)
        plotDataSets_label.append("k="+str(kNum))

        kNum *= 10

    # グラフ生成
    fig = sns.mpl.pyplot.figure()
    ax = fig.add_subplot(111)
    for i in xrange(len(plotDataSets_label)):
        ax.plot(plotDataSets_x[i], plotDataSets_y[i], label=plotDataSets_label[i])

    ax.legend()
    sns.plt.title(u"Min HashによるJaccard係数の近似値を用いた類似検索結果のPrecision Recall Curve")
    sns.plt.xlabel(u"Recall")
    sns.plt.ylabel(u"Precision")
    sns.plt.show()
