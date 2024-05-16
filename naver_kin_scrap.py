import urllib
import requests
from bs4 import BeautifulSoup
from config import Naver_config
import json
import re
import numpy as np
import time

client_id = Naver_config.client_id
client_secret = Naver_config.Client_secret

# 키워드로 네이버 지식인 검색
def search_naver_kin(keyword):
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/kin?query=" + encText
    query_response = urllib.request.Request(url)
    query_response.add_header("X-Naver-Client-Id",client_id)
    query_response.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(query_response)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        result = json.loads(response_body.decode('utf-8'))
    else:
        result = "fail"
    titles = []
    links = []
    descs = []
    for item in result.get('items'):
        titles.append(item['title'].replace('<b>','').replace('</b>',''))
        links.append(item['link'])
        descs.append(item['description'].replace('<b>','').replace('</b>',''))
    return result, titles, links, descs

# 지식인 link로 제목, 답변 발췌
def search_content(link):
    pattern = re.compile(r'answerDetail\s+_hashtagHighlightingContents\s+_param|answerDetail _endContents _endContentsText')
    response = requests.get(link)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find('meta',property="og:title")['content']
    res = soup.findAll('div', class_=pattern)
    contents = []
    for item in res:
        text = item.get_text(strip=True).encode('euc-kr','ignore').decode('euc-kr')
        contents.append(text)
    return title, contents

# 지식인 답변 중 가장 긴 K개의 답변 선택하여 저장
def content_top_k_by_length(contents, top_k):
    lengths = [len(x) for x in contents]
    top_k_indexes = np.argsort(lengths)[-top_k:].tolist()
    top_k_contents = np.array(contents)[top_k_indexes].tolist()
    return top_k_contents

# [질문 <-> 지식인 답변] 가장 높은 유사도를 갖는 답변 선택하여 저장
def content_top_k_by_embedding(model, question, contents, top_k, max_length):
    pairs = [[question,item] for item in contents]
    scores = model.compute_score(pairs, max_passage_length=max_length, weights_for_different_modes=[0.4,0.2,0.4])
    indexes = np.argsort(scores['colbert+sparse+dense'])[-top_k:].tolist()
    top_k_contents = np.array(contents)[indexes].tolist()
    return top_k_contents

# [질문 <-> 지식인 요약] 가장 높은 유사도를 갖는 링크 선택하여 저장
def search_top_k(model, question, contents, links, top_k, max_length):
    pairs = [[question,item] for item in contents]
    scores = model.compute_score(pairs, max_passage_length=max_length, weights_for_different_modes=[0.4,0.2,0.4])
    indexes = np.argsort(scores['colbert+sparse+dense'])[-top_k:].tolist()
    top_k_contents = np.array(contents)[indexes].tolist()
    top_k_links = np.array(links)[indexes].tolist()
    return top_k_contents, top_k_links

# N개의 지식인 링크에서 각 K개 씩 답변을 선택하여 저장
def search_n_contents(links, top_k):
    top_k_content = []
    for link in links:
        try:
            _, contents = search_content(link)
            contents = content_top_k_by_length(contents, top_k)
            for item in contents:
                top_k_content.append(item)
            time.sleep(np.random.randint(1,4))
        except:
            continue
    return top_k_content
