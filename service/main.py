import os
import uvicorn
import json
import traceback
import uuid
import argparse

from os.path import abspath, dirname
from loguru import logger
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from message_store import MessageStore
from transformers import AutoModel, AutoTokenizer
from errors import Errors


log_folder = os.path.join(abspath(dirname(__file__)), "log")
logger.add(os.path.join(log_folder, "{time}.log"), level="INFO")


DEFAULT_DB_SIZE = 100000

massage_store = MessageStore(db_path="message_store.json", table_name="chatgpt", max_size=DEFAULT_DB_SIZE)
# Timeout for FastAPI
# service_timeout = None

app = FastAPI()


stream_response_headers = {
    "Content-Type": "application/octet-stream",
    "Cache-Control": "no-cache",
}


@app.post("/config")
async def config():
    return JSONResponse(content=dict(
        message=None,
        status="Success",
        data=dict()
    ))



async def process(prompt, options, params, message_store, history=None):
    """
    发文字消息
    """
    # 不能是空消息
    if not prompt:
        logger.error("Prompt is empty.")
        yield Errors.PROMPT_IS_EMPTY.value
        return


    try:
        chat = {"role": "user", "content": prompt}

        # 组合历史消息
        if options:
            parent_message_id = options.get("parentMessageId")
            messages = message_store.get_from_key(parent_message_id)
            if messages:
                messages.append(chat)
            else:
                messages = []
        else:
            parent_message_id = None
            messages = [chat]

        # 记忆
        messages = messages[-params['memory_count']:]


        history_formatted = []
        if options is not None:
            history_formatted = []
            tmp = []
            for i, old_chat in enumerate(messages):
                if len(tmp) == 0 and old_chat['role'] == "user":
                    tmp.append(old_chat['content'])
                elif old_chat['role'] == "AI":
                    tmp.append(old_chat['content'])
                    history_formatted.append(tuple(tmp))
                    tmp = []
                else:
                    continue

        uid = "chatglm"+uuid.uuid4().hex
        for response, history in model.stream_chat(tokenizer, prompt, history_formatted, max_length=params['max_length'], 
                                                    top_p=params['top_p'], temperature=params['temperature']):
            message = json.dumps(dict(
                role="AI",
                id=uid,
                parentMessageId=parent_message_id,
                text=response,
            ))
            yield "data: " + message

    except:
        err = traceback.format_exc()
        logger.error(err)
        yield Errors.SOMETHING_WRONG.value
        return

    try:
        # save to cache
        chat = {"role": "AI", "content": response}
        messages.append(chat)

        parent_message_id = uid
        message_store.set(parent_message_id, messages)
    except:
        err = traceback.format_exc()
        logger.error(err)


@app.post("/chat-process")
async def chat_process(request_data: dict):
    prompt = request_data['prompt']
    max_length = request_data['max_length']
    top_p = request_data['top_p']
    temperature = request_data['temperature']
    options = request_data['options']
    if request_data['memory'] == 1 :
        memory_count = 5
    elif request_data['memory'] == 50:
        memory_count = 20
    else:
        memory_count = 999

    if 1 == request_data["top_p"]:
        top_p = 0.2
    elif 50 == request_data["top_p"]:
        top_p = 0.5
    else:
        top_p = 0.9
    if temperature is None:
        temperature = 0.9
    if top_p is None:
        top_p = 0.7
    params = {
        "max_length": max_length,
        "top_p": top_p,
        "temperature": temperature,
        "memory_count": memory_count
    }
    answer_text = process(prompt, options, params, massage_store)
    return StreamingResponse(content=answer_text, headers=stream_response_headers, media_type="text/event-stream")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simple API server for ChatGLM-6B')
    parser.add_argument('--device', '-d', help='使用设备，cpu或cuda:0等', default='cpu')
    parser.add_argument('--quantize', '-q', help='量化等级。可选值：16，8，4', default=16)
    parser.add_argument('--host', '-H', type=str, help='监听Host', default='0.0.0.0')
    parser.add_argument('--port', '-P', type=int, help='监听端口号', default=3002)
    args = parser.parse_args()
    model_name = "THUDM/chatglm-6b"
    quantize = int(args.quantize)
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
    model = None
    if args.device == 'cpu':
        if quantize == 8:
            print('cpu模式下量化等级只能是16或4，使用4')
            model_name = "THUDM/chatglm-6b-int4"
        elif quantize == 4:
            model_name = "THUDM/chatglm-6b-int4"
        model = AutoModel.from_pretrained(model_name, trust_remote_code=True).float()
    else:
        if quantize == 16:
            model = AutoModel.from_pretrained(model_name, trust_remote_code=True).half().cuda()
        else:
            model = AutoModel.from_pretrained(model_name, trust_remote_code=True).half().quantize(quantize).cuda()
    model = model.eval()

    uvicorn.run(app, host=args.host, port=args.port)
