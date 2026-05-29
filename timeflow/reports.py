"""
报表导出模块 - 支持多种格式导出时间追踪数据
Report export module - Supports multiple formats for time tracking data
"""

import json
import csv
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class ReportExporter:
    """报表导出器"""
    
    CATEGORIES = {
        'development': '💻 开发 | Development',
        'meeting': '👥 会议 | Meeting',
        'learning': '📚 学习 | Learning',
        'design': '🎨 设计 | Design',
        'writing': '✍️ 写作 | Writing',
        'research': '🔍 研究 | Research',
        'testing': '🧪 测试 | Testing',
        'planning': '📋 规划 | Planning',
        'review': '👀 审查 | Review',
        'other': '📌 其他 | Other'
    }
    
    def __init__(self, db):
        self.db = db
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """格式化时长"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    @staticmethod
    def format_duration_decimal(seconds: int) -> float:
        """格式化为小数小时"""
        return round(seconds / 3600, 2)
    
    def export_json(self, output_path: str, start_date: Optional[str] = None,
                   end_date: Optional[str] = None, project: Optional[str] = None) -> str:
        """导出为JSON格式"""
        entries = self.db.list_time_entries(
            start_date=start_date,
            end_date=end_date,
            project=project,
            limit=10000
        )
        
        # 添加格式化后的时长
        for entry in entries:
            entry['duration_formatted'] = self.format_duration(entry['duration'])
            entry['duration_hours'] = self.format_duration_decimal(entry['duration'])
        
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': start_date or 'all',
                'end': end_date or 'all'
            },
            'project': project or 'all',
            'summary': {
                'total_entries': len(entries),
                'total_seconds': sum(e['duration'] for e in entries),
                'total_hours': round(sum(e['duration'] for e in entries) / 3600, 2)
            },
            'entries': entries
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return output_path
    
    def export_csv(self, output_path: str, start_date: Optional[str] = None,
                  end_date: Optional[str] = None, project: Optional[str] = None) -> str:
        """导出为CSV格式"""
        entries = self.db.list_time_entries(
            start_date=start_date,
            end_date=end_date,
            project=project,
            limit=10000
        )
        
        fieldnames = [
            'id', 'task_name', 'project', 'category', 'tags',
            'start_time', 'end_time', 'duration_seconds', 'duration_formatted',
            'is_pomodoro', 'pomodoro_round', 'notes'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for entry in entries:
                writer.writerow({
                    'id': entry['id'],
                    'task_name': entry['task_name'],
                    'project': entry['project'],
                    'category': entry['category'],
                    'tags': entry['tags'],
                    'start_time': entry['start_time'],
                    'end_time': entry['end_time'] or 'running',
                    'duration_seconds': entry['duration'],
                    'duration_formatted': self.format_duration(entry['duration']),
                    'is_pomodoro': entry['is_pomodoro'],
                    'pomodoro_round': entry['pomodoro_round'],
                    'notes': entry['notes']
                })
        
        return output_path
    
    def export_markdown(self, output_path: str, start_date: Optional[str] = None,
                       end_date: Optional[str] = None, project: Optional[str] = None) -> str:
        """导出为Markdown格式"""
        entries = self.db.list_time_entries(
            start_date=start_date,
            end_date=end_date,
            project=project,
            limit=10000
        )
        
        # 按日期分组
        entries_by_date: Dict[str, List[Dict]] = {}
        for entry in entries:
            date = entry['start_time'][:10]  # YYYY-MM-DD
            if date not in entries_by_date:
                entries_by_date[date] = []
            entries_by_date[date].append(entry)
        
        # 生成Markdown
        lines = [
            "# 📊 TimeFlow 时间追踪报告 | Time Tracking Report",
            "",
            f"**生成时间 | Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**报告周期 | Period:** {start_date or '全部 | All'} ~ {end_date or '全部 | All'}",
            f"**项目筛选 | Project:** {project or '全部 | All'}",
            "",
            "---",
            "",
            "## 📈 概览 | Overview",
            "",
            f"- **总记录数 | Total Entries:** {len(entries)}",
            f"- **总时长 | Total Duration:** {self.format_duration(sum(e['duration'] for e in entries))}",
            f"- **总小时数 | Total Hours:** {round(sum(e['duration'] for e in entries) / 3600, 2)}h",
            "",
            "---",
            "",
        ]
        
        # 按日期详细记录
        for date in sorted(entries_by_date.keys(), reverse=True):
            day_entries = entries_by_date[date]
            day_total = sum(e['duration'] for e in day_entries)
            
            lines.extend([
                f"## 📅 {date}",
                "",
                f"**当日总计 | Daily Total:** {self.format_duration(day_total)}",
                "",
                "| 任务 | 项目 | 分类 | 时长 | 番茄钟 |",
                "|------|------|------|------|--------|",
            ])
            
            for entry in day_entries:
                pomodoro = "🍅" if entry['is_pomodoro'] else ""
                lines.append(
                    f"| {entry['task_name']} | {entry['project']} | "
                    f"{entry['category']} | {self.format_duration(entry['duration'])} | {pomodoro} |"
                )
            
            lines.append("")
        
        # 项目统计
        lines.extend([
            "---",
            "",
            "## 📁 项目统计 | Project Statistics",
            "",
            "| 项目 | 记录数 | 总时长 |",
            "|------|--------|--------|",
        ])
        
        project_stats = self.db.get_project_stats(start_date, end_date)
        for stat in project_stats:
            lines.append(
                f"| {stat['project']} | {stat['entry_count']} | "
                f"{self.format_duration(stat['total_seconds'])} |"
            )
        
        # 分类统计
        lines.extend([
            "",
            "## 🏷️ 分类统计 | Category Statistics",
            "",
            "| 分类 | 记录数 | 总时长 |",
            "|------|--------|--------|",
        ])
        
        category_stats = self.db.get_category_stats(start_date, end_date)
        for stat in category_stats:
            category_label = self.CATEGORIES.get(
                stat['category'], 
                f"📌 {stat['category']}"
            )
            lines.append(
                f"| {category_label} | {stat['entry_count']} | "
                f"{self.format_duration(stat['total_seconds'])} |"
            )
        
        lines.extend([
            "",
            "---",
            "",
            "*由 TimeFlow CLI 生成 | Generated by TimeFlow CLI*",
            ""
        ])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return output_path
    
    def generate_daily_report(self, date: Optional[str] = None) -> Dict:
        """生成日报"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        stats = self.db.get_daily_stats(date)
        entries = self.db.list_time_entries(start_date=date, end_date=date, limit=1000)
        
        # 按项目分组
        by_project: Dict[str, int] = {}
        by_category: Dict[str, int] = {}
        
        for entry in entries:
            project = entry['project']
            category = entry['category']
            duration = entry['duration']
            
            by_project[project] = by_project.get(project, 0) + duration
            by_category[category] = by_category.get(category, 0) + duration
        
        return {
            'date': date,
            'total_seconds': stats['total_seconds'],
            'total_formatted': self.format_duration(stats['total_seconds']),
            'entry_count': stats['entry_count'],
            'task_count': stats['task_count'],
            'pomodoro_count': stats['pomodoro_count'],
            'by_project': {k: self.format_duration(v) for k, v in by_project.items()},
            'by_category': {k: self.format_duration(v) for k, v in by_category.items()}
        }
    
    def generate_weekly_report(self, week_start: Optional[str] = None) -> Dict:
        """生成周报"""
        report = self.db.get_weekly_report(week_start)
        
        # 格式化
        report['total_formatted'] = self.format_duration(report['total_seconds'])
        
        for day in report['daily_stats']:
            day['formatted'] = self.format_duration(day['total_seconds'])
        
        for project in report['project_stats']:
            project['formatted'] = self.format_duration(project['total_seconds'])
        
        for category in report['category_stats']:
            category['formatted'] = self.format_duration(category['total_seconds'])
        
        return report
    
    def get_export_path(self, format_type: str, prefix: str = "timeflow") -> str:
        """获取导出文件路径"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{prefix}_{timestamp}.{format_type}"
        
        # 默认导出到用户目录
        export_dir = Path.home() / ".timeflow" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        return str(export_dir / filename)
