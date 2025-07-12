#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雪球评论分析演示脚本
使用模拟数据展示分析功能
"""

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
        logging.FileHandler('xueqiu_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class XueqiuDemoAnalyzer:
    def __init__(self, config_path: str = 'xueqiu_config.yaml'):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        
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
    
    def generate_mock_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """生成模拟的评论数据"""
        mock_comments = [
            # 科技股相关评论
            {"text": "000001 平安银行今天涨得不错，看好后市", "user": "投资达人", "created_at": datetime.now() - timedelta(hours=2)},
            {"text": "002415 海康威视AI技术领先，长期看好", "user": "科技观察", "created_at": datetime.now() - timedelta(hours=3)},
            {"text": "300059 东方财富互联网券商龙头，继续持有", "user": "财经分析师", "created_at": datetime.now() - timedelta(hours=4)},
            {"text": "000858 五粮液白酒板块调整，机会来了", "user": "白酒专家", "created_at": datetime.now() - timedelta(hours=5)},
            {"text": "600036 招商银行金融板块稳健，适合长期投资", "user": "银行研究员", "created_at": datetime.now() - timedelta(hours=6)},
            
            # 新能源相关评论
            {"text": "300750 宁德时代新能源电池龙头，继续看好", "user": "新能源投资", "created_at": datetime.now() - timedelta(hours=7)},
            {"text": "002594 比亚迪新能源汽车销量创新高", "user": "汽车分析师", "created_at": datetime.now() - timedelta(hours=8)},
            {"text": "300274 阳光电源光伏逆变器龙头，业绩增长", "user": "光伏专家", "created_at": datetime.now() - timedelta(hours=9)},
            
            # 医药相关评论
            {"text": "300015 爱尔眼科医疗服务龙头，长期价值", "user": "医药研究员", "created_at": datetime.now() - timedelta(hours=10)},
            {"text": "000661 长春高新生物医药创新，前景广阔", "user": "生物科技", "created_at": datetime.now() - timedelta(hours=11)},
            
            # 消费相关评论
            {"text": "000858 五粮液白酒消费升级，品牌价值", "user": "消费分析师", "created_at": datetime.now() - timedelta(hours=12)},
            {"text": "600519 贵州茅台白酒龙头，稀缺性价值", "user": "价值投资者", "created_at": datetime.now() - timedelta(hours=13)},
            
            # 芯片相关评论
            {"text": "002049 紫光国微芯片国产化，技术突破", "user": "芯片专家", "created_at": datetime.now() - timedelta(hours=14)},
            {"text": "300782 卓胜微射频芯片龙头，5G受益", "user": "通信分析师", "created_at": datetime.now() - timedelta(hours=15)},
            
            # 市场情绪评论
            {"text": "市场情绪乐观，科技股领涨，继续看好", "user": "市场观察", "created_at": datetime.now() - timedelta(hours=16)},
            {"text": "新能源板块调整，但长期趋势不变", "user": "趋势分析", "created_at": datetime.now() - timedelta(hours=17)},
            {"text": "医药板块估值合理，可以关注", "user": "医药投资", "created_at": datetime.now() - timedelta(hours=18)},
            {"text": "消费板块稳健，防御性配置", "user": "配置专家", "created_at": datetime.now() - timedelta(hours=19)},
            {"text": "芯片板块技术突破，国产替代加速", "user": "科技投资", "created_at": datetime.now() - timedelta(hours=20)},
            
            # 更多评论
            {"text": "000001 银行股估值修复，配置价值显现", "user": "银行分析师", "created_at": datetime.now() - timedelta(hours=21)},
            {"text": "002415 安防龙头，AI技术应用广泛", "user": "AI专家", "created_at": datetime.now() - timedelta(hours=22)},
            {"text": "300059 互联网券商，用户增长强劲", "user": "互联网分析师", "created_at": datetime.now() - timedelta(hours=23)},
            {"text": "000858 白酒消费，品牌价值持续", "user": "品牌专家", "created_at": datetime.now() - timedelta(hours=24)},
            {"text": "600036 零售银行龙头，数字化转型", "user": "数字化转型", "created_at": datetime.now() - timedelta(hours=25)},
        ]
        
        # 根据天数过滤
        cutoff_time = datetime.now() - timedelta(days=days)
        filtered_comments = [c for c in mock_comments if c['created_at'] > cutoff_time]
        
        return filtered_comments
    
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
        positive_words = ['涨', '好', '看好', '买入', '持有', '乐观', '机会', '利好', '突破', '强势', '龙头', '价值', '增长']
        negative_words = ['跌', '不好', '看空', '卖出', '悲观', '风险', '利空', '破位', '弱势', '割肉', '调整', '下跌']
        
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
        logger.info(f"开始分析雪球 {days} 天的评论数据（演示模式）...")
        
        # 1. 生成模拟数据
        comments = self.generate_mock_data(days)
        logger.info(f"生成了 {len(comments)} 条模拟评论数据")
        
        # 2. 数据清洗
        cleaned_comments = []
        for comment in comments:
            cleaned_text = self.clean_text(comment['text'])
            if cleaned_text and len(cleaned_text) > 3:
                comment['cleaned_text'] = cleaned_text
                cleaned_comments.append(comment)
        
        # 3. 关键词和统计分析
        analysis_data = self.extract_keywords(cleaned_comments)
        
        # 4. 生成总结
        summary = self.generate_summary(analysis_data)
        
        # 5. 统计信息
        user_stats = Counter([c['user'] for c in cleaned_comments])
        top_users = user_stats.most_common(10)
        
        # 6. 生成报告
        report = {
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "analysis_period": f"最近{days}天",
            "total_topics": 1,  # 演示数据
            "total_comments": len(comments),
            "valid_comments": len(cleaned_comments),
            "analysis_data": analysis_data,
            "summary": summary,
            "top_users": top_users,
            "sample_comments": cleaned_comments[:20],  # 保存前20条评论作为样本
            "demo_mode": True
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None):
        """保存分析报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"xueqiu_demo_analysis_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"报告已保存到: {filename}")
        except Exception as e:
            logger.error(f"保存报告失败: {e}")
    
    def print_summary(self, report: Dict[str, Any]):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("雪球评论分析报告（演示版）")
        print("="*60)
        print(f"分析时间: {report.get('analysis_date', 'N/A')}")
        print(f"分析周期: {report.get('analysis_period', 'N/A')}")
        print(f"话题数量: {report.get('total_topics', 0)}")
        print(f"评论总数: {report.get('total_comments', 0)}")
        print(f"有效评论: {report.get('valid_comments', 0)}")
        
        if report.get('demo_mode', False):
            print("⚠️  注意：这是演示模式，使用模拟数据")
        
        print("\n" + report.get('summary', '无分析结果'))
        
        print("\n活跃用户:")
        top_users = report.get('top_users', [])
        for user, count in top_users[:5]:
            print(f"  {user}: {count}条评论")
        
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='雪球评论分析工具（演示版）')
    parser.add_argument('--days', type=int, default=7, help='分析天数 (默认: 7)')
    parser.add_argument('--output', type=str, help='输出文件名')
    parser.add_argument('--config', type=str, default='xueqiu_config.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = XueqiuDemoAnalyzer(args.config)
    
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