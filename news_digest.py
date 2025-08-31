#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国今日新闻早报整理工具
功能：整理、分类和格式化中国今日新闻
"""

import json
import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

class NewsCategory(Enum):
    """新闻分类枚举"""
    POLITICS = "政治"
    ECONOMY = "经济"
    SOCIETY = "社会"
    TECHNOLOGY = "科技"
    CULTURE = "文化"
    SPORTS = "体育"
    INTERNATIONAL = "国际"
    HEALTH = "健康"
    EDUCATION = "教育"
    ENVIRONMENT = "环境"

@dataclass
class NewsItem:
    """新闻条目数据结构"""
    title: str
    summary: str
    category: NewsCategory
    source: str
    url: str = ""
    publish_time: str = ""
    importance: int = 1  # 重要性等级 1-5
    
class NewsDigest:
    """新闻早报整理器"""
    
    def __init__(self):
        self.news_items: List[NewsItem] = []
        self.today = datetime.datetime.now().strftime("%Y年%m月%d日")
        
    def add_news(self, title: str, summary: str, category: NewsCategory, 
                 source: str, url: str = "", publish_time: str = "", importance: int = 1):
        """添加新闻条目"""
        news_item = NewsItem(
            title=title,
            summary=summary,
            category=category,
            source=source,
            url=url,
            publish_time=publish_time,
            importance=importance
        )
        self.news_items.append(news_item)
        
    def get_news_by_category(self, category: NewsCategory) -> List[NewsItem]:
        """按分类获取新闻"""
        return [item for item in self.news_items if item.category == category]
    
    def get_top_news(self, limit: int = 5) -> List[NewsItem]:
        """获取重要新闻"""
        sorted_news = sorted(self.news_items, key=lambda x: x.importance, reverse=True)
        return sorted_news[:limit]
    
    def generate_digest(self) -> str:
        """生成新闻早报"""
        if not self.news_items:
            return "今日暂无新闻"
            
        digest = f"📰 中国今日新闻早报 - {self.today}\n"
        digest += "=" * 50 + "\n\n"
        
        # 头条新闻
        top_news = self.get_top_news(3)
        if top_news:
            digest += "🔥 头条新闻\n"
            digest += "-" * 20 + "\n"
            for i, news in enumerate(top_news, 1):
                digest += f"{i}. {news.title}\n"
                digest += f"   {news.summary}\n"
                digest += f"   来源：{news.source}\n\n"
        
        # 按分类整理新闻
        for category in NewsCategory:
            category_news = self.get_news_by_category(category)
            if category_news:
                digest += f"📋 {category.value}\n"
                digest += "-" * 20 + "\n"
                for i, news in enumerate(category_news, 1):
                    digest += f"{i}. {news.title}\n"
                    digest += f"   {news.summary}\n"
                    digest += f"   来源：{news.source}\n\n"
        
        digest += "=" * 50 + "\n"
        digest += f"📊 今日共收集 {len(self.news_items)} 条新闻\n"
        digest += f"⏰ 生成时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return digest
    
    def save_to_file(self, filename: str = None):
        """保存到文件"""
        if filename is None:
            filename = f"news_digest_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
        
        digest = self.generate_digest()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(digest)
        print(f"新闻早报已保存到：{filename}")
    
    def export_json(self, filename: str = None):
        """导出为JSON格式"""
        if filename is None:
            filename = f"news_data_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        
        # 转换枚举为字符串
        news_items_data = []
        for item in self.news_items:
            item_dict = asdict(item)
            item_dict['category'] = item_dict['category'].value  # 转换枚举为字符串
            news_items_data.append(item_dict)
        
        data = {
            "date": self.today,
            "total_news": len(self.news_items),
            "news_items": news_items_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"新闻数据已导出到：{filename}")

def create_sample_digest():
    """创建示例新闻早报"""
    digest = NewsDigest()
    
    # 添加示例新闻
    digest.add_news(
        title="国务院常务会议部署进一步扩大开放措施",
        summary="会议决定进一步扩大对外开放，优化营商环境，推动经济高质量发展。",
        category=NewsCategory.POLITICS,
        source="新华社",
        importance=5
    )
    
    digest.add_news(
        title="央行发布最新货币政策报告",
        summary="报告显示当前货币政策保持稳健，将继续支持实体经济发展。",
        category=NewsCategory.ECONOMY,
        source="中国人民银行",
        importance=4
    )
    
    digest.add_news(
        title="新能源汽车销量再创新高",
        summary="今年前11个月，我国新能源汽车销量同比增长35%，市场表现强劲。",
        category=NewsCategory.ECONOMY,
        source="中国汽车工业协会",
        importance=3
    )
    
    digest.add_news(
        title="5G网络建设取得重要进展",
        summary="全国5G基站数量突破300万个，5G用户数超过7亿。",
        category=NewsCategory.TECHNOLOGY,
        source="工业和信息化部",
        importance=4
    )
    
    digest.add_news(
        title="全国教育工作会议在京召开",
        summary="会议强调要深化教育改革，提高教育质量，促进教育公平。",
        category=NewsCategory.EDUCATION,
        source="教育部",
        importance=3
    )
    
    digest.add_news(
        title="冬季运动项目备战冬奥会",
        summary="各项目国家队积极备战，力争在冬奥会上取得好成绩。",
        category=NewsCategory.SPORTS,
        source="国家体育总局",
        importance=2
    )
    
    return digest

def main():
    """主函数"""
    print("📰 中国今日新闻早报整理工具")
    print("=" * 40)
    
    # 创建示例新闻早报
    digest = create_sample_digest()
    
    # 显示新闻早报
    print(digest.generate_digest())
    
    # 保存到文件
    digest.save_to_file()
    digest.export_json()
    
    print("\n✅ 新闻早报整理完成！")

if __name__ == "__main__":
    main()