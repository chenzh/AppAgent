#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球评论分析脚本（简化版）
功能：抓取雪球一周的评论数据，进行本地分析和总结
"""

import requests
import json
import time
import re
from datetime import datetime, timedelta
from collections import Counter
import argparse
import logging
from typing import List, Dict, Any
import yaml

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xueqiu_simple_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XueqiuSimpleAnalyzer:
    def __init__(self, config_path: str = 'xueqiu_config.yaml'):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://xueqiu.com/',
            'Origin': 'https://xueqiu.com'
        })
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return {
                'max_comments': 1000,
                'timeout': 30,
                'retry_times': 3,
                'analysis_days': 7,
                'max_topics': 10,
                'max_comments_per_topic': 50
            }
    
    def get_hot_topics(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取热门话题列表"""
        try:
            # 雪球热门话题API
            url = "https://xueqiu.com/v4/statuses/public_timeline_by_category.json"
            params = {
                'category': 'all',
                'count': 50,
                'page': 1
            }
            
            response = self.session.get(url, params=params, timeout=self.config.get('timeout', 30))
            response.raise_for_status()
            
            data = response.json()
            topics = []
            
            for item in data.get('list', []):
                # 过滤一周内的内容
                created_at = datetime.fromtimestamp(item.get('created_at', 0) / 1000)
                if created_at > datetime.now() - timedelta(days=days):
                    topics.append({
                        'id': item.get('id'),
                        'title': item.get('title', ''),
                        'text': item.get('text', ''),
                        'user': item.get('user', {}).get('screen_name', ''),
                        'created_at': created_at,
                        'retweet_count': item.get('retweet_count', 0),
                        'reply_count': item.get('reply_count', 0),
                        'fav_count': item.get('fav_count', 0)
                    })
            
            logger.info(f"获取到 {len(topics)} 个热门话题")
            return topics
            
        except Exception as e:
            logger.error(f"获取热门话题失败: {e}")
            return []
    
    def get_comments(self, topic_id: str, max_comments: int = 100) -> List[Dict[str, Any]]:
        """获取指定话题的评论"""
        try:
            url = f"https://xueqiu.com/v4/statuses/{topic_id}/comments.json"
            params = {
                'count': min(max_comments, 100),
                'page': 1
            }
            
            response = self.session.get(url, params=params, timeout=self.config.get('timeout', 30))
            response.raise_for_status()
            
            data = response.json()
            comments = []
            
            for item in data.get('list', []):
                comments.append({
                    'id': item.get('id'),
                    'text': item.get('text', ''),
                    'user': item.get('user', {}).get('screen_name', ''),
                    'created_at': datetime.fromtimestamp(item.get('created_at', 0) / 1000),
                    'reply_count': item.get('reply_count', 0),
                    'fav_count': item.get('fav_count', 0)
                })
            
            return comments
            
        except Exception as e:
            logger.error(f"获取话题 {topic_id} 评论失败: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        if not text:
            return ""
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 移除URL
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # 移除特殊字符
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_sentiment(self, text: str) -> str:
        """简单的情感分析"""
        positive_words = ['涨', '好', '看好', '买入', '持有', '乐观', '机会', '利好', '突破', '强势']
        negative_words = ['跌', '不好', '看空', '卖出', '悲观', '风险', '利空', '破位', '弱势', '割肉']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return '乐观'
        elif negative_count > positive_count:
            return '悲观'
        else:
            return '中性'
    
    def extract_keywords(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取关键词和统计信息"""
        all_text = " ".join([self.clean_text(c['text']) for c in comments if c['text']])
        
        # 提取股票代码
        stock_codes = re.findall(r'[0-9]{6}', all_text)
        stock_counter = Counter(stock_codes)
        
        # 提取行业词汇
        industry_words = {
            '科技': ['科技', '芯片', 'AI', '人工智能', '互联网', '软件'],
            '医药': ['医药', '生物', '疫苗', '医院', '药品'],
            '新能源': ['新能源', '光伏', '风电', '储能', '新能源汽车', '电池'],
            '消费': ['消费', '白酒', '食品', '饮料', '零售'],
            '金融': ['金融', '银行', '保险', '券商', '基金'],
            '地产': ['地产', '房地产', '房子', '房价'],
            '军工': ['军工', '国防', '军事', '武器'],
            '农业': ['农业', '粮食', '种植', '养殖']
        }
        
        industry_stats = {}
        for industry, keywords in industry_words.items():
            count = sum(1 for keyword in keywords if keyword in all_text)
            if count > 0:
                industry_stats[industry] = count
        
        # 情感分析
        sentiments = []
        for comment in comments:
            if comment['text']:
                sentiment = self.analyze_sentiment(comment['text'])
                sentiments.append(sentiment)
        
        sentiment_counter = Counter(sentiments)
        
        return {
            'top_stocks': stock_counter.most_common(10),
            'industry_mentions': industry_stats,
            'sentiment_distribution': dict(sentiment_counter),
            'total_stock_mentions': len(stock_codes)
        }
    
    def generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """生成分析总结"""
        summary = []
        summary.append("=== 雪球评论分析总结 ===\n")
        
        # 热门股票
        top_stocks = analysis_data.get('top_stocks', [])
        if top_stocks:
            summary.append("热门股票（按提及次数排序）：")
            for stock, count in top_stocks[:5]:
                summary.append(f"  {stock}: {count}次")
            summary.append("")
        
        # 行业关注度
        industry_mentions = analysis_data.get('industry_mentions', {})
        if industry_mentions:
            summary.append("行业关注度：")
            sorted_industries = sorted(industry_mentions.items(), key=lambda x: x[1], reverse=True)
            for industry, count in sorted_industries[:5]:
                summary.append(f"  {industry}: {count}次提及")
            summary.append("")
        
        # 市场情绪
        sentiment_dist = analysis_data.get('sentiment_distribution', {})
        if sentiment_dist:
            summary.append("市场情绪分布：")
            total = sum(sentiment_dist.values())
            for sentiment, count in sentiment_dist.items():
                percentage = (count / total * 100) if total > 0 else 0
                summary.append(f"  {sentiment}: {count}条 ({percentage:.1f}%)")
            summary.append("")
        
        # 总体分析
        total_mentions = analysis_data.get('total_stock_mentions', 0)
        summary.append(f"总体统计：")
        summary.append(f"  股票提及总数: {total_mentions}")
        summary.append(f"  涉及行业数: {len(industry_mentions)}")
        
        return "\n".join(summary)
    
    def run_analysis(self, days: int = 7) -> Dict[str, Any]:
        """运行完整的分析流程"""
        logger.info(f"开始分析雪球 {days} 天的评论数据...")
        
        # 1. 获取热门话题
        topics = self.get_hot_topics(days)
        if not topics:
            return {"error": "无法获取热门话题"}
        
        # 2. 获取评论数据
        all_comments = []
        for topic in topics[:self.config.get('max_topics', 10)]:
            comments = self.get_comments(topic['id'], max_comments=self.config.get('max_comments_per_topic', 50))
            all_comments.extend(comments)
            time.sleep(1)  # 避免请求过快
        
        logger.info(f"总共获取到 {len(all_comments)} 条评论")
        
        # 3. 数据清洗
        cleaned_comments = []
        for comment in all_comments:
            cleaned_text = self.clean_text(comment['text'])
            if cleaned_text and len(cleaned_text) > 3:
                comment['cleaned_text'] = cleaned_text
                cleaned_comments.append(comment)
        
        # 4. 关键词和统计分析
        analysis_data = self.extract_keywords(cleaned_comments)
        
        # 5. 生成总结
        summary = self.generate_summary(analysis_data)
        
        # 6. 统计信息
        user_stats = Counter([c['user'] for c in cleaned_comments])
        top_users = user_stats.most_common(10)
        
        # 7. 生成报告
        report = {
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_period": f"最近{days}天",
            "total_topics": len(topics),
            "total_comments": len(all_comments),
            "valid_comments": len(cleaned_comments),
            "analysis_data": analysis_data,
            "summary": summary,
            "top_users": top_users,
            "sample_comments": cleaned_comments[:20]  # 保存前20条评论作为样本
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """保存分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xueqiu_simple_analysis_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"报告已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
    
    def print_summary(self, report: Dict[str, Any]):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("雪球评论分析报告（简化版）")
        print("="*60)
        print(f"分析时间: {report.get('analysis_date', 'N/A')}")
        print(f"分析周期: {report.get('analysis_period', 'N/A')}")
        print(f"话题数量: {report.get('total_topics', 0)}")
        print(f"评论总数: {report.get('total_comments', 0)}")
        print(f"有效评论: {report.get('valid_comments', 0)}")
        
        print("\n" + report.get('summary', '无分析结果'))
        
        print("\n活跃用户:")
        top_users = report.get('top_users', [])
        for user, count in top_users[:5]:
            print(f"  {user}: {count}条评论")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='雪球评论分析工具（简化版）')
    parser.add_argument('--days', type=int, default=7, help='分析天数 (默认: 7)')
    parser.add_argument('--output', type=str, help='输出文件名')
    parser.add_argument('--config', type=str, default='xueqiu_config.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = XueqiuSimpleAnalyzer(args.config)
    
    # 运行分析
    report = analyzer.run_analysis(args.days)
    
    if 'error' in report:
        logger.error(f"分析失败: {report['error']}")
        return
    
    # 打印摘要
    analyzer.print_summary(report)
    
    # 保存报告
    analyzer.save_report(report, args.output)

if __name__ == "__main__":
    main()