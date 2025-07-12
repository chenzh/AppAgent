#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球评论抓取和分析脚本
功能：抓取雪球一周的评论数据，使用AI分析并总结关注点
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
from dashscope import Generation

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('xueqiu_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XueqiuCommentAnalyzer:
    def __init__(self, config_path: str = 'config.yaml'):
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
                'api_key': '',
                'max_comments': 1000,
                'timeout': 30,
                'retry_times': 3
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
    
    def analyze_comments_with_ai(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """使用AI分析评论内容"""
        if not comments:
            return {"error": "没有评论数据"}
        
        # 准备分析文本
        comment_texts = []
        for comment in comments:
            cleaned_text = self.clean_text(comment['text'])
            if cleaned_text and len(cleaned_text) > 5:  # 过滤太短的评论
                comment_texts.append(cleaned_text)
        
        if not comment_texts:
            return {"error": "没有有效的评论内容"}
        
        # 合并评论文本
        combined_text = "\n".join(comment_texts[:50])  # 限制长度避免超出API限制
        
        try:
            # 使用阿里云通义千问API进行分析
            prompt = f"""
请分析以下雪球用户的评论内容，总结出主要关注点和情感倾向：

评论内容：
{combined_text}

请从以下几个方面进行分析：
1. 主要关注的话题和股票
2. 市场情绪（乐观/悲观/中性）
3. 热门讨论的行业板块
4. 用户关注的具体问题
5. 投资策略和观点

请用中文回答，格式要清晰。
"""
            
            response = Generation.call(
                model='qwen-turbo',
                prompt=prompt,
                api_key=self.config.get('api_key', '')
            )
            
            if response.status_code == 200:
                return {
                    "analysis": response.output.text,
                    "comment_count": len(comments),
                    "valid_comment_count": len(comment_texts)
                }
            else:
                logger.error(f"AI分析失败: {response.message}")
                return {"error": f"AI分析失败: {response.message}"}
                
        except Exception as e:
            logger.error(f"AI分析异常: {e}")
            return {"error": f"AI分析异常: {e}"}
    
    def extract_keywords(self, comments: List[Dict[str, Any]]) -> List[str]:
        """提取关键词"""
        all_text = " ".join([self.clean_text(c['text']) for c in comments if c['text']])
        
        # 简单的关键词提取（股票代码、行业词汇等）
        keywords = []
        
        # 提取股票代码
        stock_codes = re.findall(r'[0-9]{6}', all_text)
        keywords.extend(stock_codes[:10])  # 限制数量
        
        # 提取常见行业词汇
        industry_words = ['科技', '医药', '新能源', '消费', '金融', '地产', '芯片', 'AI', '人工智能', 
                         '新能源汽车', '光伏', '风电', '储能', '白酒', '医药', '银行', '保险']
        
        for word in industry_words:
            if word in all_text:
                keywords.append(word)
        
        return list(set(keywords))[:20]  # 去重并限制数量
    
    def run_analysis(self, days: int = 7) -> Dict[str, Any]:
        """运行完整的分析流程"""
        logger.info(f"开始分析雪球 {days} 天的评论数据...")
        
        # 1. 获取热门话题
        topics = self.get_hot_topics(days)
        if not topics:
            return {"error": "无法获取热门话题"}
        
        # 2. 获取评论数据
        all_comments = []
        for topic in topics[:10]:  # 限制话题数量
            comments = self.get_comments(topic['id'], max_comments=50)
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
        
        # 4. AI分析
        ai_analysis = self.analyze_comments_with_ai(cleaned_comments)
        
        # 5. 关键词提取
        keywords = self.extract_keywords(cleaned_comments)
        
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
            "ai_analysis": ai_analysis,
            "keywords": keywords,
            "top_users": top_users,
            "sample_comments": cleaned_comments[:20]  # 保存前20条评论作为样本
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """保存分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xueqiu_analysis_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"报告已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
    
    def print_summary(self, report: Dict[str, Any]):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("雪球评论分析报告")
        print("="*60)
        print(f"分析时间: {report.get('analysis_date', 'N/A')}")
        print(f"分析周期: {report.get('analysis_period', 'N/A')}")
        print(f"话题数量: {report.get('total_topics', 0)}")
        print(f"评论总数: {report.get('total_comments', 0)}")
        print(f"有效评论: {report.get('valid_comments', 0)}")
        
        print("\n关键词:")
        keywords = report.get('keywords', [])
        if keywords:
            print(", ".join(keywords[:10]))
        
        print("\n活跃用户:")
        top_users = report.get('top_users', [])
        for user, count in top_users[:5]:
            print(f"  {user}: {count}条评论")
        
        print("\nAI分析结果:")
        ai_analysis = report.get('ai_analysis', {})
        if 'analysis' in ai_analysis:
            print(ai_analysis['analysis'])
        elif 'error' in ai_analysis:
            print(f"分析失败: {ai_analysis['error']}")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='雪球评论分析工具')
    parser.add_argument('--days', type=int, default=7, help='分析天数 (默认: 7)')
    parser.add_argument('--output', type=str, help='输出文件名')
    parser.add_argument('--config', type=str, default='config.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = XueqiuCommentAnalyzer(args.config)
    
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