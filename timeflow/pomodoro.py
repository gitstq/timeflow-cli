"""
番茄工作法模块 - Pomodoro Technique Implementation
支持标准25/5分钟工作休息循环
"""

import time
import threading
from enum import Enum
from typing import Optional, Callable
from dataclasses import dataclass


class PomodoroState(Enum):
    """番茄钟状态"""
    IDLE = "idle"           # 空闲
    WORKING = "working"     # 工作中
    SHORT_BREAK = "short_break"  # 短休息
    LONG_BREAK = "long_break"    # 长休息
    PAUSED = "paused"       # 暂停


@dataclass
class PomodoroConfig:
    """番茄钟配置"""
    work_duration: int = 25 * 60      # 工作时长（秒）
    short_break: int = 5 * 60         # 短休息（秒）
    long_break: int = 15 * 60         # 长休息（秒）
    rounds_before_long_break: int = 4  # 几个番茄后长休息


class PomodoroTimer:
    """番茄钟计时器"""
    
    def __init__(self, config: Optional[PomodoroConfig] = None):
        self.config = config or PomodoroConfig()
        self.state = PomodoroState.IDLE
        self.current_round = 0
        self.remaining_seconds = 0
        self.total_work_seconds = 0
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._on_tick_callbacks: List[Callable[[int, int], None]] = []
        self._on_complete_callbacks: List[Callable[[PomodoroState], None]] = []
        self._on_state_change_callbacks: List[Callable[[PomodoroState], None]] = []
    
    def on_tick(self, callback: Callable[[int, int], None]):
        """注册每秒 tick 回调 (remaining, total)"""
        self._on_tick_callbacks.append(callback)
    
    def on_complete(self, callback: Callable[[PomodoroState], None]):
        """注册阶段完成回调"""
        self._on_complete_callbacks.append(callback)
    
    def on_state_change(self, callback: Callable[[PomodoroState], None]):
        """注册状态变更回调"""
        self._on_state_change_callbacks.append(callback)
    
    def _notify_tick(self, remaining: int, total: int):
        """通知 tick 回调"""
        for callback in self._on_tick_callbacks:
            try:
                callback(remaining, total)
            except Exception:
                pass
    
    def _notify_complete(self, state: PomodoroState):
        """通知完成回调"""
        for callback in self._on_complete_callbacks:
            try:
                callback(state)
            except Exception:
                pass
    
    def _notify_state_change(self, state: PomodoroState):
        """通知状态变更回调"""
        for callback in self._on_state_change_callbacks:
            try:
                callback(state)
            except Exception:
                pass
    
    def _set_state(self, state: PomodoroState):
        """设置状态并通知"""
        self.state = state
        self._notify_state_change(state)
    
    def start_work(self) -> bool:
        """开始工作"""
        if self.state in [PomodoroState.WORKING, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            return False
        
        self._stop_event.clear()
        self._pause_event.clear()
        self.remaining_seconds = self.config.work_duration
        self._set_state(PomodoroState.WORKING)
        self._start_timer_thread()
        return True
    
    def start_break(self) -> bool:
        """开始休息"""
        if self.state != PomodoroState.WORKING:
            return False
        
        self.current_round += 1
        
        if self.current_round % self.config.rounds_before_long_break == 0:
            self.remaining_seconds = self.config.long_break
            self._set_state(PomodoroState.LONG_BREAK)
        else:
            self.remaining_seconds = self.config.short_break
            self._set_state(PomodoroState.SHORT_BREAK)
        
        return True
    
    def pause(self) -> bool:
        """暂停"""
        if self.state not in [PomodoroState.WORKING, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            return False
        
        self._pause_event.set()
        self._set_state(PomodoroState.PAUSED)
        return True
    
    def resume(self) -> bool:
        """恢复"""
        if self.state != PomodoroState.PAUSED:
            return False
        
        self._pause_event.clear()
        
        # 恢复到之前的状态
        if self.remaining_seconds > self.config.short_break:
            self._set_state(PomodoroState.WORKING)
        elif self.remaining_seconds > self.config.long_break:
            self._set_state(PomodoroState.SHORT_BREAK)
        else:
            self._set_state(PomodoroState.LONG_BREAK)
        
        return True
    
    def stop(self) -> bool:
        """停止"""
        if self.state == PomodoroState.IDLE:
            return False
        
        self._stop_event.set()
        self._set_state(PomodoroState.IDLE)
        
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join(timeout=1)
        
        return True
    
    def skip(self) -> bool:
        """跳过当前阶段"""
        if self.state == PomodoroState.IDLE:
            return False
        
        self._stop_event.set()
        
        # 根据当前状态决定下一步
        if self.state == PomodoroState.WORKING:
            self.start_break()
        else:
            self._set_state(PomodoroState.IDLE)
        
        return True
    
    def _start_timer_thread(self):
        """启动计时线程"""
        self._timer_thread = threading.Thread(target=self._timer_loop)
        self._timer_thread.daemon = True
        self._timer_thread.start()
    
    def _timer_loop(self):
        """计时器主循环"""
        total_seconds = self.remaining_seconds
        
        while self.remaining_seconds > 0 and not self._stop_event.is_set():
            # 等待暂停恢复
            while self._pause_event.is_set() and not self._stop_event.is_set():
                time.sleep(0.1)
            
            if self._stop_event.is_set():
                break
            
            self._notify_tick(self.remaining_seconds, total_seconds)
            time.sleep(1)
            self.remaining_seconds -= 1
            
            if self.state == PomodoroState.WORKING:
                self.total_work_seconds += 1
        
        if not self._stop_event.is_set():
            self._notify_complete(self.state)
    
    def get_progress(self) -> float:
        """获取当前进度 (0.0 - 1.0)"""
        if self.state == PomodoroState.IDLE:
            return 0.0
        
        if self.state == PomodoroState.WORKING:
            total = self.config.work_duration
        elif self.state == PomodoroState.SHORT_BREAK:
            total = self.config.short_break
        elif self.state == PomodoroState.LONG_BREAK:
            total = self.config.long_break
        else:
            return 0.0
        
        return 1.0 - (self.remaining_seconds / total)
    
    def format_remaining(self) -> str:
        """格式化剩余时间"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            'state': self.state.value,
            'current_round': self.current_round,
            'remaining_seconds': self.remaining_seconds,
            'total_work_seconds': self.total_work_seconds,
            'progress': self.get_progress(),
            'formatted_time': self.format_remaining()
        }


class PomodoroSession:
    """番茄钟会话管理"""
    
    def __init__(self, db, task_id: int):
        self.db = db
        self.task_id = task_id
        self.timer = PomodoroTimer()
        self.current_entry_id: Optional[int] = None
        
        # 绑定回调
        self.timer.on_complete(self._on_phase_complete)
    
    def _on_phase_complete(self, state: PomodoroState):
        """阶段完成回调"""
        if state == PomodoroState.WORKING:
            # 工作阶段完成，记录时间
            if self.current_entry_id:
                self.db.stop_timer(self.current_entry_id)
                self.current_entry_id = None
    
    def start(self) -> bool:
        """开始番茄钟会话"""
        if not self.timer.start_work():
            return False
        
        # 开始数据库计时
        self.current_entry_id = self.db.start_timer(
            self.task_id,
            is_pomodoro=True,
            pomodoro_round=self.timer.current_round + 1
        )
        
        return True
    
    def stop(self) -> bool:
        """停止番茄钟会话"""
        # 停止计时器
        self.timer.stop()
        
        # 停止数据库计时
        if self.current_entry_id:
            self.db.stop_timer(self.current_entry_id)
            self.current_entry_id = None
        
        return True
    
    def get_status(self) -> dict:
        """获取当前状态"""
        timer_stats = self.timer.get_stats()
        timer_stats['entry_id'] = self.current_entry_id
        return timer_stats
