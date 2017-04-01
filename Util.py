# setup library imports
import io, time, json
import requests
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup

# 请填写你作业网站的登录名和密码
auth=('xiaoyuh1', 'yourpassword')


'''
用来下载老师的testcase
query: query file 的 url
param: param file 的url


使用范例
for i in range(63):
    query = 'http://boston.lti.cs.cmu.edu/classes/11-642/HW/HTS/tests/HW2-Train-%d.qry' % i
    param = 'http://boston.lti.cs.cmu.edu/classes/11-642/HW/HTS/tests/HW2-Train-%d.param' % i
    retrieve(query, param)

'''
def retrieve(query, param):
    query_response = requests.get(query, auth=auth)
    param_response = requests.get(param, auth=auth)
    
    p = param_response.content.strip()
    right = p[p.index('retrievalAlgorithm'):]
    algo = right[:right.index("\n")]
    print i, '-' * 10
    print algo
    print 
    print query_response.content.strip()
    
  
'''
用于网站左边的那个测试
pretty print返回的html页面
'''
def prettyPrintHTML(html):
    soup = BeautifulSoup(html)

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text(separator="\n")

    # break into lines and remove leading and trailing space on each
    lines = (line for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    print(text)

    

def getLeftSideSoup(filePath, logtype):
    testing_url = 'http://boston.lti.cs.cmu.edu/classes/11-642/HW/HTS/tes.cgi'
    payload = {'logtype': logtype, 'hwid': 'HW3', 'id':'xiaoyuh1'}
    files = {'infile': open(filePath, 'rb')}
    r = requests.post(testing_url, files=files, auth=auth, data=payload)
    html = r.content
    return BeautifulSoup(html)
    

'''
用于网站左边的那个测试
pretty print返回的html页面
提交试验结果，求MAP, P10, P10, P30

使用范例
autoSubmitCode('/Users/hexiaoyu/Desktop/11642 search/QueryEval/output/xxxx.teln')
'''    
def getTrecSummaryScore(filePath):
    soup = getLeftSideSoup(filePath, 'Summary')

    text_tmp = soup.get_text(separator="\n")
    text = [line.strip() for line in text_tmp.split('\n') if 'map ' in line or 'P10 ' in line or 'P20 ' in line or 'P30 ' in line]
#     print '\n'.join(text)
    assert len(text) == 4
    temp = text.pop(0)
    text.append(temp)

    for line in text:
        print line[-6:]
    print ""
    

'''
Retrieve the detailed score from trec_eval service
If the total query number is N, there will be 
N line "map 195 0.0148"
1 line "map all 0.2063"
discard the map all line
'''
def getTrecDetailedScore(filePath):
    soup = getLeftSideSoup(filePath, 'Detailed')
    text_tmp = soup.get_text(separator="\n")
    text = [line.strip() for line in text_tmp.split('\n') if 'map ' in line and 'all' not in line]
    mapScore = [line[-6:] for line in text]
#     print "text"
#     print text
#     print " | ".join(mapScore)
#     print len(mapScore)
    return mapScore
    

    
'''
这个是HW3中用来得到win loss rate的工具。

# 先得到baseline的TrecDetailedScore
baseLine = getTrecDetailedScore("hw3/output/E1-RankedBoolean.teln")
# 然后比较baseLine和my-otuput.teln的win loss 
getWinLoss(baseLine, 'My-output.teln')
# sample output: win, loss, equal 10 10  0
'''
def getWinLoss(baseLine, filePath):
    myScore = getTrecDetailedScore(filePath)
    for base, my in zip(baseLine, myScore):
        print base, my
    win = sum([1 for base, my in zip(baseLine, myScore) if base < my])
    loss = sum([1 for base, my in zip(baseLine, myScore) if base > my])
    equal = sum([1 for base, my in zip(baseLine, myScore) if base == my])
#     print " ".join(baseLine)
#     print " ".join(myScore)
    print "win, loss, equal %2d %2d %2d" % (win, loss, equal)
    
    
    
'''
autoCheckCorrectness的helper函数
'''
def getCheckListPlayload(nums):
    checklist = []
    for i in nums:
        checklist.append('HW3-Train-%d' % i)
    return checklist


'''
用于老师网站右侧，自动跑test case看程序是否正确
checklist2里面的内容是test case 的名字，最多10个
使用范例

checklist2 = ['HW2-train-Nested-0', 'HW2-train-Nested-1', 'HW2-train-Nested-2', 'HW2-train-Weight-0', 'HW2-train-Weight-1']
autoCheckCorrectness(checklist2)
'''
def autoCheckCorrectness(checklist):
    checking_url = 'http://boston.lti.cs.cmu.edu/classes/11-642/HW/HTS/hts.cgi'
    payload = {'submissionType': 'interim', 'hwid': 'HW3', 'test': checklist}
    filePath = r'/Users/hexiaoyu/Desktop/11642 search/QueryEval/QryEval.zip'
    files = {'infile': open(filePath, 'rb')}
    r = requests.post(checking_url, files=files, auth=auth, data=payload)
    html = r.content
    prettyPrintHTML(html)