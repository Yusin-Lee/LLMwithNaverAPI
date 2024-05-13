import requests
import urllib
from bs4 import BeautifulSoup
from config import Naver_config
import json
import numpy as np
import time

client_id = Naver_config.client_id
client_secret = Naver_config.Client_secret

# 키워드로 네이버 블로그 글 검색
def search_naver_blog(keyword):
    encText = urllib.parse.quote(keyword)
    url = "https://openapi.naver.com/v1/search/blog?query=" + encText
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
    link_list = []
    desc_list = []
    for item in result.get('items'):
        link_list.append(item['link'])
        desc_list.append(item['description'].replace('<b>','').replace('</b>',''))
    return result, link_list, desc_list

# 블로그 link로 제목, 본문 발췌
def search_content(link):
    link = link.replace("blog","m.blog")
    response = requests.get(link)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find('meta',property="og:title")['content']
    content = []
    res_postct = soup.findAll('div',class_="post_ct")
    try:
        content = " ".join([item.get_text(strip=True) for item in res_postct]).split('URL복사신고하기')[1]
    except:
        content = " ".join([item.get_text(strip=True) for item in res_postct])
    return title, content

# [질문 <-> 블로그 요약] 가장 높은 연관을 갖는 블로그 찾기
def search_top_k(model, question, content_list, link_list, top_k, max_length, title_list=None):
    sentence_pairs = [[question, i] for i in content_list]
    scores = model.compute_score(sentence_pairs,max_passage_length=max_length,weights_for_different_modes=[0.4,0.2,0.4])
    top_k_index = np.argsort(scores['colbert+sparse+dense'])[-top_k:].tolist()
    top_k_desc = np.array(content_list)[top_k_index].tolist()
    top_k_link = np.array(link_list)[top_k_index].tolist()
    if title_list is not None:
        top_k_title = np.array(title_list)[top_k_index].tolist()
        return top_k_desc, top_k_link, top_k_title
    return top_k_desc, top_k_link

# 블로그 N개 본문 발췌
def search_n_contents(link_list):
    top_k_content = []
    top_k_title = []
    for link in link_list:
        try:
            title, content = search_content(link)
            top_k_title.append(title)
            top_k_content.append(content.encode('euc-kr','ignore').decode('euc-kr'))
            time.sleep(np.random.randint(1,4))
        except:
            continue
    return top_k_content, top_k_title
