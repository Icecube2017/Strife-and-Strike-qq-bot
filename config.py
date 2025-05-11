from dataclasses import dataclass
from typing import Dict, List, Tuple
from enum import Enum

class GameStatus(Enum):
    """游戏状态枚举"""
    WAITING = 0    # 等待开始
    PLAYING = 1    # 游戏中
    FINISHED = 2   # 已结束
    PAUSED = 3     # 已暂停
    CANCELED = 4   # 已取消

@dataclass
class GameConfig:
    """游戏配置"""
    SAVE_PATH: str = "saves"
    DEFAULT_DECK: str = "basic"
    MAX_CARDS: int = 6
    MIN_PLAYERS: int = 2
    
@dataclass 
class SkillConfig:
    """技能配置"""
    IGNORE: Tuple[str] = ("黯星", "恋慕", "卿别", "时雨", "敏博士", "赐弥")
    EXCLUSIVE: Tuple[str] = ("屠杀", "氤氲", "窃梦者", "冰芒", "异镜解构", "数据传输")
    OUT_OF_TURN: Tuple[str] = ("相转移", "恐吓", "阈限", "沉默", "最后的希望", "不死", "止杀")

class GameContext:
    """游戏提示文本"""
    # 账号相关
    NOT_REGISTERED: str = "还没有注册账户哦"
    
    # 游戏状态相关
    GAME_WAITING: str = "已有对局正在准备哦"
    GAME_NOT_PLAYED: str = "当前没有正在进行的对局哦" 
    GAME_STARTED: str = "对局已经开始了哦"
    GAME_NOT_STARTED: str = "对局还没有开始哦"
    GAME_TYPE_UNCONFIRMED: str = "还没有指定对局类型哦"
    GAME_TYPE_ERROR: str = "指定的对局类型无效哦"
    
    # 玩家操作相关
    GAME_NOT_JOINED: str = "你还没有加入对局哦"
    CANT_CANCEL: str = "你不是对局发起人，不可以取消对局哦"
    CANT_PAUSE: str = "你不是对局发起人，不可以暂停对局哦" 
    CANT_START: str = "你不是对局发起人，不可以开始对局哦"
    CANT_QUIT: str = "你是对局发起人，不可以退出哦"
    
    # 角色相关
    CHARACTER_ERROR: str = "该角色不存在哦"
    CHARACTER_CHOSEN: str = "该角色已经被选择了哦"
    CHARACTER_BANNED: str = "该角色已经被禁用了哦"
    CHARACTER_BAN_OUT: str = "角色禁用位已经满了哦"
    CHARACTER_NOT_BANNED: str = "该角色没有被禁用哦"
    
    # 队伍相关
    GAME_NOT_TEAM: str = "当前对局不是团队战哦"
    GAME_NOT_JOIN_TEAM: str = "你还没加入任何队伍哦"
    
    # 卡牌相关 
    DECK_ERROR: str = "该卡包不存在哦"
    DECK_USING: str = "该卡包正在使用哦"
    
    # 游戏验证相关
    PLAYER_TOO_LESS: str = "玩家人数小于2，不能开始对局哦"
    TEAM_TOO_LESS: str = "队伍数量小于2，不能开始对局哦"
    PLAYER_UNASSIGNED: str = "还有玩家没有选好角色哦"
    PLAYER_SOLITUDE: str = "还有玩家没有加入队伍哦"