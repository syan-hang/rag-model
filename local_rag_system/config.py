"""配置文件"""

# 数据配置
DATA_FOLDER = "data"
SUPPORTED_EXTENSIONS = ['.txt', '.md', '.csv', '.tsv', '.docx']

# ChromaDB配置
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "user_data"

# Ollama配置
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_EMBEDDINGS_URL = f"{OLLAMA_BASE_URL}/api/embeddings"
EMBEDDING_MODEL = "nomic-embed-text:latest"
GENERATION_MODEL = "deepseek-r1:7b"

# 查询配置
DEFAULT_QUERY = "查询李四的数据"
MAX_RESULTS = 150  # 增加查询结果数量以适应更细切割
MIN_SIMILARITY_THRESHOLD = 0.15  # 降低相似度阈值
ENABLE_SIMILARITY_FILTER = True  # 启用相似度过滤
FALLBACK_TO_ALL_DOCS = True  # 当匹配度过低时，返回所有文档
FALLBACK_LIMIT = 50  # 兜底查询时的最大文档数量

# 文档切割配置
MAX_CHUNK_SIZE = 50   # 大幅减小单个文档片段的最大长度
MIN_CHUNK_SIZE = 10    # 降低最小文档片段长度
OVERLAP_SIZE = 10      # 减小文档片段重叠长度
MERGE_SHORT_LINES = False  # 不合并短行，保持细粒度
PRESERVE_PARAGRAPHS = False  # 不强制保持段落完整性
SENTENCE_SPLIT = True  # 启用句子级别切割

# 提示词配置
STRICT_ANSWER_PROMPT = """请严格基于以下提供的文档内容回答问题，不要添加任何文档中没有的信息。

文档内容：
{context}

问题：{question}

回答要求：
1. 只能使用上述文档中的信息进行回答
2. 如果文档中没有相关信息，请明确说明"文档中没有相关信息"
3. 不要推测、猜测或添加文档外的信息
4. 如果信息不完整，请说明哪些信息缺失
5. 回答要准确、简洁、直接
6. 引用具体的文档内容支持你的回答

回答："""

NO_INFO_RESPONSE = "抱歉，在提供的文档中没有找到相关信息。"

# 文本处理配置
PRESERVE_URLS = True  # 是否保护URL链接
PRESERVE_EMAIL = True  # 是否保护邮箱地址
PRESERVE_SPECIAL_CHARS = [':/', '://', 'http', 'https', 'ftp', '@', '.com', '.cn', '.org', '.net']  # 需要保护的特殊字符
MINIMAL_FILTERING = True  # 使用最小化过滤，只移除明显的控制字符
PRESERVE_ORIGINAL_TEXT = True  # 尽可能保持原始文本
