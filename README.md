# 本地RAG系统

一个基于本地Ollama模型和ChromaDB向量数据库的检索增强生成（RAG）系统，支持多种文档格式的智能问答。

## 功能特性

- ✅ **多格式文档支持**：支持 .txt、.md、.csv、.tsv、.docx 文件格式
- ✅ **智能文档切割**：细粒度文档分割，保持语义完整性
- ✅ **向量化存储**：使用ChromaDB进行高效向量存储和检索
- ✅ **相似度过滤**：智能相似度匹配，兜底查询机制
- ✅ **交互式问答**：支持持续对话，实时切换模型
- ✅ **本地化部署**：完全本地运行，数据安全可控
- ✅ **链接保护**：保护文档中的URL链接和重要信息
- ✅ **增量更新**：自动检测文档变化，增量更新向量库

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据加载器     │    │   向量存储      │    │   模型客户端    │
│  DataLoader     │    │  VectorStore    │    │ OllamaClient    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   RAG系统核心   │
                    │   RAGSystem     │
                    └─────────────────┘
```

## 环境要求

### 必需软件
- Python 3.8+
- Ollama (用于本地模型服务)

### Python依赖
```bash
pip install ollama chromadb python-docx
```

### 模型要求
```bash
# 安装嵌入模型
ollama pull nomic-embed-text

# 安装生成模型
ollama pull deepseek-r1:7b
```

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd local_rag_system
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 启动Ollama服务
```bash
ollama serve
```

### 4. 准备数据
将文档文件放入 `data/` 文件夹中：
```
data/
├── document1.docx
├── document2.txt
├── document3.md
└── ...
```

### 5. 运行系统
```bash
python rag_system.py
```

## 配置说明

主要配置项位于 `config.py` 文件中：

### 数据配置
```python
DATA_FOLDER = "data"  # 数据文件夹路径
SUPPORTED_EXTENSIONS = ['.txt', '.md', '.csv', '.tsv', '.docx']  # 支持的文件格式
```

### 模型配置
```python
EMBEDDING_MODEL = "nomic-embed-text:latest"  # 嵌入模型
GENERATION_MODEL = "deepseek-r1:7b"  # 生成模型
```

### 查询配置
```python
MAX_RESULTS = 150  # 最大检索结果数
MIN_SIMILARITY_THRESHOLD = 0.15  # 最小相似度阈值
FALLBACK_TO_ALL_DOCS = True  # 启用兜底查询
```

### 文档切割配置
```python
MAX_CHUNK_SIZE = 50  # 最大文档片段长度
MIN_CHUNK_SIZE = 10  # 最小文档片段长度
SENTENCE_SPLIT = True  # 启用句子级切割
```

## 使用指南

### 基础使用
1. 启动系统后进入交互式问答模式
2. 输入问题，系统会基于文档内容回答
3. 输入 `quit` 或 `exit` 退出系统

### 高级功能
- **模式切换**：输入 `switch` 切换不同的模型
- **查看模式**：输入 `mode` 查看当前使用的模型
- **实时更新**：修改data文件夹中的文档后，系统会自动检测并更新

### 示例对话
```
请输入您的问题: 查询李四的数据

回答:
基于文档内容的回答：

根据文档信息，李四的数据如下：
- 年龄：30岁
- 手机号：13900139000
- 地址：上海市浦东新区陆家嘴

注意：以上回答仅基于提供的文档内容。
```

## 项目结构

```
local_rag_system/
├── rag_system.py          # 主程序入口
├── config.py              # 配置文件
├── data_loader.py         # 数据加载模块
├── vector_store.py        # 向量存储模块
├── ollama_client.py       # Ollama客户端
├── api_client.py          # API客户端（可选）
├── hybrid_client.py       # 混合客户端（可选）
├── data/                  # 数据文件夹
├── chroma_db/            # 向量数据库存储
├── requirements.txt       # Python依赖
└── README.md             # 说明文档
```

## 核心模块说明

### DataLoader (数据加载器)
- 支持多种文件格式的解析
- 智能文档切割和预处理
- 自动过滤临时文件和系统文件
- 保护URL链接等重要信息

### VectorStore (向量存储)
- 基于ChromaDB的向量存储
- 支持增量更新和数据去重
- 智能相似度匹配和过滤
- 兜底查询机制

### OllamaClient (模型客户端)
- 本地Ollama模型集成
- 智能文本生成
- 模型状态检查和管理

### RAGSystem (核心系统)
- 统一的问答接口
- 交互式对话管理
- 智能上下文构建
- 结果优化和排序

## 高级配置

### 文本处理优化
```python
# 保护重要信息
PRESERVE_URLS = True
PRESERVE_EMAIL = True
PRESERVE_ORIGINAL_TEXT = True

# 最小化过滤
MINIMAL_FILTERING = True
```

### 性能调优
```python
# 调整查询参数
MAX_RESULTS = 150
MIN_SIMILARITY_THRESHOLD = 0.15

# 调整文档切割
MAX_CHUNK_SIZE = 50
OVERLAP_SIZE = 10
```

## 故障排除

### 常见问题

**1. Ollama服务连接失败**
```bash
# 确保Ollama服务正在运行
ollama serve

# 检查模型是否已安装
ollama list
```

**2. 文档向量化失败**
- 检查文档格式是否支持
- 确认文档内容不为空
- 验证字符编码是否正确

**3. 查询无结果**
- 降低相似度阈值
- 启用兜底查询机制
- 检查文档是否成功加载

### 调试模式
启用详细日志输出：
```python
# 在config.py中添加
DEBUG_MODE = True
VERBOSE_LOGGING = True
```

## 性能优化建议

1. **文档数量**：建议单个data文件夹内文档数量不超过1000个
2. **文档大小**：单个文档建议不超过10MB
3. **向量维度**：根据硬件配置调整嵌入模型
4. **内存使用**：大量文档时考虑批量处理

## 扩展功能

### API模式支持
系统支持切换到云端API模式：
- OpenAI API
- DeepSeek API
- 智谱AI API
- 通义千问 API

### 自定义模型
可以替换为其他兼容的模型：
```python
EMBEDDING_MODEL = "your-custom-embedding-model"
GENERATION_MODEL = "your-custom-generation-model"
```

## 贡献指南

欢迎提交Issue和Pull Request来改进项目：

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基础RAG功能
- 多格式文档支持
- 交互式问答界面

---

**注意**：本系统完全在本地运行，确保数据隐私和安全。如有问题，请查看故障排除部分或提交Issue。
