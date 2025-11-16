"""
测试Agent日志输出
"""

import websocket
import uuid
import json
import urllib.request
import urllib.parse
import os

server_address = "127.0.0.1:8188"  # 请根据您的ComfyUI服务地址修改
save_image_dir="d:\\work\\code\\python\\sharebook2\\data\\characters\\image"
batch_size = 1
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    """向ComfyUI服务器提交任务"""
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"http://{server_address}/prompt", data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_history(prompt_id):
    """获取任务历史"""
    with urllib.request.urlopen(f"http://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

def get_image(filename, subfolder, image_type):
    """获取图片数据"""
    data = {"filename": filename, "subfolder": subfolder, "type": image_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen(f"http://{server_address}/view?{url_values}") as response:
        return response.read()

def get_images(ws, prompt, save_dir="data/characters/image"):
    """获取图片并保存到指定目录"""
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                # 当收到执行完成的消息时，退出循环
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break
    # 任务完成后，查询历史并获取图片
    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                
                # 确保保存目录存在
                os.makedirs(save_dir, exist_ok=True)
                
                # 保存图片到指定目录
                image_path = os.path.join(save_dir, image['filename'])
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # 记录保存的图片路径
                output_images[image['filename']] = image_path
                print(f"图片已保存到: {image_path}")
    
    return output_images

# 加载API工作流模板
with open(r"comfyui\novel_t2I_flux.json", "r", encoding="utf-8") as f:
    prompt_data = json.load(f)

# 动态修改参数
prompt_data["1"]["inputs"]["text"] = "Animation style,With white eyebrows and long beard, a slender face, deep-set eyes, a thin figure but a composed demeanor, exuding a touch of the air of a celestial being. A plain long robe with cloud patterns embroidered on the cuffs, a jade belt around the waist and cloth shoes on the feet, the overall look is simple yet extraordinary."
prompt_data["9"]["inputs"]["batch_size"] = batch_size


# 建立WebSocket连接并提交任务
ws = websocket.WebSocket()
ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
images = get_images(ws, prompt_data, save_dir=save_image_dir)
ws.close()