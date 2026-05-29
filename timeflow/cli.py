#!/usr/bin/env python3
"""
TimeFlow CLI - 智能命令行时间追踪工具主入口
Main entry point for TimeFlow CLI
"""

import click
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.live import Live
from rich.align import Align

from .database import Database
from .pomodoro import PomodoroTimer, PomodoroSession, PomodoroState
from .reports import ReportExporter
from .__init__ import __version__

# 初始化 Rich 控制台
console = Console()

# 分类选项
CATEGORIES = [
    'development', 'meeting', 'learning', 'design', 
    'writing', 'research', 'testing', 'planning', 'review', 'other'
]


def get_db():
    """获取数据库实例"""
    return Database()


@click.group()
@click.version_option(version=__version__, prog_name="timeflow")
def cli():
    """
    🕐 TimeFlow CLI - 智能命令行时间追踪工具
    
    A smart command-line time tracking tool with Pomodoro support
    
    快速开始:
        timeflow start "任务名称" --project myproject
        timeflow status
        timeflow stop
    """
    pass


# ==================== 计时命令 ====================

@cli.command()
@click.argument('task_name')
@click.option('--project', '-p', default='default', help='项目名称 | Project name')
@click.option('--tags', '-t', default='', help='标签，逗号分隔 | Tags (comma-separated)')
@click.option('--category', '-c', type=click.Choice(CATEGORIES), default='other',
              help='任务分类 | Task category')
@click.option('--pomodoro', '-pm', is_flag=True, help='使用番茄钟模式 | Use Pomodoro mode')
def start(task_name: str, project: str, tags: str, category: str, pomodoro: bool):
    """
    开始追踪一个任务 | Start tracking a task
    
    示例 | Examples:
        timeflow start "编写代码" --project myapp --category development
        timeflow start "开会" -p work -c meeting --tags "weekly,team"
        timeflow start "专注工作" -pm  # 番茄钟模式
    """
    db = get_db()
    
    # 检查是否有正在运行的计时器
    active = db.get_active_timer()
    if active:
        console.print(f"[yellow]⚠️ 已有正在运行的任务: {active['task_name']} ({active['project']})[/yellow]")
        console.print(f"   请先停止当前任务: [cyan]timeflow stop[/cyan]")
        return
    
    # 查找或创建任务
    task = db.get_task_by_name(task_name, project)
    if not task:
        task_id = db.create_task(task_name, project, tags, category)
        console.print(f"[green]✅ 创建新任务: {task_name}[/green]")
    else:
        task_id = task['id']
        console.print(f"[blue]📋 使用现有任务: {task_name}[/blue]")
    
    if pomodoro:
        # 番茄钟模式
        session = PomodoroSession(db, task_id)
        if session.start():
            console.print(f"[green]🍅 番茄钟开始! 专注25分钟[/green]")
            console.print(f"   任务: [cyan]{task_name}[/cyan] | 项目: [cyan]{project}[/cyan]")
            console.print(f"   使用 [yellow]timeflow pomodoro[/yellow] 查看状态")
        else:
            console.print("[red]❌ 启动番茄钟失败[/red]")
    else:
        # 普通计时模式
        entry_id = db.start_timer(task_id)
        console.print(f"[green]⏱️ 开始计时: {task_name}[/green]")
        console.print(f"   项目: [cyan]{project}[/cyan] | 分类: [cyan]{category}[/cyan]")
        console.print(f"   使用 [yellow]timeflow status[/yellow] 查看状态")


@cli.command()
def stop():
    """
    停止当前追踪 | Stop current tracking
    """
    db = get_db()
    
    active = db.get_active_timer()
    if not active:
        console.print("[yellow]⚠️ 没有正在运行的计时器[/yellow]")
        return
    
    entry = db.stop_timer(active['id'])
    if entry:
        duration = entry['duration']
        minutes = duration // 60
        seconds = duration % 60
        
        console.print(f"[green]✅ 停止计时: {active['task_name']}[/green]")
        console.print(f"   持续时间: [cyan]{minutes}分{seconds}秒[/cyan]")
        
        if entry['is_pomodoro']:
            console.print(f"   [magenta]🍅 完成一个番茄钟![/magenta]")
    else:
        console.print("[red]❌ 停止计时失败[/red]")


@cli.command()
def status():
    """
    查看当前状态 | View current status
    """
    db = get_db()
    
    active = db.get_active_timer()
    if not active:
        console.print("[dim]⏸️ 当前没有正在追踪的任务[/dim]")
        
        # 显示今日统计
        stats = db.get_daily_stats()
        if stats['total_seconds'] > 0:
            console.print(f"\n📊 今日统计 | Today's Stats:")
            console.print(f"   总时长: {format_duration(stats['total_seconds'])}")
            console.print(f"   任务数: {stats['task_count']} | 记录数: {stats['entry_count']}")
        return
    
    # 计算已运行时间
    start_time = datetime.fromisoformat(active['start_time'])
    elapsed = int((datetime.now() - start_time).total_seconds())
    
    # 创建状态面板
    grid = Table.grid(expand=True)
    grid.add_column()
    
    status_text = f"""
[bold cyan]⏱️ 正在追踪 | Currently Tracking[/bold cyan]

任务 | Task: [bold]{active['task_name']}[/bold]
项目 | Project: [cyan]{active['project']}[/cyan]
分类 | Category: [yellow]{active['category']}[/yellow]
已运行 | Elapsed: [green]{format_duration(elapsed)}[/green]
开始时间 | Started: {active['start_time'][:19]}
"""
    
    if active['is_pomodoro']:
        status_text += f"\n[magenta]🍅 番茄钟第 {active['pomodoro_round']} 轮[/magenta]"
    
    panel = Panel(status_text, title="TimeFlow Status", border_style="blue")
    console.print(panel)


# ==================== 番茄钟命令 ====================

@cli.group()
def pomodoro():
    """
    🍅 番茄钟命令 | Pomodoro commands
    """
    pass


@pomodoro.command('start')
@click.argument('task_name')
@click.option('--project', '-p', default='default', help='项目名称 | Project name')
@click.option('--category', '-c', type=click.Choice(CATEGORIES), default='development',
              help='任务分类 | Task category')
def pomodoro_start(task_name: str, project: str, category: str):
    """
    开始番茄钟 | Start a Pomodoro session
    """
    db = get_db()
    
    # 检查是否有正在运行的计时器
    active = db.get_active_timer()
    if active:
        console.print(f"[yellow]⚠️ 已有正在运行的任务[/yellow]")
        return
    
    # 查找或创建任务
    task = db.get_task_by_name(task_name, project)
    if not task:
        task_id = db.create_task(task_name, project, '', category)
    else:
        task_id = task['id']
    
    # 启动番茄钟
    session = PomodoroSession(db, task_id)
    if session.start():
        console.print(f"[green]🍅 番茄钟启动![/green]")
        console.print(f"   任务: [cyan]{task_name}[/cyan]")
        console.print(f"   专注25分钟，然后休息5分钟")
        console.print(f"   使用 [yellow]timeflow pomodoro status[/yellow] 查看进度")
    else:
        console.print("[red]❌ 启动失败[/red]")


@pomodoro.command('status')
def pomodoro_status():
    """
    查看番茄钟状态 | View Pomodoro status
    """
    # 这里简化处理，实际应该维护一个全局会话
    db = get_db()
    active = db.get_active_timer()
    
    if not active or not active['is_pomodoro']:
        console.print("[yellow]没有正在运行的番茄钟[/yellow]")
        return
    
    start_time = datetime.fromisoformat(active['start_time'])
    elapsed = int((datetime.now() - start_time).total_seconds())
    remaining = max(0, 25 * 60 - elapsed)
    progress = min(1.0, elapsed / (25 * 60))
    
    # 进度条
    bar_width = 30
    filled = int(bar_width * progress)
    bar = "█" * filled + "░" * (bar_width - filled)
    
    mins, secs = divmod(remaining, 60)
    
    console.print(f"\n[bold cyan]🍅 番茄钟进行中 | Pomodoro #{active['pomodoro_round']}[/bold cyan]")
    console.print(f"任务: {active['task_name']}")
    console.print(f"\n[{bar}] {progress*100:.1f}%")
    console.print(f"剩余时间: [bold green]{mins:02d}:{secs:02d}[/bold green]")


@pomodoro.command('stop')
def pomodoro_stop():
    """
    停止番茄钟 | Stop Pomodoro session
    """
    db = get_db()
    active = db.get_active_timer()
    
    if not active or not active['is_pomodoro']:
        console.print("[yellow]没有正在运行的番茄钟[/yellow]")
        return
    
    db.stop_timer(active['id'])
    console.print(f"[green]🍅 番茄钟已停止: {active['task_name']}[/green]")


# ==================== 任务管理命令 ====================

@cli.group()
def task():
    """
    📋 任务管理 | Task management
    """
    pass


@task.command('list')
@click.option('--project', '-p', help='按项目筛选 | Filter by project')
@click.option('--category', '-c', type=click.Choice(CATEGORIES), help='按分类筛选 | Filter by category')
def task_list(project: Optional[str], category: Optional[str]):
    """
    列出所有任务 | List all tasks
    """
    db = get_db()
    tasks = db.list_tasks(project=project, category=category)
    
    if not tasks:
        console.print("[dim]暂无任务 | No tasks found[/dim]")
        return
    
    table = Table(title="📋 任务列表 | Task List")
    table.add_column("ID", style="dim", width=6)
    table.add_column("任务名 | Name", style="cyan")
    table.add_column("项目 | Project", style="green")
    table.add_column("分类 | Category", style="yellow")
    table.add_column("标签 | Tags", style="magenta")
    
    for task in tasks:
        table.add_row(
            str(task['id']),
            task['name'],
            task['project'],
            task['category'],
            task['tags'] or '-'
        )
    
    console.print(table)


@task.command('add')
@click.argument('name')
@click.option('--project', '-p', default='default', help='项目名称')
@click.option('--tags', '-t', default='', help='标签')
@click.option('--category', '-c', type=click.Choice(CATEGORIES), default='other', help='分类')
def task_add(name: str, project: str, tags: str, category: str):
    """
    添加新任务 | Add a new task
    """
    db = get_db()
    
    existing = db.get_task_by_name(name, project)
    if existing:
        console.print(f"[yellow]⚠️ 任务已存在: {name}[/yellow]")
        return
    
    task_id = db.create_task(name, project, tags, category)
    console.print(f"[green]✅ 任务已创建 (ID: {task_id}): {name}[/green]")


@task.command('delete')
@click.argument('task_id', type=int)
def task_delete(task_id: int):
    """
    删除任务 | Delete a task
    """
    db = get_db()
    
    task = db.get_task(task_id)
    if not task:
        console.print(f"[red]❌ 任务不存在: {task_id}[/red]")
        return
    
    if click.confirm(f"确定删除任务 '{task['name']}'?"):
        db.delete_task(task_id)
        console.print(f"[green]✅ 任务已删除[/green]")


# ==================== 项目管理命令 ====================

@cli.group()
def project():
    """
    📁 项目管理 | Project management
    """
    pass


@project.command('list')
def project_list():
    """
    列出所有项目 | List all projects
    """
    db = get_db()
    projects = db.list_projects()
    
    table = Table(title="📁 项目列表 | Project List")
    table.add_column("名称 | Name", style="cyan")
    table.add_column("描述 | Description", style="green")
    table.add_column("颜色 | Color")
    
    for proj in projects:
        color = proj['color'] or '#3B82F6'
        table.add_row(
            proj['name'],
            proj['description'] or '-',
            f"[{color}]■[/{color}] {color}"
        )
    
    console.print(table)


@project.command('add')
@click.argument('name')
@click.option('--description', '-d', default='', help='项目描述')
@click.option('--color', '-c', default='#3B82F6', help='项目颜色 (HEX)')
def project_add(name: str, description: str, color: str):
    """
    添加新项目 | Add a new project
    """
    db = get_db()
    
    project_id = db.create_project(name, description, color)
    if project_id > 0:
        console.print(f"[green]✅ 项目已创建: {name}[/green]")
    else:
        console.print(f"[yellow]⚠️ 项目已存在: {name}[/yellow]")


# ==================== 报表命令 ====================

@cli.group()
def report():
    """
    📊 报表与导出 | Reports and exports
    """
    pass


@report.command('today')
def report_today():
    """
    显示今日报告 | Show today's report
    """
    db = get_db()
    exporter = ReportExporter(db)
    
    report_data = exporter.generate_daily_report()
    
    console.print(f"\n[bold cyan]📅 今日报告 | Daily Report: {report_data['date']}[/bold cyan]\n")
    
    # 总览
    console.print(Panel(f"""
[bold]总时长 | Total:[/bold] {report_data['total_formatted']}
[bold]任务数 | Tasks:[/bold] {report_data['task_count']}
[bold]记录数 | Entries:[/bold] {report_data['entry_count']}
[bold]番茄钟 | Pomodoros:[/bold] {report_data['pomodoro_count']}
    """, title="Overview", border_style="green"))
    
    # 项目分布
    if report_data['by_project']:
        console.print("\n[bold]📁 项目分布 | By Project:[/bold]")
        for proj, duration in report_data['by_project'].items():
            console.print(f"   • {proj}: [cyan]{duration}[/cyan]")
    
    # 分类分布
    if report_data['by_category']:
        console.print("\n[bold]🏷️ 分类分布 | By Category:[/bold]")
        for cat, duration in report_data['by_category'].items():
            console.print(f"   • {cat}: [yellow]{duration}[/yellow]")


@report.command('week')
def report_week():
    """
    显示本周报告 | Show weekly report
    """
    db = get_db()
    exporter = ReportExporter(db)
    
    report_data = exporter.generate_weekly_report()
    
    console.print(f"\n[bold cyan]📊 周报 | Weekly Report[/bold cyan]")
    console.print(f"周期 | Period: {report_data['week_start']} ~ {report_data['week_end']}\n")
    
    console.print(f"[bold]总时长 | Total:[/bold] {report_data['total_formatted']}")
    console.print(f"[bold]番茄钟 | Pomodoros:[/bold] {report_data['total_pomodoros']}\n")
    
    # 每日统计
    console.print("[bold]📅 每日统计 | Daily Stats:[/bold]")
    table = Table()
    table.add_column("日期 | Date", style="cyan")
    table.add_column("时长 | Duration", style="green")
    table.add_column("记录数 | Entries", style="yellow")
    table.add_column("番茄钟 | Pomodoros", style="magenta")
    
    for day in report_data['daily_stats']:
        table.add_row(
            day['date'],
            day['formatted'],
            str(day['entry_count']),
            str(day['pomodoro_count'])
        )
    
    console.print(table)


@report.command('export')
@click.option('--format', '-f', 'format_type', type=click.Choice(['json', 'csv', 'md']), 
              default='json', help='导出格式 | Export format')
@click.option('--output', '-o', help='输出路径 | Output path')
@click.option('--start', '-s', help='开始日期 (YYYY-MM-DD)')
@click.option('--end', '-e', help='结束日期 (YYYY-MM-DD)')
@click.option('--project', '-p', help='项目筛选 | Project filter')
def report_export(format_type: str, output: Optional[str], start: Optional[str], 
                  end: Optional[str], project: Optional[str]):
    """
    导出时间记录 | Export time entries
    
    示例 | Examples:
        timeflow report export -f json
        timeflow report export -f csv -o ~/exports/mytime.csv
        timeflow report export -f md -s 2025-01-01 -e 2025-01-31
    """
    db = get_db()
    exporter = ReportExporter(db)
    
    # 确定输出路径
    if not output:
        output = exporter.get_export_path(format_type)
    
    # 导出
    try:
        if format_type == 'json':
            exporter.export_json(output, start, end, project)
        elif format_type == 'csv':
            exporter.export_csv(output, start, end, project)
        elif format_type == 'md':
            exporter.export_markdown(output, start, end, project)
        
        console.print(f"[green]✅ 导出成功 | Export successful:[/green]")
        console.print(f"   路径 | Path: [cyan]{output}[/cyan]")
    except Exception as e:
        console.print(f"[red]❌ 导出失败 | Export failed: {e}[/red]")


# ==================== 历史记录命令 ====================

@cli.command()
@click.option('--limit', '-n', default=20, help='显示条数 | Number of entries')
@click.option('--project', '-p', help='项目筛选 | Filter by project')
def history(limit: int, project: Optional[str]):
    """
    查看历史记录 | View history
    """
    db = get_db()
    entries = db.list_time_entries(project=project, limit=limit)
    
    if not entries:
        console.print("[dim]暂无记录 | No entries found[/dim]")
        return
    
    table = Table(title=f"📜 最近 {len(entries)} 条记录 | Recent Entries")
    table.add_column("时间 | Time", style="dim", width=16)
    table.add_column("任务 | Task", style="cyan")
    table.add_column("项目 | Project", style="green")
    table.add_column("时长 | Duration", style="yellow")
    table.add_column("🍅", width=3)
    
    for entry in entries:
        start = entry['start_time'][5:16]  # MM-DD HH:MM
        duration = format_duration(entry['duration'])
        pomodoro = "🍅" if entry['is_pomodoro'] else ""
        
        table.add_row(
            start,
            entry['task_name'],
            entry['project'],
            duration,
            pomodoro
        )
    
    console.print(table)


# ==================== 辅助函数 ====================

def format_duration(seconds: int) -> str:
    """格式化时长显示"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h{minutes}m"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"


def main():
    """主入口函数"""
    cli()


if __name__ == '__main__':
    main()
