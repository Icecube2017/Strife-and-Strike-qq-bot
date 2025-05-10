# -*- coding:utf-8 -*-

import pickle, time, random

from pathlib import Path
from typing import Union
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

import assets, classes
from config import GameStatus, SkillConfig, GameContext

# 初始化游戏存档系统，记录已经进行/正在进行的游戏局次
game_history: List[Union[int, Dict[int, List[str]]]] = [
    0,
    {0: ["000000-0000"]},
]  # [已经进行/正在进行/中途取消的游戏场数, 群号:[局次id]]
# 定义存档目录
saves_path = Path(__file__).parent / "saves"
# 导入日志模块
log = classes.Logger("debug")
# 读取/新建游戏局次列表
try:
    with open(saves_path / "saves.pkl", mode="rb") as _temp:
        game_history = pickle.load(_temp)
except FileNotFoundError:
    with open(saves_path / "saves.pkl", "wb") as _temp:
        pickle.dump(game_history, _temp)


# 群号 + 游戏实例
# 此处储存了正在进行的对局
playing_games: Dict[str, classes.Game] = {}
# 暂时存储对局初始状态和对局最终状态
game_temp: Dict[str, List[classes.Game]] = {}
# 自带技能角色忽略技能抽取

class SkillPrefiner:
    IGNORE = ["黯星", "恋慕", "卿别", "时雨", "敏博士", "赐弥"]
    EXCLUSIVE: Dict[str, str] = {
        "黯星": "屠杀",
        "恋慕": "氤氲",
        "卿别": "窃梦者",
        "时雨": "冰芒",
        "敏博士": "异镜解构",
        "赐弥": "数据传输",
    }
    # 回合外释放的技能
    OUT_OF_TURN: List[str] = [
        "相转移",
        "恐吓",
        "阈限",
        "沉默",
        "最后的希望",
        "不死",
        "止杀",
    ]

# 初始化常量
CTX = GameContext()
SKL = SkillConfig()

# 随机字符串生成器 参数为字符串长度
def random_string(length: int = 4):
    string = "1234567890abcdefghijklmnopqrstuvwxyz1234567890"
    ret = ""
    for i in range(length):
        ret += random.choice(string)
    return ret


# 新建对局
@log
def new_game(gid: str, starter_qq: str, game_type: int = -1) -> str:
    try:
        sender_name = assets.accounts[starter_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
        
    try:
        if playing_games[gid]:
            return CTX.GAME_WAITING
    except KeyError:
        if game_type == -1:
            return CTX.GAME_TYPE_UNCONFIRMED
            
    try:
        type_name = ("个人战", "团队战", "Boss战")[game_type]
    except IndexError:
        return CTX.GAME_TYPE_ERROR
    game_id = "{t}-{s}".format(
        t=time.strftime("%y%m%d", time.localtime()), s=random_string()
    )  # 通过日期和随机字符串确定对局id
    playing_games[gid] = classes.Game(
        game_id=game_id, starter_qq=starter_qq, game_type=game_type
    )  # 将游戏实例加入游戏列表
    playing_games[gid].character_available = assets.CHARACTER
    for _key in assets.CHARACTER:
        playing_games[gid].character_status[_key] = 0
    playing_games[gid].deck_name = "basic"
    playing_games[gid].deck = assets.PROPCARD["basic"].copy()
    playing_games[gid].skill_deck = assets.SKILL
    playing_games[gid].add_player_without_return(starter_qq)
    # game_temp[game_id] = playing_games[gid]
    return f"{assets.accounts[starter_qq]} 发起的 Strife & Strike {type_name} 开始招募选手了！对局id为{game_id}"


# 保存对局状态及对局过程日志
def save_game(id: str, is_complete: bool, is_canceled: bool = False):
    pass


# 取消未开始的/正在进行的对局
@log
def cancel_game(gid: str, sender_qq: str) -> str:
    try:
        sender_name = assets.accounts[sender_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    if game_now.starter_qq != sender_qq:  # 比较命令发送者和实际发起者qq号 下同
        return CTX.CANT_CANCEL
    if game_now.game_status == GameStatus.WAITING:  # 对局未开始
        playing_games.pop(gid)
        return f"对局 {game_now.game_id} 取消成功！"
    elif game_now.game_status == GameStatus.PLAYING:  # 对局进行中
        if game_now.cancel_ensure == 1:
            game_now.cancel_ensure -= 1
            return "请再次发送指令以取消对局"
        if game_now.cancel_ensure == 0:  # 二次确认取消正在进行的对局
            game_now.game_status = GameStatus.CANCELED
            # game_temp[game_now.game_id][1] = game_now
            game_now.save(False, True)
            playing_games.pop(gid)
            return f"对局 {game_now.game_id} 取消成功，存档和记录已保存"


# 暂停对局 将状态储存至本地
@log
def pause_game(gid: str, sender_qq: str) -> str:
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    if game_now.starter_qq != sender_qq:
        return CTX.CANT_PAUSE
    if game_now.game_status == GameStatus.WAITING:
        return CTX.GAME_WAITING
    game_now.game_status = GameStatus.PAUSED
    game_temp[game_now.game_id][1] = game_now
    save_game(game_now.game_id, False)
    return f"对局 {game_now.game_id} 暂停成功"


# 加入群内对局
@log
def join_game(gid: str, player_qq: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    return game_now.add_player(player_qq)


def quit_game(gid: str, player_qq: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:  # 确认玩家是否在对局中 否则不执行
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.starter_qq == player_qq:
        return CTX.CANT_QUIT
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    return game_now.move_player(player_qq)


@log
def set_character(gid: str, player_qq: str, character: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    if character not in game_now.character_available:
        return CTX.CHARACTER_ERROR
    if game_now.character_status[character] == 1:  # 该角色的状态为1（被选择）
        return CTX.CHARACTER_CHOSEN
    if game_now.character_status[character] == 2:  # 该角色的状态为2（被禁用）
        return CTX.CHARACTER_BANNED
    return game_now.set_character(player_qq, character)


@log
def ban_character(gid: str, player_qq: str, character: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    if character not in game_now.character_available:
        return CTX.CHARACTER_ERROR
    if game_now.character_status[character] == 1:
        return CTX.CHARACTER_CHOSEN
    if game_now.character_status[character] == 2:
        return CTX.CHARACTER_BANNED
    if len(_player.banned) >= game_now.ban_num:
        return CTX.CHARACTER_BAN_OUT
    return game_now.ban_character(player_qq, character)


@log
def unban_character(gid: str, player_qq: str, character: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    if character not in game_now.character_available:
        return CTX.CHARACTER_ERROR
    if game_now.character_status[character] == 1:
        return CTX.CHARACTER_CHOSEN
    if game_now.character_status[character] == 0:
        return CTX.CHARACTER_NOT_BANNED
    return game_now.unban_character(player_qq, character)


@log
def set_ban_num(gid: str, player_qq: str, num: int):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    return game_now.set_ban_number(num)


@log
def set_team(gid: str, player_qq: str, name: str = ""):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    if game_now.game_type != 1:
        return CTX.GAME_NOT_TEAM
    try:
        _team = game_now.teams[name]
    except KeyError:
        return game_now.create_team(player_qq, name)
    return game_now.set_team(player_qq, name)


@log
def quit_team(gid: str, player_qq: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    if game_now.game_type != 1:
        return CTX.GAME_NOT_TEAM
    if not _player.team:
        return CTX.GAME_NOT_JOIN_TEAM
    if len(game_now.teams[_player.team]) == 1:
        return game_now.delete_team(player_qq)
    return game_now.quit_team(player_qq)


@log
def set_deck(gid: str, player_qq: str, deck_name: str = ""):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    try:
        deck = assets.PROPCARD[deck_name]
    except KeyError:
        return CTX.DECK_ERROR
    if game_now.deck_name == deck_name:
        return CTX.DECK_USING
    return game_now.set_deck(deck_name)


# 开始游戏
@log
def start_game(gid: str, player_qq: str) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    if game_now.starter_qq != player_qq:
        return CTX.CANT_START
    if game_now.player_count < 2:
        return CTX.PLAYER_TOO_LESS
    if game_now.game_status == GameStatus.PLAYING:
        return CTX.GAME_STARTED
    for pl in game_now.players.values():
        if not pl.character.id:
            return CTX.PLAYER_UNASSIGNED
    if game_now.game_type == 0:
        pass
    elif game_now.game_type == 1:
        if game_now.team_count < 2:
            return CTX.TEAM_TOO_LESS
        for pl in game_now.players.values():
            if not pl.team:
                return CTX.PLAYER_SOLITUDE
    return game_now.start_game(player_qq)


@log
def draw(gid: str, player_qq: str) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    _card = _player.get_hand()
    _rst = "当前的手牌有："
    for _c in _card:
        _rst += _c + " "
    _rst += "\n当前的技能有："
    _skill = _player.skill.keys()
    for _s in list(_skill):
        _rst += _s + " "
    return _rst


@log
def play_card(
    gid: str, player_qq: str, target_list: list, card: list = None, extra: list = None
) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    if game_now.game_sequence[game_now.turn - 1] != _player.id:
        return "现在不是你出牌哦"
    if _player.has_played_card:
        return "你已经出过牌了哦"
    has_player = 0  # 判断出牌的对象（玩家名或角色名）是否存在
    _tg_qq_list = []
    for _tgs in target_list:
        for _tg_pl in game_now.players.values():
            if _tg_pl.name == _tgs or _tg_pl.character.id == _tgs:
                has_player += 1
                _tg_qq_list.append(_tg_pl.qq)
    if has_player < len(target_list):
        return "出牌的对象有的不存在哦"
    try:  # 判断是否不携带道具
        _c0 = card[0]
    except IndexError:
        return game_now.play_card(player_qq, _tg_qq_list, [], [])
    std_card = []  # 将输入的卡牌名转换为标准化名称
    _pl_card = _player.get_hand()
    for _c in card:
        _std_c = assets.match_alias(_c)
        if _std_c == 'none':
            return "出的卡牌里有的不存在哦"
        try:
            _pl_card.remove(_std_c)
        except ValueError:
            return "你手里没有这张牌哦"
        std_card.append(_std_c)
    return game_now.play_card(player_qq, _tg_qq_list, std_card, extra)


@log
def play_skill(
    gid: str, player_qq: str, target_list: list, skill: str, extra: list = None
) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    if not _player.has_skill(skill):
        return "你没有这个技能哦"
    if (
        game_now.game_sequence[game_now.turn - 1] != _player.id
        and not skill in SKL.OUT_OF_TURN
    ):
        return "现在不可以使用技能哦"
    has_player = 0  # 判断出牌的对象（玩家名或角色名）是否存在
    _tg_qq_list = []
    for _tgs in target_list:
        for _tg_pl in game_now.players.values():
            if _tg_pl.name == _tgs or _tg_pl.character.id == _tgs:
                has_player += 1
                _tg_qq_list.append(_tg_pl.qq)
    if has_player < len(target_list):
        return "技能使用的对象有的不存在哦"
    return game_now.play_skill(
        player_qq, _tg_qq_list, skill, extra
    )  # 未完成 检查extra是否为合法输入


@log
def play_trait(
    gid: str, player_qq: str, target_list: list, trait: str, extra: list = None
) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    if not _player.has_trait(trait):
        return "你没有这个特质哦"
    if game_now.game_sequence[game_now.turn - 1] != _player.id:
        return "现在不可以使用特质哦"
    has_player = 0  # 判断出牌的对象（玩家名或角色名）是否存在
    _tg_qq_list = []
    for _tgs in target_list:
        for _tg_pl in game_now.players.values():
            if _tg_pl.name == _tgs or _tg_pl.character.id == _tgs:
                has_player += 1
                _tg_qq_list.append(_tg_pl.qq)
    if has_player < len(target_list):
        return "特质使用的对象有的不存在哦"
    return game_now.play_trait(player_qq, _tg_qq_list, trait, extra)


@log
def fold_card(gid: str, player_qq: str, cards: list) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    if game_now.game_sequence[game_now.turn - 1] != _player.id:
        return "现在还没到你弃牌哦"
    std_card = []  # 将输入的卡牌名转换为标准化名称
    for _c in cards:
        _std_c = assets.match_alias(_c)
        std_card.append(_std_c)
        if _std_c == "none":
            return "弃的卡牌里有的不存在哦"
        if not _player.has_card(_std_c):
            return "你手里没有这张牌哦"
    return game_now.fold_card(player_qq, std_card)


@log
def pass_turn(gid: str, player_qq: str) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    if game_now.game_sequence[game_now.turn - 1] != _player.id:
        return "现在不是你出牌哦"
    if _player.count_card() > _player.card_max:
        return "手牌太多了，需要弃到不多于六张牌哦"
    return game_now.end_turn()


def start_turn(gid: str) -> str:
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    return game_now.start_turn()


def player_info(gid: str, player_qq: str) -> str:
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    return game_now.player_info()


def set_skill(gid: str, player_qq: str, skill: str):
    try:
        sender_name = assets.accounts[player_qq]
    except KeyError:
        return CTX.NOT_REGISTERED
    try:
        game_now = playing_games[gid]
    except KeyError:
        return CTX.GAME_NOT_PLAYED
    try:
        _player = game_now.players[player_qq]
    except KeyError:
        return CTX.GAME_NOT_JOINED
    if game_now.game_status != GameStatus.PLAYING:
        return CTX.GAME_NOT_STARTED
    _player.skill[skill] = 0
    _player.skill_status[skill] = 0
    return f"设置玩家技能为{skill}"


"""start_game(1000, "希尔")
new_game(1000, "希尔", 1810940687, 1)
join_game(1000, "Icecube", 1851556514)
start_game(1000, "Icecube")
start_game(1000, "希尔")
set_character(1000, "希尔", "晴箬")
set_character(1000, "希尔", "洛尔")
set_character(1000, "Icecube", "abcd")
set_character(1000, "Icecube", "冰块")
set_team(1000, "希尔", "Icecube")
set_team(1000, "Icecube", "2")
set_team(1000, "Icecube", "晴箬")
start_game(1000, "希尔")
set_team(1000, "Icecube")
set_team(1000, "Icecube", "1")
set_team(1000, "Icecube")
cancel_game(1000, "希尔")
"""
