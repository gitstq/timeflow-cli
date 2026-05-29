"""
数据库管理模块 - 负责SQLite数据库的连接、初始化和操作
Database management module - Handles SQLite connection, initialization and operations
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class Database:
    """SQLite数据库管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为用户目录下的.timeflow/timeflow.db
        """
        if db_path is None:
            home_dir = Path.home()
            data_dir = home_dir / ".timeflow"
            data_dir.mkdir(exist_ok=True)
            self.db_path = str(data_dir / "timeflow.db")
        else:
            self.db_path = db_path
            # 确保目录存在
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = None
        self.cursor = None
        self.connect()
        self.init_tables()
    
    def connect(self):
        """建立数据库连接"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def init_tables(self):
        """初始化数据库表结构"""
        # 任务表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                project TEXT DEFAULT 'default',
                tags TEXT DEFAULT '',
                category TEXT DEFAULT 'other',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 时间记录表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration INTEGER DEFAULT 0,
                notes TEXT DEFAULT '',
                is_pomodoro BOOLEAN DEFAULT 0,
                pomodoro_round INTEGER DEFAULT 0,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
        """)
        
        # 项目表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                color TEXT DEFAULT '#3B82F6',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入默认项目
        self.cursor.execute("""
            INSERT OR IGNORE INTO projects (name, description, color) 
            VALUES ('default', '默认项目 | Default Project', '#3B82F6')
        """)
        
        self.conn.commit()
    
    # ==================== 任务管理 ====================
    
    def create_task(self, name: str, project: str = 'default', 
                    tags: str = '', category: str = 'other') -> int:
        """创建新任务"""
        self.cursor.execute("""
            INSERT INTO tasks (name, project, tags, category)
            VALUES (?, ?, ?, ?)
        """, (name, project, tags, category))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """获取任务详情"""
        self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_task_by_name(self, name: str, project: str = 'default') -> Optional[Dict]:
        """根据名称和项目获取任务"""
        self.cursor.execute(
            "SELECT * FROM tasks WHERE name = ? AND project = ?", 
            (name, project)
        )
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def list_tasks(self, project: Optional[str] = None, 
                   category: Optional[str] = None) -> List[Dict]:
        """列出所有任务"""
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if project:
            query += " AND project = ?"
            params.append(project)
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY updated_at DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_task(self, task_id: int, **kwargs) -> bool:
        """更新任务信息"""
        allowed_fields = ['name', 'project', 'tags', 'category']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        updates['updated_at'] = datetime.now().isoformat()
        
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [task_id]
        
        self.cursor.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    # ==================== 时间记录管理 ====================
    
    def start_timer(self, task_id: int, notes: str = '', 
                    is_pomodoro: bool = False, pomodoro_round: int = 0) -> int:
        """开始计时"""
        now = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO time_entries (task_id, start_time, notes, is_pomodoro, pomodoro_round)
            VALUES (?, ?, ?, ?, ?)
        """, (task_id, now, notes, is_pomodoro, pomodoro_round))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def stop_timer(self, entry_id: int) -> Optional[Dict]:
        """停止计时"""
        now = datetime.now()
        
        # 获取开始时间
        self.cursor.execute(
            "SELECT start_time FROM time_entries WHERE id = ? AND end_time IS NULL",
            (entry_id,)
        )
        row = self.cursor.fetchone()
        
        if not row:
            return None
        
        start_time = datetime.fromisoformat(row['start_time'])
        duration = int((now - start_time).total_seconds())
        
        self.cursor.execute("""
            UPDATE time_entries 
            SET end_time = ?, duration = ?
            WHERE id = ?
        """, (now.isoformat(), duration, entry_id))
        self.conn.commit()
        
        return self.get_time_entry(entry_id)
    
    def get_time_entry(self, entry_id: int) -> Optional[Dict]:
        """获取时间记录详情"""
        self.cursor.execute("SELECT * FROM time_entries WHERE id = ?", (entry_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_active_timer(self) -> Optional[Dict]:
        """获取当前正在运行的计时器"""
        self.cursor.execute("""
            SELECT te.*, t.name as task_name, t.project, t.category
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            WHERE te.end_time IS NULL
            ORDER BY te.start_time DESC
            LIMIT 1
        """)
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def stop_all_timers(self) -> int:
        """停止所有运行的计时器"""
        now = datetime.now()
        
        # 获取所有未停止的计时器
        self.cursor.execute(
            "SELECT id, start_time FROM time_entries WHERE end_time IS NULL"
        )
        active_timers = self.cursor.fetchall()
        
        count = 0
        for timer in active_timers:
            start_time = datetime.fromisoformat(timer['start_time'])
            duration = int((now - start_time).total_seconds())
            
            self.cursor.execute("""
                UPDATE time_entries 
                SET end_time = ?, duration = ?
                WHERE id = ?
            """, (now.isoformat(), duration, timer['id']))
            count += 1
        
        self.conn.commit()
        return count
    
    def list_time_entries(self, task_id: Optional[int] = None,
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         project: Optional[str] = None,
                         limit: int = 100) -> List[Dict]:
        """列出时间记录"""
        query = """
            SELECT te.*, t.name as task_name, t.project, t.category, t.tags
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            WHERE 1=1
        """
        params = []
        
        if task_id:
            query += " AND te.task_id = ?"
            params.append(task_id)
        
        if start_date:
            query += " AND date(te.start_time) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(te.start_time) <= date(?)"
            params.append(end_date)
        
        if project:
            query += " AND t.project = ?"
            params.append(project)
        
        query += " ORDER BY te.start_time DESC LIMIT ?"
        params.append(limit)
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== 统计报表 ====================
    
    def get_daily_stats(self, date: Optional[str] = None) -> Dict:
        """获取每日统计"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute("""
            SELECT 
                COUNT(DISTINCT te.id) as entry_count,
                COALESCE(SUM(te.duration), 0) as total_seconds,
                COUNT(DISTINCT te.task_id) as task_count,
                SUM(CASE WHEN te.is_pomodoro THEN 1 ELSE 0 END) as pomodoro_count
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            WHERE date(te.start_time) = date(?)
        """, (date,))
        
        row = self.cursor.fetchone()
        return {
            'date': date,
            'entry_count': row['entry_count'] or 0,
            'total_seconds': row['total_seconds'] or 0,
            'task_count': row['task_count'] or 0,
            'pomodoro_count': row['pomodoro_count'] or 0
        }
    
    def get_project_stats(self, start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> List[Dict]:
        """获取项目统计"""
        query = """
            SELECT 
                t.project,
                COUNT(DISTINCT te.id) as entry_count,
                COALESCE(SUM(te.duration), 0) as total_seconds,
                COUNT(DISTINCT te.task_id) as task_count
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date(te.start_time) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(te.start_time) <= date(?)"
            params.append(end_date)
        
        query += " GROUP BY t.project ORDER BY total_seconds DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_category_stats(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Dict]:
        """获取分类统计"""
        query = """
            SELECT 
                t.category,
                COUNT(DISTINCT te.id) as entry_count,
                COALESCE(SUM(te.duration), 0) as total_seconds,
                COUNT(DISTINCT te.task_id) as task_count
            FROM time_entries te
            JOIN tasks t ON te.task_id = t.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND date(te.start_time) >= date(?)"
            params.append(start_date)
        
        if end_date:
            query += " AND date(te.start_time) <= date(?)"
            params.append(end_date)
        
        query += " GROUP BY t.category ORDER BY total_seconds DESC"
        
        self.cursor.execute(query, params)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_weekly_report(self, week_start: Optional[str] = None) -> Dict:
        """获取周报数据"""
        if week_start is None:
            # 获取本周一
            today = datetime.now()
            monday = today - timedelta(days=today.weekday())
            week_start = monday.strftime('%Y-%m-%d')
        
        week_end = (datetime.strptime(week_start, '%Y-%m-%d') + 
                   timedelta(days=6)).strftime('%Y-%m-%d')
        
        # 每日统计
        daily_stats = []
        for i in range(7):
            day = (datetime.strptime(week_start, '%Y-%m-%d') + 
                  timedelta(days=i)).strftime('%Y-%m-%d')
            daily_stats.append(self.get_daily_stats(day))
        
        # 项目统计
        project_stats = self.get_project_stats(week_start, week_end)
        
        # 分类统计
        category_stats = self.get_category_stats(week_start, week_end)
        
        # 总计
        total_seconds = sum(day['total_seconds'] for day in daily_stats)
        total_pomodoros = sum(day['pomodoro_count'] for day in daily_stats)
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'total_seconds': total_seconds,
            'total_pomodoros': total_pomodoros,
            'daily_stats': daily_stats,
            'project_stats': project_stats,
            'category_stats': category_stats
        }
    
    # ==================== 项目管理 ====================
    
    def create_project(self, name: str, description: str = '', 
                       color: str = '#3B82F6') -> int:
        """创建新项目"""
        try:
            self.cursor.execute("""
                INSERT INTO projects (name, description, color)
                VALUES (?, ?, ?)
            """, (name, description, color))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return -1  # 项目已存在
    
    def list_projects(self) -> List[Dict]:
        """列出所有项目"""
        self.cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def delete_project(self, name: str) -> bool:
        """删除项目"""
        # 将相关任务移动到默认项目
        self.cursor.execute(
            "UPDATE tasks SET project = 'default' WHERE project = ?",
            (name,)
        )
        
        self.cursor.execute("DELETE FROM projects WHERE name = ?", (name,))
        self.conn.commit()
        return self.cursor.rowcount > 0
