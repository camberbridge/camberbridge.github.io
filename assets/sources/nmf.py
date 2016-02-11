# -*- coding: utf-8 -*-
from numpy import *

##
# 同じサイズの2つの行列を行, 列に関してループしながら差の2乗を計算
# 引数: 行列, 行列
# 返り値: 残差平方和
##
def difcost(a,b):
	dif=0

	for i in range(shape(a)[0]):  # 行
		for j in range(shape(a)[1]):  # 列
			dif+=pow(a[i,j]-b[i,j],2)
	return dif

##
# 非負値行列因子分解(行列の乗算と転置の操作)を行う
#   - 目的: かけ合わせることで再びもとの行列を構築できるような以下の二つの小さな行列を探し出すこと
#     - 特徴の行列: 行はそれぞれの特徴で, 列がそれぞれの単語を表す. 値は単語が特徴に対してどれくらい重要であるかを示す. それぞれの特徴は文書セットから引き出したテーマを表している必要がある. 
#     - 重みの行列: 特徴たちを文書の行列にマップする. それぞれの行が文書であり, 列が特徴である. 値はそれぞれの特徴がそれぞれの記事にどの程度適合するかを表す. 
# 乗法的更新ルール: 差の最小化
#   - 用いる4つの更新行列
#     - hn: 転置した重みの行列にデータ行列を掛け合わせたもの
#     - hd: 転置した重みの行列に重みの行列を掛け合わせたものに特徴の行列を掛け合わせたもの
#     - wn: データ行列に転置した特徴の行列を掛け合わせたもの
#     - wd: 重みの行列に特徴の行列を掛け合わせたものに転置した特徴の行列を掛け合わせたもの
#   - 流れ: 特徴の行列にhnを掛けてhdで割る. 重みの行列にwnを描けてwdで割る.
# 引数: 因子分解するmatrix化した特徴行列, 因子の数(全文書から求めたいトピックの数), 更新回数
# 返り値: 重みの行列, 特徴の行列
##
def factorize(v,pc=10,iter=50):
	ic=shape(v)[0]  # vの行数
	fc=shape(v)[1]  # vの列数

	# 重みの行列(w)と特徴の行列(h)をランダムな値で初期化
	w=matrix([[random.random() for j in range(pc)] for i in range(ic)])
	h=matrix([[random.random() for i in range(fc)] for i in range(pc)])

	# 乗法的更新ルール. iter回繰り返す
	for i in range(iter):
		wh=w*h # 目的の行列

		# 差の計算
                # この差(cost)を小さくすることが目的->乗法的更新ルールを適用
		cost=difcost(v,wh)
                # 10回ごとに残差平方和を表示
		if i%10==0: print cost
		# 行列が完全に因子分解されたら終了
		if cost==0: break

		# 特徴の行列を更新
		hn=(transpose(w)*v)
		hd=(transpose(w)*w*h)
		h=matrix(array(h)*array(hn)/array(hd))

		# 重みの行列を更新
		wn=(v*transpose(h))
		wd=(w*h*transpose(h))
		## 実行時エラーが出たら
		## (RuntimeWarning: invalid value encountered in divide)
		#wd = [[1e-20 if (x - 1e-20 < 0) else x for x in lst] for lst in wd.tolist()]
		w=matrix(array(w)*array(wn)/array(wd))

	return w,h

##
# 行列を見やすい形式にして表示する
# 行列の特徴上位いくつかを表示することで重要な単語を確認できる
# 引数: 重みの行列, 特徴の行列, 各文書のタイトル, 出力ファイル名
# 返り値: パターン[文書総数][トピック数][各文書タイトルとその重み],各トピックにおける頻出単語配列[因子数][上位6特徴語]
##
def showfeatures(w,h,titles,wordvec,out='features.txt'):
    with open(out, "w") as outfile:
        pc,wc=shape(h)
        toppatterns=[[] for i in range(len(titles))]
        patternnames=[]

        # 因子数分繰り返し
        for i in range(pc):
            slist=[]
            # 単語とその重みのリストを作る
            # 重みの数繰り返し
            for j in range(wc):
                slist.append((h[i,j],wordvec[j]))
            # 単語のリストを降順に並び替え
            slist.sort()
            slist.reverse()

            # 上位6つの要素(特徴語)を出力
            n=[s[1] for s in slist[0:6]]
            outfile.write(str(n)+'\n')
            print "トピック" + str(i+1) + ": ",
            for hoge in n:
                print hoge,
            print ""
            patternnames.append(n)

            # 当該特徴を持つ文書のリストを作る
            flist=[]
            for j in range(len(titles)):
                # 該当する重みに対応する文書タイトルを重みに結合
                flist.append((w[j,i],titles[j]))
                toppatterns[j].append((w[j,i],i,titles[j]))

            flist.sort()
            flist.reverse()

            # 上位3つの文書を表示
            for f in flist[0:3]:
                outfile.write(str(f)+'\n')
                for hoge in f:
                    print hoge,
                print ""
            outfile.write('\n')

        return toppatterns,patternnames

##
# 行列を見やすい形式にして表示する2
# 各文書が表すトピック(頻出単語(特徴語)上位6件)上位3件を表示する
##
def showarticles(titles,toppatterns,patternnames,out='article.txt'):
    with open(out,'w') as outfile:

        # 全文書について
        for j in range(len(titles)):
            outfile.write(titles[j].encode('utf8')+'\n')
            print "-----" + str(j+1) + "-----" + "\n" + titles[j] + "\n"

            # この文書の特徴たちを取得しソートする
            toppatterns[j].sort()
            toppatterns[j].reverse()

            # 上位3トピックを出力する
            for i in range(3):
                outfile.write(str(toppatterns[j][i][0])+' '+str(patternnames[toppatterns[j][i][1]])+'\n')
                print "トピック" + str(i+1) + ": ",
                for hoge in patternnames[toppatterns[j][i][1]]:
                    print hoge,
                print ""

            outfile.write('\n')
