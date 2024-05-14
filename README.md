# LLMwithRAG_naverblog
```
네이버 블로그 검색을 기반으로 LLM 사용

LLM : command-r-plus [cohere] API(응답 생성) / GPT-4o [openai] API(검색 키워드 생성)

Embedding model : "BAAI/bge-m3"

Web demo : gradio(4.28)

With Naver Search API
```

## Data path
![image](https://github.com/Yusin-Lee/LLMwithNaverAPI/assets/98385516/97eeecd5-26fc-434e-803e-ac972ea369a1)
```
1. USER -> Gradio : 질문 입력 / BLOG, 지식인 검색 중 하나 선택

2. GPT-4 : 질문과 관련된 검색 키워드 추출

3-1 BLOG.
> 1. Naver Search API로 blog[10개] 검색, 결과[title, link, description] 추출
> 2. [질문 <-> description]을 임베딩 후 유사도 계산, 연관 높은 4개 블로그 본문 추출
> 3. [질문 <-> 본문]을 임베딩 후 유사도 계산, 연관 높은 2개 블로그 선택

3-2 지식인.
> 1. Naver Search API로 지식인[10개] 검색, 결과[title, link, description] 추출
> 2. [질문 <-> description]을 임베딩 후 유사도 계산, 연관 높은 2개 지식인 본문 추출
> 3. 지식인 본문 답변 중 길이가 가장 긴 답변 2개씩 채택[총 4개]
> 4. [질문 <-> 답변] 임베딩 후 유사도 계산, 연관 높은 2개 답변 선택

4. command-r-plus : 질문 + 블로그 본문을 프롬프트로 입력 및 응답

5. gradio : 응답 출력
```

## Deploy path
```
1. 네이버 블로그 본문 / 지식인 답변 크롤링 구현

2. command-r-plus / GPT-4 API 키 발급

3. Gradio 서버 구현
```

** command-r-plus는 1달 1,000건의 API콜 무료 / GPT-3.5 ~ GPT-4 사이 수준으로 여겨짐

** GPT-4o를 [질문 -> 검색키워드 생성]에 사용하는 이유는 해당 태스크에 대한 Input, Output token이 크지 않고, 질문을 요약하여 검색 키워드를 생성하는 것이 검색 정확도에 중요하기 때문

