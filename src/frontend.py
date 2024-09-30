import json
import gradio as gr
import requests

from llm.schemas import Question, ModelEnum


def send_request(question: str):
    url = "http://localhost:8000/generate_response"
    payload = Question(question=question,
                       model=ModelEnum.llama).model_dump()

    try:
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            response_json = response.json().get('response', 'No answer found.')
            return ' '.join(json.dumps(response_json, indent=4).replace('"', '').replace("\\n", " ").strip().split())
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Failed to connect: {e}"


iface = gr.Interface(
    fn=send_request,
    inputs=gr.Textbox(label="Your Question", placeholder="Ask a question..."),
    outputs=gr.Textbox(label="Response"),
    title="Chatbox"
)

iface.launch()
