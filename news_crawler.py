#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻爬虫工具
功能：从多个新闻源获取实时新闻并进行整理
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import feedparser
from news_digest import NewsDigest, NewsCategory

class NewsCrawler:
    """新闻爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_rss_news(self, rss_url: str) -> List[Dict[str, Any]]:
        """从RSS源获取新闻"""
        try:
            feed = feedparser.parse(rss_url)
            news_list = []
            
            for entry in feed.entries[:10]:  # 获取前10条新闻
                news = {
                    'title': entry.title,
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'url': entry.link,
                    'publish_time': entry.published if hasattr(entry, 'published') else '',
                    'source': feed.feed.title if hasattr(feed.feed, 'title') else 'RSS源'
                }
                news_list.append(news)
                
            return news_list
        except Exception as e:
            print(f"获取RSS新闻失败: {e}")
            return []
    
    def get_web_news(self, url: str, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """从网页获取新闻"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            
            # 根据选择器提取新闻
            if 'news_container' in selectors:
                containers = soup.select(selectors['news_container'])
                for container in containers[:10]:  # 限制数量
                    news = {}
                    
                    if 'title' in selectors:
                        title_elem = container.select_one(selectors['title'])
                        if title_elem:
                            news['title'] = title_elem.get_text(strip=True)
                    
                    if 'summary' in selectors:
                        summary_elem = container.select_one(selectors['summary'])
                        if summary_elem:
                            news['summary'] = summary_elem.get_text(strip=True)
                    
                    if 'url' in selectors:
                        url_elem = container.select_one(selectors['url'])
                        if url_elem and url_elem.get('href'):
                            news['url'] = urljoin(url, url_elem['href'])
                    
                    if 'time' in selectors:
                        time_elem = container.select_one(selectors['time'])
                        if time_elem:
                            news['publish_time'] = time_elem.get_text(strip=True)
                    
                    if news.get('title'):  # 只添加有标题的新闻
                        news['source'] = urlparse(url).netloc
                        news_list.append(news)
            
            return news_list
        except Exception as e:
            print(f"获取网页新闻失败: {e}")
            return []

class NewsAggregator:
    """新闻聚合器"""
    
    def __init__(self):
        self.crawler = NewsCrawler()
        self.digest = NewsDigest()
        
        # 新闻源配置
        self.news_sources = {
            'rss': {
                'people': 'http://www.people.com.cn/rss/politics.xml',  # 人民网政治
                'xinhua': 'http://www.xinhuanet.com/politics/news_politics.xml',  # 新华网政治
                'cctv': 'http://news.cctv.com/2019/07/gaiban/cmsdatainterface/page/news_1.jsonp'  # 央视新闻
            },
            'web': {
                'sina': {
                    'url': 'https://news.sina.com.cn/',
                    'selectors': {
                        'news_container': '.news-item',
                        'title': 'h2 a',
                        'summary': '.summary',
                        'url': 'h2 a',
                        'time': '.time'
                    }
                }
            }
        }
    
    def categorize_news(self, title: str, summary: str) -> NewsCategory:
        """根据标题和摘要自动分类新闻"""
        text = (title + ' ' + summary).lower()
        
        # 政治类关键词
        politics_keywords = ['国务院', '政治局', '中央', '政府', '政策', '法规', '会议', '领导人', '习近平', '李克强']
        if any(keyword in text for keyword in politics_keywords):
            return NewsCategory.POLITICS
        
        # 经济类关键词
        economy_keywords = ['经济', '金融', '股市', '银行', '央行', 'GDP', '投资', '贸易', '出口', '进口', '企业']
        if any(keyword in text for keyword in economy_keywords):
            return NewsCategory.ECONOMY
        
        # 科技类关键词
        tech_keywords = ['科技', '技术', '互联网', 'AI', '人工智能', '5G', '芯片', '创新', '数字化']
        if any(keyword in text for keyword in tech_keywords):
            return NewsCategory.TECHNOLOGY
        
        # 教育类关键词
        education_keywords = ['教育', '学校', '学生', '教师', '考试', '招生', '大学', '培训']
        if any(keyword in text for keyword in education_keywords):
            return NewsCategory.EDUCATION
        
        # 体育类关键词
        sports_keywords = ['体育', '足球', '篮球', '奥运会', '比赛', '运动员', '冠军', '赛事']
        if any(keyword in text for keyword in sports_keywords):
            return NewsCategory.SPORTS
        
        # 健康类关键词
        health_keywords = ['健康', '医疗', '医院', '疾病', '疫苗', '药品', '治疗', '医生']
        if any(keyword in text for keyword in health_keywords):
            return NewsCategory.HEALTH
        
        # 环境类关键词
        environment_keywords = ['环境', '环保', '污染', '气候', '生态', '绿色', '可持续发展']
        if any(keyword in text for keyword in environment_keywords):
            return NewsCategory.ENVIRONMENT
        
        # 文化类关键词
        culture_keywords = ['文化', '艺术', '电影', '音乐', '文学', '历史', '传统', '博物馆']
        if any(keyword in text for keyword in culture_keywords):
            return NewsCategory.CULTURE
        
        # 国际类关键词
        international_keywords = ['国际', '外交', '美国', '日本', '欧洲', '联合国', '全球', '世界']
        if any(keyword in text for keyword in international_keywords):
            return NewsCategory.INTERNATIONAL
        
        # 默认为社会类
        return NewsCategory.SOCIETY
    
    def determine_importance(self, title: str, summary: str, source: str) -> int:
        """判断新闻重要性等级"""
        text = (title + ' ' + summary).lower()
        
        # 重要关键词
        important_keywords = ['紧急', '重大', '重要', '突发', '首次', '突破', '创新', '政策', '法规']
        if any(keyword in text for keyword in important_keywords):
            return 5
        
        # 权威媒体
        authoritative_sources = ['新华社', '人民日报', '央视', '中央', '国务院']
        if any(source in authoritative_sources for source in authoritative_sources):
            return 4
        
        # 一般重要
        if len(title) > 20 or '发布' in text or '公布' in text:
            return 3
        
        return 2
    
    def aggregate_news(self) -> NewsDigest:
        """聚合新闻"""
        print("开始获取新闻...")
        
        # 从RSS源获取新闻
        for source_name, rss_url in self.news_sources['rss'].items():
            print(f"正在获取 {source_name} 的新闻...")
            news_list = self.crawler.get_rss_news(rss_url)
            
            for news in news_list:
                category = self.categorize_news(news['title'], news['summary'])
                importance = self.determine_importance(news['title'], news['summary'], news['source'])
                
                self.digest.add_news(
                    title=news['title'],
                    summary=news['summary'],
                    category=category,
                    source=news['source'],
                    url=news.get('url', ''),
                    publish_time=news.get('publish_time', ''),
                    importance=importance
                )
        
        # 从网页获取新闻
        for source_name, config in self.news_sources['web'].items():
            print(f"正在获取 {source_name} 的新闻...")
            news_list = self.crawler.get_web_news(config['url'], config['selectors'])
            
            for news in news_list:
                category = self.categorize_news(news['title'], news['summary'])
                importance = self.determine_importance(news['title'], news['summary'], news['source'])
                
                self.digest.add_news(
                    title=news['title'],
                    summary=news['summary'],
                    category=category,
                    source=news['source'],
                    url=news.get('url', ''),
                    publish_time=news.get('publish_time', ''),
                    importance=importance
                )
        
        print(f"共获取到 {len(self.digest.news_items)} 条新闻")
        return self.digest

def main():
    """主函数"""
    print("📰 中国今日新闻早报自动整理工具")
    print("=" * 50)
    
    # 创建新闻聚合器
    aggregator = NewsAggregator()
    
    # 聚合新闻
    digest = aggregator.aggregate_news()
    
    # 生成并显示新闻早报
    print("\n" + digest.generate_digest())
    
    # 保存文件
    digest.save_to_file()
    digest.export_json()
    
    print("\n✅ 新闻早报自动整理完成！")

if __name__ == "__main__":
    main()