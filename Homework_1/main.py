import re
import nltk
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer


dataFile = 'SMSSpamCollection'
oneTDD = "oneTimeDealData.txt"
onlyHWD = "OnlyHaveWordData.txt"
hamWords = "hamDick.json"
spamWords = "spamWorks.json"

hamSentenceNum = 0
spamSentenceNum = 0

hamList = []
spamList = []
allList = []

hamDict = {}
spamDict = {}
allDict = {}
def allLine():
    with open(dataFile,'r+',encoding='UTF-8') as file:
        saveFile = open(oneTDD,'w',encoding='UTF-8')
        AllLine = file.readlines()
        for line in AllLine:
            newline = re.sub(r'[.!#%^$@&*()_+<>?:"|{},`\'\-=/;]','',line.lower())
            #newline = re.sub(r'[0-9]','',newline)
            saveFile.write(newline)


def dealWord():
    with open(oneTDD,'r+',encoding='UTF-8') as file:
        global hamSentenceNum
        global spamSentenceNum
        AllLine = file.readlines()
        for line in AllLine:
            result = re.search('ham\t(.+)',line)
            if  result is not None:
                hamSentenceNum = hamSentenceNum + 1
                tempList = re.split(' ',result.group(1))
                for word in tempList:
                    if word !='':
                        hamList.append(word)
                        allList.append(word)
            else:
                result = re.search('spam\t(.+)',line)
                spamSentenceNum = spamSentenceNum + 1
                tempList = re.split(' ',result.group(1))
                for word in tempList:
                    if word !='':
                        spamList.append(word)
                        allList.append(word)


    dealOnlyLeaveWord()
    stopword()
    lemmat()
    doIt()
    return 1

def lemmat():
    global hamList
    global spamList
    tempList_ham = []
    for w in hamList:
        w1 = WordNetLemmatizer().lemmatize(w)
        tempList_ham.append(w1)
    hamList = tempList_ham
    tempList_spam = []
    for w in spamList:
        w1 = WordNetLemmatizer().lemmatize(w)
        tempList_spam.append(w1)
    spamList = tempList_spam

def stopword():
    for word in spamList:
        if word in stopwords.words('english'):
            spamList.remove(word)
    for word in hamList:
        if word in stopwords.words('english'):
            hamList.remove(word)
def dealOnlyLeaveWord():
    global hamList
    global spamList
    global allList
    for word in hamList:
        result = re.search(r'([a-z]+)',word)
        if result is None:
            hamList.remove(word)
    for word in spamList:
        result = re.search(r'[a-z]+',word)
        if result is None:
            spamList.remove(word)
    for word in allList:
        result = re.search(r'[a-z]+',word)
        if result is None:
            allList.remove(word)

def doIt():
    global hamDict
    global spamDict
    global allDict
    hamDict = nltk.FreqDist(hamList)
    spamDict = nltk.FreqDist(spamList)
    allDict = nltk.FreqDist(allList)
    json_ham = json.dumps(hamDict)
    json_spam = json.dumps(spamDict)
    json_all = json.dumps(allDict)
    json_tdick = {'spam':json_spam,'spamWordNumSum':spamDict.N(),'spamWordNum':spamDict.B(),'ham':json_ham,'hamWordNumSum':hamDict.N(),
                  'hamWord':hamDict.B(),'all':json_all,'allNumSum':allDict.N(),'allNum':allDict.B(),'hamSentenceNum':hamSentenceNum,'spamSentenceNum':spamSentenceNum}
    json_dick = json.dumps(json_tdick)
    with open("Dick.json", 'w', encoding='utf-8') as json_file:
        json.dump(json_dick, json_file, ensure_ascii=False)

    # with open("hamDict.json",'w',encoding='utf-8') as json_file:
    #     json.dump(json_ham,json_file,ensure_ascii=False)
    # with open("spamDict.json",'w',encoding='utf-8') as json_file:
    #     json.dump(json_spam,json_file,ensure_ascii=False)

def getans():
    json_ham = {}
    json_spam = {}
    json_all = {}
    ansList = []
    with open("Dick.json", 'r', encoding='utf-8') as json_file:
        json_dick = json.loads(json.load(json_file))
        json_spam = json.loads(json_dick['spam'])
        spamWordNum = json_dick['spamWordNum']
        json_ham = json.loads(json_dick['ham'])
        hamWordNum = json_dick['hamWord']
        json_all = json.loads(json_dick['all'])
        allNum = json_dick['allNum']
        hamSentenceNum = json_dick['hamSentenceNum']
        spamSentenceNum = json_dick['spamSentenceNum']

        #先验概率
        P_PreHam = hamSentenceNum / (hamSentenceNum + spamSentenceNum)
        P_PreSpam = spamSentenceNum / (hamSentenceNum + spamSentenceNum)

        with open("dofile.txt",'r',encoding='utf-8') as dofile:
            AllLine = dofile.readlines()
            for line in AllLine:
                wordList = re.split(' ',line)
                #单词预处理
                for word in wordList:
                    result = re.search(r'([a-z]+)', word)
                    if result is None:
                        wordList.remove(word)
                for word in wordList:
                    if word in stopwords.words('english'):
                        wordList.remove(word)
                tempList_ham = []
                for w in wordList:
                    w1 = WordNetLemmatizer().lemmatize(w)
                    tempList_ham.append(w1)
                wordList = tempList_ham
                flag = 0
                # 判断拉普拉斯平滑
                for w in wordList:
                    if json_all.get(w) is None:
                        flag = 1
                        break
                p_ham = 1
                p_spam = 1
#                wordnum = wordList.__len__()
                for w in wordList:
                    p1 = json_ham.get(w) if json_ham.get(w) is not None else 0
                    temp_ham = (p1 + flag) / (hamWordNum + allNum * flag)
                    p2 = json_spam.get(w) if json_spam.get(w) is not None else 0
                    temp_spam = (p2 + flag) / (spamWordNum + allNum * flag)
                    p_ham *= temp_ham
                    p_spam *= temp_spam

                p_ham *= P_PreHam
                p_spam *= P_PreSpam
                if (p_ham > p_spam):
                    ansList.append('ham')
                else:
                    ansList.append('spam')

    with open("fileans.txt", 'r', encoding='utf-8') as ansfile:
        ans = ansfile.readlines()
        for i in range(0, ansList.__len__()):
            #print("myans:", ansList[i], "  trueans:", ans[i])
            if ((ansList[i]+'\n') != ans[i]):
                print(i)




    return 1

def initData():
    with open('testData.txt','r', encoding='utf-8') as f:
        Allline = f.readlines()
        fileans = open('fileans.txt', 'w', encoding='UTF-8')
        doflie = open('dofile.txt','w',encoding='utf-8')
        for line in Allline:
            nowLine = line.split('\t',maxsplit=1)
            fileans.write(nowLine[0]+'\n')
            doflie.write(nowLine[1])
        fileans.close()
        doflie.close()

if __name__ == '__main__':
    #nltk.download('stopwords')
    #nltk.download('wordnet')
    allLine()
    #dealWord()
    initData()
    getans()

