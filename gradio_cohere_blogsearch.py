import gradio as gr
import cohere
from FlagEmbedding import BGEM3FlagModel
from datetime import timezone, timedelta
from config import Cohere_config
import naver_blog_scrap
import keyword_extract
KST = timezone(timedelta(hours=9))

crp_client = cohere.Client(Cohere_config.API_key) # command-r-plus api
model_name = "gpt-4-turbo-2024-04-09" # Keyword 생성용 모델 이름
emb_model = BGEM3FlagModel("BAAI/bge-m3",use_fp16=True,device = "cuda")
search_params = {"metric_type": "COSINE", "params": {}}

def answering_with_chatcomplate(prompt):
        # 질문으로 검색 키워드 생성
        keyword = keyword_extract.keyword_extract(prompt, model_name)
        print(keyword)

        # 질문과 관련된 블로그 본문 탐색
        _, link_list, desc_list = naver_blog_scrap.search_naver_blog(keyword)
        _, top_k_link = naver_blog_scrap.search_top_k(emb_model, prompt, desc_list, link_list, top_k=4, max_length=150)
        print(top_k_link)
        top_k_contents, top_k_titles = naver_blog_scrap.search_n_contents(top_k_link)
        final_contents, _, final_titles = naver_blog_scrap.search_top_k(emb_model, prompt, top_k_contents, top_k_link, top_k=2, max_length=512, title_list=top_k_titles)
        documents_1 = [{"title":final_titles[0], "text":final_contents[0]}]
        documents_2 = [{"title":final_titles[1], "text":final_contents[1]}]

        # cohere api 요청 및 응답 / 2개의 블로그 따로 사용
        preamble = "당신은 참고 문서에서 질문 관련 내용을 찾아 이를 바탕으로 질문에 대답하는 AI 모델입니다. 참고 문서로 블로그 글이 주어지며, 이는 질문과 관련있는 내용으로 이루어졌습니다. 질문과 참고 문서를 잘 읽고 올바른 대답을 하길 바랍니다. 만약 참고 문서가 질문과 연관이 없다면 `연관성이 부족한 참고문서입니다. 응답할 수 없습니다.`라고 대답하세요."
        output_1 = crp_client.chat(
                message = prompt,
                documents = documents_1, 
                preamble = preamble
                )

        output_2 = crp_client.chat(
                message = prompt,
                documents = documents_2, 
                preamble = preamble
                )
        return output_1.text, output_2.text, keyword, final_contents[0], final_contents[1]

demo = gr.Interface(
    fn=answering_with_chatcomplate,
    title = 'Command-r-plus',
    inputs = [gr.Textbox(label="질문")],
    outputs = [gr.Textbox(label="Answer 1"), gr.Textbox(label="Answer 2"), gr.Textbox(label="Ref Keyword"), gr.Textbox(label="Ref 1"), gr.Textbox(label="Ref 2")],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860) # share=True
