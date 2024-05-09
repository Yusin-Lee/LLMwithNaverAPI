# LLMwithRAG_naverblog
네이버 블로그 검색을 기반으로 LLM 사용

LLM : "QuantFactory/Meta-Llama-3-8B-Instruct-GGUF" with llama_cpp(0.2.64)

Embedding model : "BAAI/bge-m3"

Web demo : gradio(4.28)

With Naver Search API

Data path
1. USER -> Gradio : 질문 입력

2. LLM : 질문과 관련된 검색 키워드 추출

3. Naver Search API로 blog[10개] 검색, 결과[title, link, description, postdate] 추출

4. 질문과 description을 임베딩 후 유사도 계산, 연관 높은 N개 블로그 본문 추출

5. 질문 + 본문으로 프롬프트 구성 후 LLM에 입력

5. Gradio : 응답 출력


Deploy path
1. 네이버 블로그 본문 크롤링 구현

2. OpenAI compatible 서버 구현[llama-cpp & llama-3]

3. Gradio 서버 구현

** llama-cpp-python 설치 시, gpu 사용을 위해서 환경변수 설정이 필요할 수 있습니다.
** config로 llama-cpp서버 올리는 것은 https://llama-cpp-python.readthedocs.io/en/latest/server/#configuration-and-multi-model-support 를 참고하세요.
