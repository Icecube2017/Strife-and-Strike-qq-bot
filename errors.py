class GameError(Exception):
    """游戏错误基类"""
    pass

class PlayerNotFoundError(GameError):
    """玩家未找到"""
    pass

class GameNotFoundError(GameError):
    """游戏未找到"""
    pass

class InvalidOperationError(GameError):
    """非法操作"""
    pass