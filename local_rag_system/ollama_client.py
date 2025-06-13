"""Ollama客户端模块"""

import ollama
from typing import List, Optional
from config import EMBEDDING_MODEL, GENERATION_MODEL


class OllamaClient:
    """Ollama客户端"""
    
    def __init__(self):
        self.embedding_model = EMBEDDING_MODEL
        self.generation_model = GENERATION_MODEL
    
    def check_service(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            test_response = ollama.list()
            print("Ollama服务连接正常")
            
            models = self._get_installed_models(test_response)
            print(f"已安装的模型: {models}")
            
            # 检查嵌入模型
            if not self._check_embedding_model(models):
                return False
            
            # 检查生成模型
            self._check_generation_model(models)
            
            return True
            
        except Exception as e:
            print(f"Ollama服务连接失败: {e}")
            print("请确保:")
            print("1. Ollama服务正在运行 (ollama serve)")
            print("2. 模型已下载")
            print("3. 服务监听在正确端口")
            return False
    
    def _get_installed_models(self, response) -> List[str]:
        """获取已安装的模型列表"""
        models = []
        try:
            if hasattr(response, 'models') and response.models:
                for model in response.models:
                    if hasattr(model, 'model'):
                        models.append(model.model)
        except Exception as e:
            print(f"模型检查时出错: {e}")
        
        return models
    
    def _check_embedding_model(self, models: List[str]) -> bool:
        """检查嵌入模型是否存在"""
        embed_models = [m for m in models if 'nomic-embed-text' in m]
        if not embed_models:
            print("警告: 未找到 nomic-embed-text 模型")
            print("请运行: ollama pull nomic-embed-text")
            return False
        else:
            print(f"找到嵌入模型: {embed_models[0]}")
            return True
    
    def _check_generation_model(self, models: List[str]) -> None:
        """检查生成模型是否存在"""
        deepseek_models = [m for m in models if 'deepseek-r1' in m]
        if deepseek_models:
            print(f"找到生成模型: {deepseek_models[0]}")
        else:
            print("警告: 未找到 deepseek-r1 模型，将在生成回答时处理")
    
    def generate_response(self, prompt: str) -> str:
        """生成回答"""
        try:
            print("正在生成回答...")
            # 使用更严格的参数减少幻觉
            response = ollama.generate(
                model=self.generation_model, 
                prompt=prompt,
                options={
                    'temperature': 0.1,  # 降低随机性
                    'top_p': 0.8,       # 限制词汇选择范围
                    'repeat_penalty': 1.1,  # 减少重复
                    'num_predict': 500,     # 限制输出长度
                }
            )
            return response['response']
        except Exception as e:
            print(f"生成回答失败: {e}")
            print(f"请检查模型 '{self.generation_model}' 是否已下载")
            raise
