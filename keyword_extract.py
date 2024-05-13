from config import Openai_config
from openai import OpenAI
llm_client = OpenAI(api_key=Openai_config.API_key)

# LLM 활용하여 질문 -> 검색 키워드로 변경
def keyword_extract(question, model_name):
    completion = llm_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "당신의 역할은 질문과 관련된 검색 문장을 생성하는 것입니다. 검색 문장은 구글 검색을 위해 사용되며, 적절한 검색 문장을 사용해야 유저는 올바른 정보를 얻을 수 있습니다. 5단어 이하의 문장 혹은 단어로 요약하여 검색 문장만 응답하세요. 항상 한국어로만 응답하고, 한자어 대신 한글 용어 사용을 주로 해주세요."},
                    {"role": "user", "content": f"{question}"}
                ],
                seed=42,
                temperature=0.7,
                max_tokens = 512
                )
    return completion.choices[0].message.content.replace('"','').replace("'","")
