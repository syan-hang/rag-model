"""向量存储模块"""

import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from typing import List, Dict, Any
from config import (
    CHROMA_DB_PATH, 
    COLLECTION_NAME, 
    OLLAMA_EMBEDDINGS_URL, 
    EMBEDDING_MODEL,
    MAX_RESULTS,
    MIN_SIMILARITY_THRESHOLD,
    MAX_CHUNK_SIZE,
    FALLBACK_TO_ALL_DOCS,
    FALLBACK_LIMIT
)


class VectorStore:
    """向量存储管理器"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.embedding_function = OllamaEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            url=OLLAMA_EMBEDDINGS_URL
        )
        self.collection = None
        self._initialize_collection()
    
    def _initialize_collection(self):
        """初始化集合"""
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_function
        )
        print("集合已准备就绪")
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        return self.collection.count()
    
    def need_update(self, current_hash: str) -> bool:
        """检查是否需要更新数据"""
        try:
            metadata = self.collection.get(ids=["data_hash"])
            if metadata['metadatas'] and len(metadata['metadatas']) > 0:
                stored_hash = metadata['metadatas'][0].get('hash')
                return stored_hash != current_hash
            return True
        except:
            return True
    
    def _clean_document(self, doc: str) -> str:
        """最小化清理文档内容，保持信息完整性"""
        import re
        
        # 只进行最基本的清理
        # 移除不可见的控制字符
        doc = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', doc)
        
        # 规范化空白字符
        doc = re.sub(r'\s+', ' ', doc).strip()
        
        # 降低最小长度要求以适应细粒度切割
        if len(doc) < 5:
            return ""
        
        # 使用配置的最大块大小
        if len(doc) > MAX_CHUNK_SIZE * 2:  # 允许稍微超出配置大小
            doc = doc[:MAX_CHUNK_SIZE * 2] + "..."
            
        return doc
    
    def add_documents(self, documents: List[str], data_hash: str) -> bool:
        """添加文档到向量存储"""
        try:
            print(f"开始向量化 {len(documents)} 个文档...")
            
            # 预处理文档
            valid_documents = []
            for i, doc in enumerate(documents):
                cleaned_doc = self._clean_document(doc)
                if cleaned_doc:
                    valid_documents.append((i, cleaned_doc))
            
            print(f"有效文档数: {len(valid_documents)}")
            
            # 显示前几个文档内容用于调试
            for i, (original_idx, doc) in enumerate(valid_documents[:3]):
                print(f"文档 {i+1} 预览: {doc[:80]}...")
            
            # 逐个添加文档以避免批处理错误
            successful_count = 0
            for i, (original_idx, doc) in enumerate(valid_documents):
                try:
                    self.collection.add(
                        documents=[doc],
                        ids=[str(original_idx)]
                    )
                    successful_count += 1
                    
                    if (i + 1) % 10 == 0:  # 每10个文档打印一次进度
                        print(f"已处理 {i + 1}/{len(valid_documents)} 个文档")
                        
                except Exception as e:
                    print(f"添加文档 {original_idx+1} 失败: {e}")
                    # 尝试进一步清理
                    try:
                        super_clean_doc = re.sub(r'[^\u4e00-\u9fff\w\s]', ' ', doc)
                        super_clean_doc = re.sub(r'\s+', ' ', super_clean_doc).strip()
                        if len(super_clean_doc) > 5:
                            self.collection.add(
                                documents=[super_clean_doc],
                                ids=[str(original_idx)]
                            )
                            successful_count += 1
                            print(f"文档 {original_idx+1} 深度清理后重试成功")
                    except Exception as retry_e:
                        print(f"文档 {original_idx+1} 深度清理重试失败: {retry_e}")
                        continue
            
            # 存储数据哈希值
            try:
                self.collection.add(
                    documents=["data_hash"],
                    metadatas=[{"hash": data_hash}],
                    ids=["data_hash"]
                )
            except Exception as e:
                print(f"存储哈希值失败: {e}")
            
            print(f"成功添加 {successful_count}/{len(documents)} 个文档到向量数据库")
            return successful_count > 0
            
        except Exception as e:
            print(f"添加文档失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_documents(self, documents: List[str], data_hash: str) -> bool:
        """更新文档"""
        try:
            print("开始更新文档...")
            # 清空现有数据
            all_ids = self.collection.get()['ids']
            if all_ids:
                self.collection.delete(ids=all_ids)
                print("已清空旧数据")
            
            # 添加新数据
            if documents:
                return self.add_documents(documents, data_hash)
            return True
        except Exception as e:
            print(f"更新数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def query(self, query: str, n_results: int = MAX_RESULTS) -> List[str]:
        """查询相关文档"""
        try:
            print(f"开始查询: {query}")
            print(f"请求返回 {n_results} 个相关文档")
            
            # 检查集合中的总文档数
            total_docs = self.collection.count()
            print(f"集合中总文档数: {total_docs}")
            
            # 对于细粒度切割，可能需要更多文档来获得完整信息
            actual_results = min(n_results * 2, total_docs - 1)  # 增加查询数量
            
            query_embedding = self.embedding_function([query])
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=actual_results
            )
            
            documents = results['documents'][0]
            distances = results.get('distances', [None])[0] if 'distances' in results else [None] * len(documents)
            
            print(f"查询完成，原始返回 {len(documents)} 个文档")
            
            # 过滤掉data_hash文档并应用相似度过滤
            filtered_results = []
            for doc, distance in zip(documents, distances):
                if doc != "data_hash":
                    similarity = 1 - distance if distance is not None else 1.0
                    
                    # 对细粒度文档使用更宽松的阈值
                    adjusted_threshold = MIN_SIMILARITY_THRESHOLD * 0.8
                    if similarity >= adjusted_threshold:
                        filtered_results.append((doc, similarity))
                        print(f"相似度: {similarity:.3f} - {doc[:60]}...")
                    else:
                        print(f"相似度过低({similarity:.3f})，已过滤: {doc[:40]}...")
            
            # 按相似度排序
            filtered_results.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前N个最相关的文档
            final_documents = [doc for doc, similarity in filtered_results[:n_results]]
            
            print(f"经过相似度过滤后返回 {len(final_documents)} 个有效文档")
            
            # 如果没有找到任何匹配的文档，启用兜底策略
            if len(final_documents) == 0 and FALLBACK_TO_ALL_DOCS:
                print("未找到匹配文档，启用兜底策略：查询所有文档")
                return self._fallback_query_all_docs()
            
            # 如果文档太少，进一步降低阈值
            if len(final_documents) < 3:
                print("文档数量不足，进一步降低阈值...")
                additional_docs = []
                for doc, distance in zip(documents, distances):
                    if doc != "data_hash" and doc not in final_documents:
                        similarity = 1 - distance if distance is not None else 1.0
                        if similarity >= 0.05:  # 非常低的阈值
                            additional_docs.append(doc)
                
                final_documents.extend(additional_docs[:max(0, 5 - len(final_documents))])
                print(f"最终返回 {len(final_documents)} 个文档")
                
                # 如果仍然没有文档且启用兜底策略
                if len(final_documents) == 0 and FALLBACK_TO_ALL_DOCS:
                    print("降低阈值后仍无文档，启用兜底策略：查询所有文档")
                    return self._fallback_query_all_docs()
            
            return final_documents
            
        except Exception as e:
            print(f"查询失败: {e}")
            # 如果查询出错且启用兜底策略，返回所有文档
            if FALLBACK_TO_ALL_DOCS:
                print("查询异常，启用兜底策略：返回所有文档")
                return self._fallback_query_all_docs()
            raise
    
    def _fallback_query_all_docs(self) -> List[str]:
        """兜底策略：返回所有文档（排除系统文档）"""
        try:
            print("执行兜底查询：获取所有文档")
            
            # 获取所有文档
            all_results = self.collection.get()
            all_documents = all_results.get('documents', [])
            
            # 过滤掉系统文档
            filtered_docs = [doc for doc in all_documents if doc != "data_hash"]
            
            # 限制返回数量
            limited_docs = filtered_docs[:FALLBACK_LIMIT]
            
            print(f"兜底查询返回 {len(limited_docs)} 个文档（总计 {len(filtered_docs)} 个可用文档）")
            
            # 显示前几个文档的预览
            for i, doc in enumerate(limited_docs[:3]):
                print(f"兜底文档 {i+1}: {doc[:60]}...")
            
            return limited_docs
            
        except Exception as e:
            print(f"兜底查询失败: {e}")
            return []
