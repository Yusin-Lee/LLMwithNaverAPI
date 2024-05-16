import gradio as gr
import cohere
from FlagEmbedding import BGEM3FlagModel
from datetime import timezone, timedelta
from config import Cohere_config
import naver_blog_scrap
import naver_kin_scrap
import keyword_extract
KST = timezone(timedelta(hours=9))

crp_client = cohere.Client(Cohere_config.API_key)
model_name = "gpt-4o-2024-05-13"
emb_model = BGEM3FlagModel("BAAI/bge-m3",use_fp16=True,device = "cuda")
search_params = {"metric_type": "COSINE", "params": {}}

def answering_with_chatcomplate(search_type, prompt):
        # send prompt to extract search keyword
        keyword = keyword_extract.keyword_extract(prompt, model_name)
        print(keyword)
        # search blog related to keyword
        print(search_type)
        if search_type == 'BLOG':
                _, links, descs = naver_blog_scrap.search_naver_blog(keyword)
                _, top_k_link = naver_blog_scrap.search_top_k(emb_model, prompt, descs, links, top_k=4, max_length=150)
                top_k_contents, top_k_title = naver_blog_scrap.search_n_contents(top_k_link)
                final_contents, final_links, _ = naver_blog_scrap.search_top_k(emb_model, prompt, top_k_contents, top_k_link, top_k=2, max_length=512, title_list=top_k_title)
                preamble = "당신은 참고 문서에서 질문 관련 내용을 찾아 이를 바탕으로 질문에 대답하는 AI 모델입니다. 참고 문서로 네이버 블로그 글이 주어지며, 이는 질문과 관련있는 내용으로 이루어졌습니다. 질문과 참고 문서를 잘 읽고 올바른 대답을 하길 바랍니다. 만약 참고 문서가 질문과 연관이 없다면 `연관성이 부족한 참고문서입니다. 응답할 수 없습니다.`라고 대답하세요."
        elif search_type == 'KIN':
                _, _, links, descs = naver_kin_scrap.search_naver_kin(keyword)
                _, final_links = naver_kin_scrap.search_top_k(emb_model, prompt, descs, links, top_k=2, max_length=150)
                top_k_content = naver_kin_scrap.search_n_contents(top_k_link, top_k=2)
                final_contents = naver_kin_scrap.content_top_k_by_embedding(emb_model, prompt, top_k_content, top_k = 2, max_length=512)
                preamble = "당신은 참고 문서에서 질문 관련 내용을 찾아 이를 바탕으로 질문에 대답하는 AI 모델입니다. 참고 문서로 네이버 지식인 글이 주어지며, 이는 질문과 관련있는 내용으로 이루어졌습니다. 질문과 참고 문서를 잘 읽고 올바른 대답을 하길 바랍니다. 만약 참고 문서가 질문과 연관이 없다면 `연관성이 부족한 참고문서입니다. 응답할 수 없습니다.`라고 대답하세요."
        print(top_k_link)
        documents_1 = [{"title":'title 1', "text":final_contents[0]}]
        documents_2 = [{"title":'title 2', "text":final_contents[1]}]
        # Request to LLM server
        output_1 = crp_client.chat(
                message = prompt,
                documents = documents_1, 
                preamble = preamble,
                prompt_truncation='AUTO'
                )
        output_2 = crp_client.chat(
                message = prompt,
                documents = documents_2,
                preamble = preamble,
                prompt_truncation='AUTO'
                )
        return output_1.text, output_2.text, keyword, final_links[0], final_links[1]

search_type = ['BLOG','KIN']
demo = gr.Interface(
    fn=answering_with_chatcomplate,
    title = 'Command-r-plus',
    inputs = [gr.Dropdown(search_type, label = 'Search type'),gr.Textbox(label="질문")],
    outputs = [gr.Textbox(label="Answer 1"), gr.Textbox(label="Answer 2"), gr.Textbox(label="Ref Keyword"), gr.Textbox(label="Ref 1"), gr.Textbox(label="Ref 2")],
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860) # share=True
