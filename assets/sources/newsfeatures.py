# -*- coding: utf-8 -*-
import feedparser
import re
from janome.tokenizer import Tokenizer

feedlist=['http://rss.allabout.co.jp/aa/latest/ch/health/',
    'http://rss.allabout.co.jp/aa/latest/ch/house/',
    'http://rss.allabout.co.jp/aa/latest/ch/domestic/',
    'http://rss.allabout.co.jp/aa/latest/ch/ch_creditcard/',
    'http://rss.allabout.co.jp/aa/latest/ch/beautydiet/',
    'http://rss.allabout.co.jp/aa/latest/ch/mobile/',
    'http://rss.allabout.co.jp/aa/latest/ch/pet/',
    'http://rss.allabout.co.jp/aa/latest/ch/marriage/',
    'http://rss.allabout.co.jp/aa/latest/ch/mensbeauty/',
    'http://rss.allabout.co.jp/aa/latest/ch/fashion/',
    'http://rss.allabout.co.jp/aa/latest/ch/ch_sweets/',
    'http://rss.allabout.co.jp/aa/latest/ch/examination/',
    'http://rss.allabout.co.jp/aa/latest/ch/auto/',
    'http://rss.allabout.co.jp/aa/latest/ch/homeelectronics/',
    'http://rss.allabout.co.jp/aa/latest/ch/ch_sports/',
    'http://rss.allabout.co.jp/aa/latest/ch/ch_game/',
    'http://rss.allabout.co.jp/aa/latest/ch/ch_hobby/']

##
# 与えられた文字列からHTMLを除く
# 返り値: 文字列
## 
def stripHTML(h):
    p=''
    s=0
    for c in h:
        if c=='<': s=1
        elif c=='>':
            s=0
            p+=' '
        elif s==0: p+=c
    return p

## 
# 単語を分割する
# 返り値: 分かち書きした単語を格納した配列
##
def separatewords(text):
    separatedWord=[]
    t=Tokenizer()
    tokens=t.tokenize(unicode(text, "utf-8"))
    
    for token in tokens:
        posList=token.part_of_speech.split(",")

        pos1=posList[0]
        if isinstance(pos1, unicode):
          pos1=pos1.encode("utf-8")

        pos2=posList[1]
        if isinstance(pos2, unicode):
          pos2=pos2.encode("utf-8")

        ruby=token.reading
        if isinstance(ruby, unicode):
          ruby=ruby.encode("utf-8")

        if pos1=="名詞":
            if pos2!="接尾" and pos2!="代名詞" and pos2!="非自立" and pos2!="数" and pos2!="形容動詞語幹":
                if ruby!="*":
                    separatedWord.append(token.surface.lower())
                    print token.surface.lower()
                elif pos2!="サ変接続" and len(token.surface)>3:
                    # 英単語に関しては4文字以上の単語を扱う
                    separatedWord.append(token.surface.lower())
                    print token.surface.lower()

    return separatedWord

##
# BOW表現する
# feedparserによってfeedのタイトルと本文を抽出して単語の数をカウントする
# 返り値: allwords, articlewords, articletitles
##
def getarticlewords():
    allwords={}  # 全文書の総単語とその出現回数を格納する
    articlewords=[]  # 各文書の総単語とその出現回数を格納する
    articletitles=[]  # 文書タイトルを格納する
    ec=0
    # すべてのフィードをループする
    for feed in feedlist:
        f=feedparser.parse(feed)

        # すべての記事をループする
        for e in f.entries:
            # 同一の記事の場合は飛ばす
            if e.title in articletitles: continue

            # 単語を抽出する
            txt=e.title.encode('utf8')+stripHTML(e.description.encode('utf8'))
            print txt + "\n" + "------------------" + "\n"
            words=separatewords(txt)
            print words
            articlewords.append({})
            articletitles.append(e.title)

            # allwordsとarticlewordsにあるこの単語のカウントを増やす
            for word in words:
                allwords.setdefault(word,0)  # setdefault-辞書に対しての処理: wordがなかったらkeyをword, valueを0でallwordsに登録
                allwords[word]+=1
                articlewords[ec].setdefault(word,0)
                articlewords[ec][word]+=1

            ec+=1

    print "allwords: "
    print allwords
    print "articlewords: "
    print articlewords

    return allwords,articlewords,articletitles

##
# 行を文書総数(articlewの長さ), 列を特徴単語総数(wordvecの長さ)とした特徴行列を生成
# 行列サイズを軽減するために珍しい単語と一般的な単語を除く(1)
# 引数: 全文書の総単語とその出現回数{}, 各文書の総単語とその出現回数[{}]
# 返り値: 特徴行列, 全文書中の特徴単語の配列
##
def makematrix(allw,articlew):
    wordvec=[]

    # 一般的だが一般的すぎない(特徴があるとする)単語のみを利用する
    for w,c in allw.items():
        if c>3 and c<len(articlew)*0.6:  # (1)出現回数が4以上かつ文書総数の6割未満だったらその単語を特徴語とする
            wordvec.append(w)

    # 各文書における特徴単語の出現回数の分布を持つ行列(特徴行列)を生成する
    # (各文書に特徴単語があればその出現回数を要素とし, 無ければ0を要素とする)
    l1=[[(word in f and f[word] or 0) for word in wordvec] for f in articlew]
    return l1,wordvec
