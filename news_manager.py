#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻管理器
功能：整合配置、爬虫、整理和输出功能
"""

import yaml
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from jinja2 import Template
import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from news_digest import NewsDigest, NewsCategory

class NewsManager:
    """新闻管理器主类"""
    
    def __init__(self, config_file: str = "news_config.yaml"):
        self.config_file = config_file
        self.config = self.load_config()
        self.digest = NewsDigest()
        self.setup_logging()
        
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'system': {
                'fetch_interval': 3600,
                'max_news_count': 50,
                'output_format': ['txt', 'json'],
                'auto_categorize': True,
                'auto_importance': True
            },
            'news_sources': {
                'rss': {
                    'people_politics': {
                        'name': '人民网政治',
                        'url': 'http://www.people.com.cn/rss/politics.xml',
                        'enabled': True,
                        'category': '政治'
                    }
                }
            }
        }
    
    def setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_config.get('file', 'news_manager.log'), encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def fetch_news(self) -> NewsDigest:
        """获取新闻"""
        self.logger.info("开始获取新闻...")
        
        # 获取RSS新闻
        rss_sources = self.config.get('news_sources', {}).get('rss', {})
        for source_id, source_config in rss_sources.items():
            if source_config.get('enabled', True):
                self.logger.info(f"正在获取 {source_config['name']} 的新闻...")
                news_list = self.fetch_rss_news(source_config['url'])
                self.process_news_list(news_list, source_config['name'])
        
        # 获取网页新闻
        web_sources = self.config.get('news_sources', {}).get('web', {})
        for source_id, source_config in web_sources.items():
            if source_config.get('enabled', True):
                self.logger.info(f"正在获取 {source_config['name']} 的新闻...")
                news_list = self.fetch_web_news(source_config['url'], source_config.get('selectors', {}))
                self.process_news_list(news_list, source_config['name'])
        
        self.logger.info(f"共获取到 {len(self.digest.news_items)} 条新闻")
        return self.digest
    
    def fetch_rss_news(self, rss_url: str) -> List[Dict[str, Any]]:
        """从RSS源获取新闻"""
        try:
            feed = feedparser.parse(rss_url)
            news_list = []
            
            for entry in feed.entries[:10]:
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
            self.logger.error(f"获取RSS新闻失败: {e}")
            return []
    
    def fetch_web_news(self, url: str, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """从网页获取新闻"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_list = []
            
            if 'news_container' in selectors:
                containers = soup.select(selectors['news_container'])
                for container in containers[:10]:
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
                    
                    if news.get('title'):
                        news['source'] = urlparse(url).netloc
                        news_list.append(news)
            
            return news_list
        except Exception as e:
            self.logger.error(f"获取网页新闻失败: {e}")
            return []
    
    def process_news_list(self, news_list: List[Dict[str, Any]], source_name: str):
        """处理新闻列表"""
        for news in news_list:
            # 过滤新闻
            if not self.filter_news(news):
                continue
            
            # 自动分类
            category = self.auto_categorize(news['title'], news['summary'])
            
            # 判断重要性
            importance = self.determine_importance(news['title'], news['summary'], source_name)
            
            # 添加到摘要
            self.digest.add_news(
                title=news['title'],
                summary=news['summary'],
                category=category,
                source=source_name,
                url=news.get('url', ''),
                publish_time=news.get('publish_time', ''),
                importance=importance
            )
    
    def filter_news(self, news: Dict[str, Any]) -> bool:
        """过滤新闻"""
        filters = self.config.get('filters', {})
        
        # 标题黑名单过滤
        title_blacklist = filters.get('title_blacklist', [])
        if any(keyword in news['title'] for keyword in title_blacklist):
            return False
        
        # 来源黑名单过滤
        source_blacklist = filters.get('source_blacklist', [])
        if any(keyword in news.get('source', '') for keyword in source_blacklist):
            return False
        
        # 标题长度过滤
        min_length = filters.get('min_title_length', 5)
        max_length = filters.get('max_title_length', 100)
        if not (min_length <= len(news['title']) <= max_length):
            return False
        
        # 摘要长度过滤
        min_summary_length = filters.get('min_summary_length', 10)
        max_summary_length = filters.get('max_summary_length', 500)
        if not (min_summary_length <= len(news['summary']) <= max_summary_length):
            return False
        
        return True
    
    def auto_categorize(self, title: str, summary: str) -> NewsCategory:
        """自动分类新闻"""
        if not self.config.get('system', {}).get('auto_categorize', True):
            return NewsCategory.SOCIETY
        
        categories_config = self.config.get('categories', {})
        text = (title + ' ' + summary).lower()
        
        for category_name, config in categories_config.items():
            keywords = config.get('keywords', [])
            if any(keyword in text for keyword in keywords):
                # 将中文分类名转换为枚举
                for category_enum in NewsCategory:
                    if category_enum.value == category_name:
                        return category_enum
        
        return NewsCategory.SOCIETY
    
    def determine_importance(self, title: str, summary: str, source: str) -> int:
        """判断新闻重要性"""
        if not self.config.get('system', {}).get('auto_importance', True):
            return 3
        
        importance_config = self.config.get('importance', {})
        text = (title + ' ' + summary).lower()
        
        # 重要关键词
        critical_keywords = importance_config.get('critical_keywords', [])
        if any(keyword in text for keyword in critical_keywords):
            return 5
        
        # 权威媒体
        authoritative_sources = importance_config.get('authoritative_sources', [])
        if any(source in auth_source for auth_source in authoritative_sources):
            return 4
        
        # 一般重要关键词
        important_keywords = importance_config.get('important_keywords', [])
        if any(keyword in text for keyword in important_keywords):
            return 3
        
        # 标题长度判断
        title_length_threshold = importance_config.get('title_length_threshold', 20)
        if len(title) > title_length_threshold:
            return 3
        
        return 2
    
    def generate_outputs(self):
        """生成输出文件"""
        output_config = self.config.get('output', {})
        
        # 生成文本格式
        if output_config.get('txt', {}).get('enabled', True):
            self.generate_txt_output()
        
        # 生成JSON格式
        if output_config.get('json', {}).get('enabled', True):
            self.generate_json_output()
        
        # 生成HTML格式
        if output_config.get('html', {}).get('enabled', False):
            self.generate_html_output()
    
    def generate_txt_output(self):
        """生成文本格式输出"""
        txt_config = self.config.get('output', {}).get('txt', {})
        filename_template = txt_config.get('filename_template', 'news_digest_{date}.txt')
        filename = filename_template.format(date=datetime.now().strftime('%Y%m%d'))
        
        self.digest.save_to_file(filename)
        self.logger.info(f"文本格式输出已保存到: {filename}")
    
    def generate_json_output(self):
        """生成JSON格式输出"""
        json_config = self.config.get('output', {}).get('json', {})
        filename_template = json_config.get('filename_template', 'news_data_{date}.json')
        filename = filename_template.format(date=datetime.now().strftime('%Y%m%d'))
        
        self.digest.export_json(filename)
        self.logger.info(f"JSON格式输出已保存到: {filename}")
    
    def generate_html_output(self):
        """生成HTML格式输出"""
        html_config = self.config.get('output', {}).get('html', {})
        filename_template = html_config.get('filename_template', 'news_digest_{date}.html')
        filename = filename_template.format(date=datetime.now().strftime('%Y%m%d'))
        
        # 读取HTML模板
        template_file = html_config.get('template_file', 'templates/news_template.html')
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            self.logger.error(f"HTML模板文件 {template_file} 不存在")
            return
        
        # 准备模板数据
        template_data = self.prepare_html_data()
        
        # 渲染模板
        template = Template(template_content)
        html_content = template.render(**template_data)
        
        # 保存HTML文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML格式输出已保存到: {filename}")
    
    def prepare_html_data(self) -> Dict[str, Any]:
        """准备HTML模板数据"""
        # 统计分类数据
        category_stats = {}
        for item in self.digest.news_items:
            category = item.category.value
            category_stats[category] = category_stats.get(category, 0) + 1
        
        # 按分类组织新闻
        categorized_news = {}
        for item in self.digest.news_items:
            category = item.category.value
            if category not in categorized_news:
                categorized_news[category] = []
            categorized_news[category].append({
                'title': item.title,
                'summary': item.summary,
                'source': item.source,
                'publish_time': item.publish_time,
                'importance': item.importance
            })
        
        return {
            'title': f"中国今日新闻早报 - {self.digest.today}",
            'date': self.digest.today,
            'total_news': len(self.digest.news_items),
            'categories_count': len(category_stats),
            'top_news_count': len(self.digest.get_top_news(3)),
            'category_stats': category_stats,
            'top_news': [
                {
                    'title': item.title,
                    'summary': item.summary,
                    'source': item.source,
                    'publish_time': item.publish_time,
                    'importance': item.importance
                }
                for item in self.digest.get_top_news(3)
            ],
            'categorized_news': categorized_news,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def run(self):
        """运行新闻管理器"""
        self.logger.info("新闻管理器启动")
        
        try:
            # 获取新闻
            self.fetch_news()
            
            # 生成输出
            self.generate_outputs()
            
            # 显示摘要
            print("\n" + self.digest.generate_digest())
            
            self.logger.info("新闻管理器运行完成")
            
        except Exception as e:
            self.logger.error(f"新闻管理器运行失败: {e}")
            raise

def main():
    """主函数"""
    print("📰 中国今日新闻早报管理器")
    print("=" * 50)
    
    # 创建新闻管理器
    manager = NewsManager()
    
    # 运行管理器
    manager.run()
    
    print("\n✅ 新闻早报整理完成！")

if __name__ == "__main__":
    main()