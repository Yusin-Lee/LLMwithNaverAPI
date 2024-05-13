# LLMwithRAG_naverblog
네이버 블로그 검색을 기반으로 LLM 사용

LLM : command-r-plus [cohere] API(응답 생성) / GPT-4 [openai] API(검색 키워드 생성)

Embedding model : "BAAI/bge-m3"

Web demo : gradio(4.28)

With Naver Search API


Data path
1. USER -> Gradio : 질문 입력

2. GPT-4 : 질문과 관련된 검색 키워드 추출

3. Naver Search API로 blog[10개] 검색, 결과[title, link, description] 추출

4. [질문 <-> description]을 임베딩 후 유사도 계산, 연관 높은 4개 블로그 본문 추출

5. [질문 <-> 본문]을 임베딩 후 유사도 계산, 연관 높은 2개 블로그 선택

6. command-r-plus : 질문 + 블로그 본문을 프롬프트로 입력 및 응답

7. gradio : 응답 출력


Deploy path
1. 네이버 블로그 본문 크롤링 구현

2. command-r-plus / GPT-4 API 키 발급 및 python sdk 사용 방법 확인

3. Gradio 서버 구현

** command-r-plus는 1달 1,000건의 API콜 무료
** GPT-4를 [질문 -> 검색키워드 생성]에 사용하는 이유는 해당 태스크에서 Input, Output token이 크지 않고, 질문을 요약하여 검색 키워드를 생성하는 태스크가 중요하기 때문
