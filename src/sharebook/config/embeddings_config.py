"""
Embeddings配置文件
提供统一的Embeddings配置管理，支持多种嵌入模型和API
"""

import os
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
import time
import hashlib
import json
from functools import lru_cache

# 加载环境变量
load_dotenv()

class EmbeddingsConfig(BaseModel):
    """Embeddings配置模型"""
    
    # 模型配置
    model_name: str = Field(
        default="BAAI/bge-large-zh-v1.5",
        description="嵌入模型名称"
    )
    
    api_base: str = Field(
        default="https://api.siliconflow.cn/v1",
        description="API基础URL"
    )
    
    api_key: str = Field(
        default_factory=lambda: os.getenv("EMBEDDINGS_API_KEY", "sk-iqontzqztzrhpbrqaihlmpmxmkuxqieamehtfmemaqipfxnu"),
        description="API密钥"
    )
    
    # 模型参数
    model_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="模型参数"
    )
    
    # 缓存配置
    cache_enabled: bool = Field(
        default=True,
        description="是否启用缓存"
    )
    
    cache_dir: Optional[str] = Field(
        default=None,
        description="缓存目录"
    )
    
    # 处理配置
    batch_size: int = Field(
        default=32,
        description="批处理大小"
    )
    
    timeout: int = Field(
        default=30,
        description="请求超时时间（秒）"
    )
    
    # 向量维度（根据模型自动设置）
    dimension: Optional[int] = Field(
        default=None,
        description="向量维度"
    )
    
    class Config:
        """Pydantic配置"""
        validate_assignment = True
        extra = "forbid"
    
    @validator('api_key')
    def validate_api_key(cls, v):
        """验证API密钥格式"""
        if not v:
            raise ValueError('API密钥不能为空')
        return v
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        """验证批处理大小"""
        if v <= 0 or v > 1000:
            raise ValueError('批处理大小必须在1-1000之间')
        return v
    
    @validator('timeout')
    def validate_timeout(cls, v):
        """验证超时设置"""
        if v <= 0 or v > 300:
            raise ValueError('超时时间必须在1-300秒之间')
        return v
    
    def get_model_dimension(self) -> int:
        """获取模型的向量维度"""
        # 已知模型的维度映射
        model_dimensions = {
            "BAAI/bge-large-zh-v1.5": 1024,
            "BAAI/bge-base-zh-v1.5": 768,
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }
        
        # 返回已知模型的维度
        if self.model_name in model_dimensions:
            return model_dimensions[self.model_name]
        
        # 默认返回1024
        return 1024
    
    def get_openai_kwargs(self) -> Dict[str, Any]:
        """获取OpenAI兼容的参数"""
        return {
            "model": self.model_name,
            "openai_api_base": self.api_base,
            "openai_api_key": self.api_key,
            "chunk_size": self.batch_size,
            "max_retries": 3,
            "request_timeout": self.timeout
        }


class VectorResult(BaseModel):
    """向量嵌入结果"""
    
    # 原始文本
    text: str = Field(description="原始文本")
    
    # 向量表示
    embedding: List[float] = Field(description="向量表示")
    
    # 模型信息
    model_used: str = Field(description="使用的模型")
    
    # 处理时间
    processing_time: float = Field(description="处理时间（秒）")
    
    # 向量维度
    dimension: int = Field(description="向量维度")
    
    # 元数据
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据"
    )
    
    @validator('embedding')
    def validate_embedding(cls, v, values):
        """验证向量嵌入"""
        if not v:
            raise ValueError('嵌入向量不能为空')
        
        # 检查维度一致性
        if 'dimension' in values and len(v) != values['dimension']:
            raise ValueError(f'嵌入向量维度必须为{values["dimension"]}')
        
        return v


class SimilarityResult(BaseModel):
    """相似度计算结果"""
    
    # 查询文本
    query_text: str = Field(description="查询文本")
    
    # 匹配文本
    match_text: str = Field(description="匹配文本")
    
    # 相似度分数
    similarity_score: float = Field(description="相似度分数")
    
    # 向量距离
    vector_distance: float = Field(description="向量距离")
    
    # 排名
    rank: int = Field(description="排名")
    
    # 匹配详情
    match_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="匹配详情"
    )
    
    @validator('similarity_score')
    def validate_similarity_score(cls, v):
        """验证相似度分数"""
        if not 0 <= v <= 1:
            raise ValueError('相似度分数必须在0-1之间')
        return v


# 全局配置实例
_config: Optional[EmbeddingsConfig] = None


def get_embeddings_config() -> EmbeddingsConfig:
    """获取全局Embeddings配置"""
    global _config
    if _config is None:
        _config = EmbeddingsConfig()
    return _config


def get_embeddings_kwargs() -> Dict[str, Any]:
    """获取OpenAI兼容的参数"""
    config = get_embeddings_config()
    return config.get_openai_kwargs()


def update_embeddings_config(**kwargs) -> None:
    """更新Embeddings配置"""
    global _config
    if _config is None:
        _config = EmbeddingsConfig()
    
    # 更新配置
    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"未知的配置项: {key}")


@lru_cache(maxsize=128)
def _get_config_hash() -> str:
    """获取配置的哈希值，用于缓存"""
    config = get_embeddings_config()
    config_str = json.dumps({
        "model_name": config.model_name,
        "api_base": config.api_base,
        "model_params": config.model_params,
    }, sort_keys=True)
    return hashlib.md5(config_str.encode()).hexdigest()


def get_embeddings() -> "BaseEmbeddings":
    """
    获取配置的Embeddings实例
    
    Returns:
        Embeddings实例
    """
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.embeddings import HuggingFaceEmbeddings
    
    config = get_embeddings_config()
    
    # 根据模型名称选择合适的Embeddings类
    if "openai" in config.model_name.lower() or config.api_base.endswith("openai.com"):
        # OpenAI模型
        embeddings = OpenAIEmbeddings(
            model=config.model_name,
            openai_api_base=config.api_base,
            openai_api_key=config.api_key,
            chunk_size=config.batch_size,
            max_retries=3,
            request_timeout=config.timeout
        )
    elif "siliconflow" in config.api_base.lower():
        # SiliconFlow API（兼容OpenAI格式）
        embeddings = OpenAIEmbeddings(
            model=config.model_name,
            openai_api_base=config.api_base,
            openai_api_key=config.api_key,
            chunk_size=config.batch_size,
            max_retries=3,
            request_timeout=config.timeout
        )
    else:
        # 本地HuggingFace模型
        embeddings = HuggingFaceEmbeddings(
            model_name=config.model_name,
            model_kwargs=config.model_params,
            encode_kwargs={"batch_size": config.batch_size},
            cache_folder=config.cache_dir
        )
    
    return embeddings


def embed_text(text: str, **kwargs) -> VectorResult:
    """
    嵌入单个文本
    
    Args:
        text: 要嵌入的文本
        **kwargs: 额外的配置参数
        
    Returns:
        VectorResult: 嵌入结果
    """
    start_time = time.time()
    
    # 获取embeddings实例
    embeddings = get_embeddings()
    
    # 执行嵌入
    embedding = embeddings.embed_query(text)
    
    # 计算处理时间
    processing_time = time.time() - start_time
    
    # 获取配置
    config = get_embeddings_config()
    
    # 创建结果
    result = VectorResult(
        text=text,
        embedding=embedding,
        model_used=config.model_name,
        processing_time=processing_time,
        dimension=len(embedding),
        metadata={
            "api_base": config.api_base,
            "batch_size": config.batch_size,
        }
    )
    
    return result


def embed_texts(texts: List[str], **kwargs) -> List[VectorResult]:
    """
    批量嵌入文本（优化版本）
    
    Args:
        texts: 要嵌入的文本列表
        **kwargs: 额外的配置参数
        
    Returns:
        List[VectorResult]: 嵌入结果列表
    """
    start_time = time.time()
    
    # 获取embeddings实例
    embeddings = get_embeddings()
    config = get_embeddings_config()
    
    # 性能优化：检查缓存
    cache_enabled = kwargs.get("cache_enabled", config.cache_enabled)
    if cache_enabled:
        cached_results = _check_cache(texts)
        if cached_results:
            return cached_results
    
    # 性能优化：动态调整批处理大小
    optimal_batch_size = _calculate_optimal_batch_size(len(texts), config.batch_size)
    
    # 分批处理大量文本
    if len(texts) > optimal_batch_size:
        embeddings_list = []
        for i in range(0, len(texts), optimal_batch_size):
            batch = texts[i:i + optimal_batch_size]
            batch_embeddings = embeddings.embed_documents(batch)
            embeddings_list.extend(batch_embeddings)
    else:
        embeddings_list = embeddings.embed_documents(texts)
    
    # 计算处理时间
    processing_time = time.time() - start_time
    
    # 创建结果列表
    results = []
    for i, (text, embedding) in enumerate(zip(texts, embeddings_list)):
        result = VectorResult(
            text=text,
            embedding=embedding,
            model_used=config.model_name,
            processing_time=processing_time / len(texts),  # 平均处理时间
            dimension=len(embedding),
            metadata={
                "api_base": config.api_base,
                "batch_size": optimal_batch_size,
                "batch_index": i,
                "total_batches": (len(texts) + optimal_batch_size - 1) // optimal_batch_size,
                "optimization_used": len(texts) > optimal_batch_size
            }
        )
        results.append(result)
    
    # 缓存结果
    if cache_enabled:
        _save_cache(texts, results)
    
    return results


def _calculate_optimal_batch_size(text_count: int, default_batch_size: int) -> int:
    """
    计算最优批处理大小
    
    Args:
        text_count: 文本数量
        default_batch_size: 默认批处理大小
        
    Returns:
        最优批处理大小
    """
    # 对于少量文本，使用默认批处理大小
    if text_count <= default_batch_size:
        return default_batch_size
    
    # 对于大量文本，使用较大的批处理大小
    # 但不超过API限制
    max_batch_size = 100
    optimal_size = min(default_batch_size * 2, max_batch_size)
    
    # 确保批次数不少于2次
    if text_count // optimal_size < 2:
        optimal_size = text_count // 2
    
    return optimal_size


_cache = {}

def _check_cache(texts: List[str]) -> Optional[List[VectorResult]]:
    """
    检查缓存
    
    Args:
        texts: 文本列表
        
    Returns:
        缓存的结果或None
    """
    # 生成缓存键
    cache_key = hashlib.md5("|".join(texts).encode()).hexdigest()
    
    # 检查缓存
    if cache_key in _cache:
        cached_time, cached_results = _cache[cache_key]
        # 缓存有效期1小时
        if time.time() - cached_time < 3600:
            return cached_results
        else:
            del _cache[cache_key]
    
    return None


def _save_cache(texts: List[str], results: List[VectorResult]) -> None:
    """
    保存结果到缓存
    
    Args:
        texts: 文本列表
        results: 嵌入结果
    """
    # 生成缓存键
    cache_key = hashlib.md5("|".join(texts).encode()).hexdigest()
    
    # 保存到缓存
    _cache[cache_key] = (time.time(), results)
    
    # 限制缓存大小
    if len(_cache) > 100:
        # 删除最旧的缓存项
        oldest_key = min(_cache.keys(), key=lambda k: _cache[k][0])
        del _cache[oldest_key]


def calculate_similarity(
    text1: str, 
    text2: str, 
    metric: str = "cosine"
) -> SimilarityResult:
    """
    计算两个文本的相似度
    
    Args:
        text1: 第一个文本
        text2: 第二个文本
        metric: 相似度度量方法 ("cosine", "euclidean", "manhattan")
        
    Returns:
        SimilarityResult: 相似度结果
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances, manhattan_distances
    
    # 嵌入文本
    result1 = embed_text(text1)
    result2 = embed_text(text2)
    
    # 转换为numpy数组
    emb1 = np.array(result1.embedding).reshape(1, -1)
    emb2 = np.array(result2.embedding).reshape(1, -1)
    
    # 计算相似度/距离
    if metric == "cosine":
        similarity = cosine_similarity(emb1, emb2)[0][0]
        distance = 1 - similarity
    elif metric == "euclidean":
        distance = euclidean_distances(emb1, emb2)[0][0]
        # 将欧几里得距离转换为相似度（使用高斯核）
        similarity = np.exp(-distance / np.linalg.norm(result1.embedding))
    elif metric == "manhattan":
        distance = manhattan_distances(emb1, emb2)[0][0]
        # 将曼哈顿距离转换为相似度
        similarity = 1 / (1 + distance)
    else:
        raise ValueError(f"不支持的相似度度量方法: {metric}")
    
    # 创建结果
    result = SimilarityResult(
        query_text=text1,
        match_text=text2,
        similarity_score=float(similarity),
        vector_distance=float(distance),
        rank=1,
        match_details={
            "metric": metric,
            "model_used": result1.model_used,
            "dimension": result1.dimension,
        }
    )
    
    return result


if __name__ == "__main__":
    # 测试配置
    config = get_embeddings_config()
    print(f"当前配置:")
    print(f"  模型: {config.model_name}")
    print(f"  API: {config.api_base}")
    print(f"  批处理大小: {config.batch_size}")
    print(f"  向量维度: {config.get_model_dimension()}")
    
    # 测试嵌入
    test_text = "这是一个测试文本"
    result = embed_text(test_text)
    print(f"\n嵌入结果:")
    print(f"  文本: {result.text}")
    print(f"  维度: {result.dimension}")
    print(f"  处理时间: {result.processing_time:.3f}秒")
    print(f"  前5个值: {result.embedding[:5]}")
    
    # 测试相似度
    text1 = "机器学习是人工智能的一个分支"
    text2 = "深度学习属于机器学习领域"
    sim_result = calculate_similarity(text1, text2)
    print(f"\n相似度结果:")
    print(f"  文本1: {sim_result.query_text}")
    print(f"  文本2: {sim_result.match_text}")
    print(f"  相似度: {sim_result.similarity_score:.4f}")
    print(f"  距离: {sim_result.vector_distance:.4f}")