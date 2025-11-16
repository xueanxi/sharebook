"""
ComfyUI工具类使用示例
"""

from src.utils.comfyui_wrapper import ComfyUIWrapper
import os

def example_usage():
    """使用ComfyUIWrapper生成图像的示例"""
    
    # 初始化ComfyUI连接
    with ComfyUIWrapper(server_address="127.0.0.1:8188") as comfy:
        # 加载工作流模板
        workflow = comfy.load_workflow_template("comfyui/novel_t2I_flux.json")
        
        # 更新工作流参数
        comfy.update_workflow_text(
            workflow, 
            "1", 
            "Animation style,With white eyebrows and long beard, a slender face, deep-set eyes, a thin figure but a composed demeanor, exuding a touch of the air of a celestial being. A plain long robe with cloud patterns embroidered on the cuffs, a jade belt around the waist and cloth shoes on the feet, the overall look is simple yet extraordinary."
        )
        comfy.update_workflow_batch_size(workflow, "9", 1)
        
        # 生成图像
        save_dir = "data/characters/image"
        output_images = comfy.generate_images(workflow, save_dir=save_dir)
        
        print(f"生成的图像: {output_images}")

if __name__ == "__main__":
    example_usage()