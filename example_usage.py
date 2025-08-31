#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻整理工具使用示例
展示如何使用新闻整理工具的各种功能
"""

from news_digest import NewsDigest, NewsCategory
from datetime import datetime

def example_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    # 创建新闻摘要对象
    digest = NewsDigest()
    
    # 添加新闻
    digest.add_news(
        title="中国成功发射新一代通信卫星",
        summary="今日凌晨，中国在酒泉卫星发射中心成功发射新一代通信卫星，标志着我国航天技术再上新台阶。",
        category=NewsCategory.TECHNOLOGY,
        source="中国航天科技集团",
        importance=4
    )
    
    digest.add_news(
        title="全国经济工作会议在京召开",
        summary="会议强调要稳中求进，推动经济高质量发展，确保明年经济工作开好局、起好步。",
        category=NewsCategory.ECONOMY,
        source="新华社",
        importance=5
    )
    
    # 生成并显示摘要
    print(digest.generate_digest())
    
    return digest

def example_custom_news():
    """自定义新闻示例"""
    print("\n=== 自定义新闻示例 ===")
    
    digest = NewsDigest()
    
    # 添加不同类型的新闻
    news_data = [
        {
            "title": "国务院发布新能源汽车产业发展规划",
            "summary": "规划提出到2035年，新能源汽车市场竞争力明显增强，销量占汽车总销量的50%以上。",
            "category": NewsCategory.ECONOMY,
            "source": "国务院",
            "importance": 5
        },
        {
            "title": "中国队在亚运会上获得金牌",
            "summary": "在刚刚结束的亚运会比赛中，中国队表现出色，获得多枚金牌，为国争光。",
            "category": NewsCategory.SPORTS,
            "source": "国家体育总局",
            "importance": 3
        },
        {
            "title": "全国教育工作会议强调素质教育",
            "summary": "会议强调要全面贯彻党的教育方针，落实立德树人根本任务，发展素质教育。",
            "category": NewsCategory.EDUCATION,
            "source": "教育部",
            "importance": 4
        },
        {
            "title": "环保部发布空气质量改善报告",
            "summary": "报告显示，今年以来全国空气质量持续改善，PM2.5浓度同比下降明显。",
            "category": NewsCategory.ENVIRONMENT,
            "source": "生态环境部",
            "importance": 3
        },
        {
            "title": "中国传统文化展览在京开幕",
            "summary": "展览集中展示了中华优秀传统文化的精髓，吸引了众多观众参观。",
            "category": NewsCategory.CULTURE,
            "source": "文化部",
            "importance": 2
        }
    ]
    
    # 批量添加新闻
    for news in news_data:
        digest.add_news(**news)
    
    # 按分类获取新闻
    print("政治类新闻:")
    politics_news = digest.get_news_by_category(NewsCategory.POLITICS)
    for news in politics_news:
        print(f"  - {news.title}")
    
    print("\n经济类新闻:")
    economy_news = digest.get_news_by_category(NewsCategory.ECONOMY)
    for news in economy_news:
        print(f"  - {news.title}")
    
    print("\n科技类新闻:")
    tech_news = digest.get_news_by_category(NewsCategory.TECHNOLOGY)
    for news in tech_news:
        print(f"  - {news.title}")
    
    return digest

def example_file_operations():
    """文件操作示例"""
    print("\n=== 文件操作示例 ===")
    
    digest = NewsDigest()
    
    # 添加一些新闻
    digest.add_news(
        title="示例新闻标题1",
        summary="这是第一条示例新闻的摘要内容。",
        category=NewsCategory.SOCIETY,
        source="示例来源",
        importance=3
    )
    
    digest.add_news(
        title="示例新闻标题2",
        summary="这是第二条示例新闻的摘要内容。",
        category=NewsCategory.HEALTH,
        source="示例来源",
        importance=2
    )
    
    # 保存到文件
    filename = f"example_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    digest.save_to_file(f"{filename}.txt")
    digest.export_json(f"{filename}.json")
    
    print(f"文件已保存:")
    print(f"  - {filename}.txt (文本格式)")
    print(f"  - {filename}.json (JSON格式)")

def example_statistics():
    """统计信息示例"""
    print("\n=== 统计信息示例 ===")
    
    digest = NewsDigest()
    
    # 添加不同重要性的新闻
    for i in range(1, 6):
        digest.add_news(
            title=f"重要性等级{i}的新闻",
            summary=f"这是重要性等级为{i}的新闻摘要。",
            category=NewsCategory.SOCIETY,
            source="示例来源",
            importance=i
        )
    
    # 获取重要新闻
    top_news = digest.get_top_news(3)
    print("最重要的3条新闻:")
    for i, news in enumerate(top_news, 1):
        print(f"  {i}. {news.title} (重要性: {news.importance})")
    
    # 统计信息
    print(f"\n总新闻数: {len(digest.news_items)}")
    
    # 按分类统计
    category_counts = {}
    for news in digest.news_items:
        category = news.category.value
        category_counts[category] = category_counts.get(category, 0) + 1
    
    print("按分类统计:")
    for category, count in category_counts.items():
        print(f"  {category}: {count}条")

def main():
    """主函数"""
    print("📰 新闻整理工具使用示例")
    print("=" * 50)
    
    try:
        # 运行各种示例
        example_basic_usage()
        example_custom_news()
        example_file_operations()
        example_statistics()
        
        print("\n✅ 所有示例运行完成！")
        
    except Exception as e:
        print(f"❌ 运行示例时出错: {e}")

if __name__ == "__main__":
    main()