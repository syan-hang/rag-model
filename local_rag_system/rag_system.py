"""主RAG系统"""

from typing import List
from data_loader import DataLoader
from ollama_client import OllamaClient
from vector_store import VectorStore
from config import DEFAULT_QUERY, STRICT_ANSWER_PROMPT, NO_INFO_RESPONSE, FALLBACK_TO_ALL_DOCS, FALLBACK_LIMIT


class RAGSystem:
    """RAG系统主类"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.ollama_client = OllamaClient()
        self.vector_store = VectorStore()
    
    def initialize(self) -> bool:
        """初始化系统"""
        # 检查Ollama服务
        if not self.ollama_client.check_service():
            return False
        
        # 加载数据
        all_content, documents = self.data_loader.load_from_folder()
        if not documents:
            print("无法加载数据")
            return False
        
        # 计算数据哈希
        current_hash = self.data_loader.get_folder_hash()
        
        # 检查是否需要更新数据
        existing_count = self.vector_store.get_document_count()
        print(f"集合中现有文档数量: {existing_count}")
        
        if existing_count == 0:
            print("集合为空，开始添加文档到向量数据库...")
            if not self.vector_store.add_documents(documents, current_hash):
                return False
        elif self.vector_store.need_update(current_hash):
            print("检测到数据已更新，重新加载数据...")
            if not self.vector_store.update_documents(documents, current_hash):
                return False
        else:
            print("数据未发生变化，跳过添加步骤")
        
        return True
    
    def query(self, question: str = DEFAULT_QUERY) -> str:
        """查询并生成回答"""
        try:
            # 查询相关文档
            related_documents = self.vector_store.query(question)
            
            if not related_documents:
                return NO_INFO_RESPONSE
            
            # 过滤掉系统文档
            filtered_documents = [doc for doc in related_documents if doc != "data_hash"]
            
            if not filtered_documents:
                return NO_INFO_RESPONSE
            
            # 如果文档数量很多（可能是兜底查询），给出提示
            if len(filtered_documents) > 20:
                print(f"检索到大量文档({len(filtered_documents)}个)，可能使用了兜底查询策略")
                # 可以选择截取部分文档以避免上下文过长
                filtered_documents = filtered_documents[:30]
                print(f"截取前{len(filtered_documents)}个文档进行分析")
            
            # 构建严格的上下文和提示
            context = "\n".join(filtered_documents)
            
            # 如果上下文过长，进行智能截取
            if len(context) > 8000:  # 限制上下文长度
                print("上下文过长，进行智能截取...")
                # 优先保留包含查询关键词的文档
                prioritized_docs = self._prioritize_documents(filtered_documents, question)
                context = "\n".join(prioritized_docs[:20])
                print(f"截取后上下文长度: {len(context)} 字符")
            
            prompt = STRICT_ANSWER_PROMPT.format(context=context, question=question)
            
            # 生成回答
            try:
                answer = self.ollama_client.generate_response(prompt)
                
                # 后处理：检查回答是否包含明显的幻觉标识
                if any(phrase in answer.lower() for phrase in [
                    "我不知道", "无法确定", "文档中没有", "没有相关信息", 
                    "不确定", "无法回答"
                ]):
                    return answer
                else:
                    # 在回答前添加提醒
                    return f"基于文档内容的回答：\n\n{answer}\n\n注意：以上回答仅基于提供的文档内容。"
                    
            except Exception:
                # 如果生成失败，返回基础信息
                return f"无法生成智能回答，以下是相关文档原文：\n\n{context[:2000]}..."
            
        except Exception as e:
            print(f"查询过程失败: {e}")
            return "查询失败，请检查系统状态"
    
    def _prioritize_documents(self, documents: List[str], question: str) -> List[str]:
        """根据问题关键词优先排序文档"""
        import re
        
        # 提取问题中的关键词
        keywords = re.findall(r'[\u4e00-\u9fff]+|\w+', question.lower())
        keywords = [k for k in keywords if len(k) > 1]
        
        # 计算每个文档的关键词匹配分数
        scored_docs = []
        for doc in documents:
            score = 0
            doc_lower = doc.lower()
            for keyword in keywords:
                score += doc_lower.count(keyword)
            scored_docs.append((doc, score))
        
        # 按分数排序
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored_docs]

    def interactive_chat(self):
        """交互式聊天模式"""
        print("\n=== 进入交互式问答模式 ===")
        print("输入 'quit' 或 'exit' 退出程序")
        print("=" * 40)
        
        while True:
            try:
                # 获取用户输入
                user_input = input("\n请输入您的问题: ").strip()
                
                # 检查退出条件
                if user_input.lower() in ['quit', 'exit', 'q', '退出']:
                    print("\n谢谢使用，再见！")
                    break
                
                # 检查空输入
                if not user_input:
                    print("请输入有效的问题")
                    continue
                
                # 执行查询
                print("\n正在处理您的问题...")
                result = self.query(user_input)
                
                # 输出结果
                print("\n" + "=" * 40)
                print("回答:")
                print(result)
                print("=" * 40)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"\n处理问题时出错: {e}")
                print("请重试或输入 'quit' 退出")


def main():
    """主函数"""
    print("=== RAG系统启动 ===")
    
    # 创建RAG系统
    rag = RAGSystem()
    
    # 初始化系统
    if not rag.initialize():
        print("系统初始化失败")
        return
    
    print("\n系统初始化成功！")
    
    # 进入交互式模式
    rag.interactive_chat()


if __name__ == "__main__":
    main()