# 中国今日新闻早报整理工具

📰 一个功能强大的中国新闻自动整理工具，支持多源新闻获取、智能分类、重要性判断和多种格式输出。

## ✨ 功能特点

- 🔄 **多源新闻获取**：支持RSS源和网页爬取
- 🏷️ **智能分类**：自动将新闻分类为政治、经济、科技、社会等10个类别
- ⭐ **重要性判断**：根据关键词和来源自动判断新闻重要性等级
- 📊 **多种输出格式**：支持TXT、JSON、HTML格式输出
- 🎨 **美观界面**：生成现代化的HTML新闻早报页面
- ⚙️ **灵活配置**：通过YAML配置文件自定义所有设置
- 🚫 **智能过滤**：自动过滤广告和低质量新闻

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r news_requirements.txt
```

### 2. 运行示例

```bash
# 运行基础示例
python news_digest.py

# 运行完整管理器
python news_manager.py
```

### 3. 查看结果

运行完成后，会生成以下文件：
- `news_digest_YYYYMMDD.txt` - 文本格式新闻早报
- `news_data_YYYYMMDD.json` - JSON格式新闻数据
- `news_digest_YYYYMMDD.html` - HTML格式新闻早报（如果启用）

## 📁 文件结构

```
├── news_digest.py          # 基础新闻整理工具
├── news_crawler.py         # 新闻爬虫工具
├── news_manager.py         # 完整新闻管理器
├── news_config.yaml        # 配置文件
├── news_requirements.txt   # 依赖文件
├── templates/
│   └── news_template.html  # HTML模板
└── NEWS_README.md         # 说明文档
```

## ⚙️ 配置说明

### 主要配置项

1. **新闻源配置**
   - RSS源：人民网、新华网等官方媒体
   - 网页源：新浪、搜狐等门户网站

2. **分类配置**
   - 政治、经济、科技、社会、教育、体育、健康、环境、文化、国际

3. **重要性判断**
   - 等级1-5，根据关键词和来源自动判断

4. **输出格式**
   - TXT：纯文本格式
   - JSON：结构化数据
   - HTML：美观的网页格式

### 自定义配置

编辑 `news_config.yaml` 文件来自定义：

```yaml
# 添加新的新闻源
news_sources:
  rss:
    your_source:
      name: "你的新闻源"
      url: "RSS地址"
      enabled: true
      category: "分类"

# 修改分类关键词
categories:
  科技:
    keywords: ["AI", "人工智能", "5G", "芯片"]
    priority: 4
```

## 🎯 使用场景

### 1. 个人新闻阅读
- 每日自动获取最新新闻
- 按兴趣分类浏览
- 生成个人新闻摘要

### 2. 企业信息监控
- 监控行业相关新闻
- 生成每日新闻简报
- 跟踪竞争对手动态

### 3. 学术研究
- 收集研究领域新闻
- 分析新闻趋势
- 生成研究数据

### 4. 内容创作
- 获取新闻素材
- 生成内容摘要
- 制作新闻专题

## 🔧 高级功能

### 1. 定时任务

```python
import schedule
import time
from news_manager import NewsManager

def daily_news():
    manager = NewsManager()
    manager.run()

# 每天上午8点运行
schedule.every().day.at("08:00").do(daily_news)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2. 自定义新闻源

```python
from news_manager import NewsManager

manager = NewsManager()

# 添加自定义新闻源
manager.config['news_sources']['rss']['custom'] = {
    'name': '自定义源',
    'url': 'https://example.com/rss',
    'enabled': True,
    'category': '科技'
}

manager.run()
```

### 3. 新闻过滤

```yaml
filters:
  title_blacklist: ["广告", "推广", "营销"]
  source_blacklist: ["垃圾网站"]
  min_title_length: 10
  max_title_length: 100
```

## 📊 输出示例

### 文本格式
```
📰 中国今日新闻早报 - 2024年12月19日
==================================================

🔥 头条新闻
--------------------
1. 国务院常务会议部署进一步扩大开放措施
   会议决定进一步扩大对外开放，优化营商环境，推动经济高质量发展。
   来源：新华社

2. 央行发布最新货币政策报告
   报告显示当前货币政策保持稳健，将继续支持实体经济发展。
   来源：中国人民银行

📋 政治
--------------------
1. 国务院常务会议部署进一步扩大开放措施
   会议决定进一步扩大对外开放，优化营商环境，推动经济高质量发展。
   来源：新华社

📋 经济
--------------------
1. 央行发布最新货币政策报告
   报告显示当前货币政策保持稳健，将继续支持实体经济发展。
   来源：中国人民银行

2. 新能源汽车销量再创新高
   今年前11个月，我国新能源汽车销量同比增长35%，市场表现强劲。
   来源：中国汽车工业协会

==================================================
📊 今日共收集 6 条新闻
⏰ 生成时间：2024-12-19 10:30:00
```

### HTML格式
生成美观的响应式网页，包含：
- 新闻分类导航
- 重要性标识
- 交互式筛选
- 移动端适配

## 🛠️ 故障排除

### 常见问题

1. **网络连接失败**
   - 检查网络连接
   - 确认新闻源URL可访问
   - 调整请求超时时间

2. **依赖安装失败**
   ```bash
   pip install --upgrade pip
   pip install -r news_requirements.txt
   ```

3. **配置文件错误**
   - 检查YAML语法
   - 确认文件编码为UTF-8
   - 验证配置项格式

4. **新闻获取为空**
   - 检查新闻源是否有效
   - 调整CSS选择器
   - 查看日志文件

### 日志查看

```bash
# 查看运行日志
tail -f news_manager.log

# 查看错误信息
grep ERROR news_manager.log
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个工具！

### 贡献方式

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

### 开发环境

```bash
# 克隆项目
git clone <repository-url>
cd news-digest-tool

# 安装开发依赖
pip install -r news_requirements.txt

# 运行测试
python -m pytest tests/
```

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

感谢以下开源项目的支持：
- requests - HTTP库
- beautifulsoup4 - HTML解析
- feedparser - RSS解析
- PyYAML - YAML处理
- Jinja2 - 模板引擎

---

📧 如有问题或建议，请通过Issue联系我们！