# -*- coding:utf-8 -*-
import random, math,time

from typing import List, Dict
from pathlib import Path

import assets
from assets import accounts, MAP

# 自带技能角色忽略技能抽取
CHARA_EXCLUSIVE: Dict[str, str] = {"黯星": "屠杀", "恋慕": "氤氲", "卿别": "窃梦者", "时雨": "冰芒", "敏博士": "异镜解构", "赐弥": "数据传输"}
SKILL_EXCLUSIVE: Dict[str, int] = {"屠杀": 0, "氤氲": 4, "冰芒": 1,  "异镜解构": 3, "数据传输": -2} # 数据传输CD动态变化
# 可叠加的状态
STATUS_STACKABLE: list = []

def dice(size: int, times: int = 1) -> int:
    _d: int = 0
    for i in range(times):
        _d += random.randint(1, size)
    return _d



class Logger(object):
    def __init__(self, level: str) -> None:
        self.level = f"[{level.upper()}]"

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            __LOG_PATH = Path(__file__).parent / "logs"
            _rst = func(*args, **kwargs)
            with open(__LOG_PATH / f"log-{time.strftime("%Y-%m-%d")}.txt", 'a', encoding="utf-8") as f:
                f.write(f'{self.level} {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} {_rst}\n')
            f.close()
            return _rst
        return wrapper


# 定义角色类
class Character:
    def __init__(
            self, id: str = "", max_hp: int = 0, attack: int = 0, defense: int = 0,
            max_move: int = 0, move_regenerate: int = 0, regenerate_type: int = 0, regenerate_turns: int = 1
    ) -> None:
        self.id = id
        self.hp = max_hp # 角色生命值
        self.max_hp = max_hp # 角色最大生命
        self.attack = attack # 角色攻击力
        self.defense = defense # 角色防御力
        self.armor: int = 0  # 角色护甲值

        # self.damage: Damage = Damage()
        self.damage_received_total: int = 0 # 角色受到的总伤害
        self.damage_dealt_total: int = 0 # 角色造成的总伤害
        self.damage_dealt_round: int = 0  # 角色每回合造成的伤害

        self.move_point: int = 0 # 角色行动点
        self.max_move = max_move # 角色最大行动点
        self.move_regenerate = move_regenerate # 角色行动点回复量
        self.regenerate_type = regenerate_type # 角色行动点回复类型
        self.regenerate_turns = regenerate_turns # 角色行动点回复频率

        self.status: Dict[str, List[int]] = {}  # 角色状态，存储状态名和持续时间
        self.status_layers: Dict[str, int] = {} # 存储可堆叠状态的层数
        self.hidden_status: Dict[str, List[int]] = {} # 一些未写明是状态，但实际上依靠状态实现的效果

        #self.extra: List = [] # 储存额外数据 已弃用，改为用
        # hidden_status存放

# 定义玩家类
class Player:
    def __init__(
            self, qq: str, id: int = 0
            # skill_1: str = "", skill_1_cd: int = 0, skill_2: str = "", skill_2_cd: int = 0, skill_3: str = "", skill_3_cd: int = 0
    ) -> None:  # 初始化玩家数据
        self.id = id  # 玩家编号
        self.name: str = '' # 玩家昵称
        self.qq = qq  # 玩家openid
        self.team: str = ''  # 玩家所在队伍id

        self.character: Character = Character()  # 传入角色数据
        self.banned: List[str] = [] # 玩家禁用角色列表

        self.skill: Dict[str, int] = {} # 玩家技能，存储技能名与冷却时间
        self.skill_status: Dict[str, int] = {} # 判断技能是否被释放过

        self.card_count = 0  # 玩家手牌数量
        self.card: List[str] = []  # 初始化玩家手牌
        self.card_max = 6 # 玩家手牌上限

        self.has_played_card: bool = False # 玩家本回合是否出过牌

        self.is_dead: bool = False
        self.data_temp: list = []

    '''def regenerate(self, round: int) -> None:            # 行动点回复方法
        if round == 0:
            pass
        if round % self.character.regenerate_turns == 0:
            _move_temp = self.character.move_point
            self.character.move_point += self.character.move_regenerate
            if self.character.move_point > self.character.max_move:
                self.character.move_point = self.character.max_move'''


    '''def move_init(self) -> None:
        _rt = self.character.regenerate_type
        _c = self.character
        if _rt == 0:
            _c.move_point = _c.move_regenerate
        elif _rt == 1:
            _c.move_point = 3
        elif _rt == 2:
            _c.move_point = _c.max_move
        elif _rt == 3:
            _c.move_point = math.ceil(float(self.card_count) / 2)
        elif _rt == 4:
            _c.move_point = _c.max_move'''

    def count_card(self) -> int:
        self.card_count = len(self.card)
        return self.card_count

    def has_card(self, card: str) -> bool:  # 判断玩家是否持有手牌
        return True if card in self.card else False

    def remove_card(self, card: str):
        self.card.remove(card)

    def get_hand(self) -> list:
        _rst = []
        for _c in self.card:
            _rst.append(_c)
        return _rst

    def clear_hand(self):
        self.card.clear()

    def set_max_card(self, num: int):
        self.card_max = num

    def has_skill(self, skill: str) -> bool:
        return True if skill in self.skill.keys() else False

    def has_trait(self, trait: str) -> bool: # 未完成
        return True if trait in assets.TRAIT[self.id] else False

    def set_character(self, c: list) -> str:  # 设置玩家角色
        self.character = Character(*c)
        if c[0] == "洛尔":
            self.character.attack = 60 + dice(4, 2) * 5
            self.character.defense = 25 + dice(6) * 5
        return f"{self.name} 选择了角色 {c[0]}"

    def has_status(self, status: str) -> bool:
        return True if status in self.character.status.keys() else False

    def has_hidden_status(self, status: str) -> bool:
        return True if status in self.character.hidden_status.keys() else False

    def get_status_duration(self, status: str) -> int:
        try:
            _ret = self.character.status[status][0]
        except KeyError:
            _ret = 0
        return _ret

    '''def play_card(self, *card: str):
        if not self._has_card(card):
            return f"你的手上没有 {card} 哦"
        self.card.remove(card)
        return None'''

    '''def add_attribute(self, attribute: str, value: int):
        if attribute == "attack":
            self.character.attack += value
        elif attribute == "defense":
            self.character.defense += value
        elif attribute == "max_hp":
            self.character.max_hp += value
        elif attribute == "move_point":
            self.character.move_point += value'''

    def player_info(self) -> str:
        self.count_card()
        _c = self.character
        if not self.team:
            _t = "无"
        else:
            _t = self.team
        _st = ""
        if not _c.status:
            _st = "无 "
        else:
            for _k, _v in _c.status.items():
                _d = _v[0] # 状态持续时间
                if _d < 0:
                    _st += f"{_k}(∞) "
                else:
                    _st += f"{_k}({_d}) "
        for _k, _v in _c.hidden_status.items():
            _d = _v[0]  # 状态持续时间
            if _d < 0:
                _st += f"{_k}(∞) "
            else:
                _st += f"{_k}({_d}) "
        _sk = ""
        for _k, _v in self.skill.items():
            if self.skill_status[_k] == 1:
                _sk += f"{_k}({_v}) "
        _ret = f'''{_c.id}({self.name}):  手牌:{self.card_count}  队伍:{_t}\nhp:{_c.hp}({_c.armor})/{_c.max_hp}  atk:{_c.attack}  def:{_c.defense}\nmp:{_c.move_point}/{_c.max_move}  状态:{_st}  技能:{_sk}\n'''
        return _ret


EMPTY_PLAYER = Player('123', -1856)

"""
class Scene:
    pass
"""
        

# 定义boss类
class Boss:
    def __init__(
            self, max_hp: int = 0, attack: int = 0, defense: int = 0,
            # skill_1: str = "", skill_1_cd: int = 0, skill_2: str = "", skill_2_cd: int = 0, skill_3: str = "", skill_3_cd: int = 0
    ) -> None:
        self.name: str = ""
        self.health_point = max_hp
        self.max_health = max_hp
        self.attack = attack
        self.defense = defense

        self.skill: Dict[str, int] = {}

        self.status: List[int] = []


# 定义队伍类
'''class Team:
    def __init__(self, *players) -> None:
        self.team_member: List[str] = list(players)  # 队伍成员'''

# 定义事件类
class Action:
    def __init__(self, target: Player, source: Player = EMPTY_PLAYER, action_type: str = 'damage', name: str = '',
                 damage_point: int = 0, damage_type: str = 'physical', is_pierce: bool = False,
                 is_aoe: bool = False, is_void: bool = False, is_track: bool = False, is_penetrate: bool = False):
        self.source = source
        self.target = target
        self.type = action_type  # 有action, skill, trait, damage, heal
        self.damage_type: str = damage_type # 有physical, fire, ice 等
        self.name: str = name # 技能或特质的名称

        #type=action
        self.is_aoe: bool = is_aoe # 群攻（对部分角色无效）
        self.is_pierce: bool = is_pierce # 无敌贯通（无视护甲，战斗续行）
        self.is_hplost: bool = False # 生命流失（无来源）
        self.is_void: bool = is_void # 实际不造成伤害
        self.is_track: bool = is_track # 无视闪避
        self.is_penetrate: bool = is_penetrate # 无视护盾
        self.is_fission: bool = False
        self.fission_target: Player = EMPTY_PLAYER

        #type=skill
        self.is_silenced: bool = False # 是否被沉默
        self.target_list: List[Player] = [] #   技能的多个目标

        self.damage_point: int = damage_point

        self.dice_size: int = 4
        self.dice_point: int = 1
        self.attack_plus: int = 0
        self.attack_multi: float = 1
        self.damage_plus: int = 0
        self.damage_multi: float = 1

    def dice_multi(self):
        self.dice_point = dice(self.dice_size, 1)

    def calculate(self):
        source_atk = (self.attack_plus + self.source.character.attack) *  self.attack_multi
        _ret = ((source_atk - self.target.character.defense)
                * self.dice_point + self.damage_plus) * self.damage_multi
        _ret = round(_ret)
        if source_atk - self.target.character.defense < 0:
            _ret = round(source_atk * 0.1 + 5)
        if _ret < 0:
            _ret = 0
        return _ret

    def set_damage_point(self, value: int):
        self.damage_point = value

EMPTY_ACTION = Action(EMPTY_PLAYER)

# 定义游戏类
class Game:
    def __init__(self, game_id: str, starter_qq: str, game_type: int) -> None:
        self.game_id = game_id  # 局次id作为每场对局的唯一识别码
        self.starter_qq = starter_qq  #发起人openid
        self.game_type = game_type  # 对局类型:0-个人战 1-团队战 2-Boss战

        self.game_status: int = 0  # 游戏状态:0-准备阶段 1-进行中 2-已结束 3-暂停中 4-中途取消
        self.game_sequence: List[int] = []  # 出牌次序
        self.player_count: int = 0  # 玩家数量
        self.round: int = 0  # 游戏轮次
        self.turn: int = 0  # 玩家轮次，1代表第一位玩家，以此类推

        self.players: Dict[str, Player] = {}  # 玩家列表(openid + 玩家实例)
        self.died: Dict[str, Player] = {}  # 阵亡列表
        self.team_count: int = 0  # 队伍数量
        self.teams: Dict[str, list] = {}  # 队伍id和队伍列表
        self.scene_on: bool = False  # 场景是否开启
        self.scene: str = ""  # 场景名称

        self.deck_name: str = "basic_prop"
        self.deck: List[str] = []  # 摸牌堆
        self.discard: List[str] = []  # 出牌堆
        self.skill_deck: Dict[str, int] = {}  # 技能及已获取技能
        self.skill_banned: List[str] = []
        self.character_available: Dict[str, list] = {}  # 可用角色
        self.character_status: Dict[str, int] = {}  # 角色状态（0=可用,1=被占用,2=禁用）
        self.ban_num: int = 1 # ban位个数

        # self.current_action: Action = 0
        self.action_stack: List[Action] = [] # 行动阶段的技能栈
        self.action_stack_post: List[Action] = [] # 回合结束的技能栈
        self.skill_stack: List[Action] = []
        self.dice_stack: List = []

        self.cancel_ensure: int = 1  # 确认取消对局
        self.data_temp: dict = {}  # 储存额外数据

    def add_player(self, player_qq: str):
        self.players[player_qq] = Player(qq=player_qq, id=self.player_count + 1)
        self.players[player_qq].name = accounts[player_qq]
        self.player_count += 1
        return f"{assets.accounts[player_qq]} 加入了对局 {self.game_id}\n目前已有 {self.player_count} 名玩家"

    def add_player_without_return(self, player_qq: str):
        self.players[player_qq] = Player(qq=player_qq, id=self.player_count + 1)
        self.players[player_qq].name = accounts[player_qq]
        self.player_count += 1

    def move_player(self, player_qq: str):
        _id = self.players[player_qq].id
        for player in self.players.values():   # 更改其余玩家的编号
            if player.id > _id:
                player.id -= 1
        self.player_count -= 1  # 对局玩家总数
        if self.game_type == 1:  # 团队战模式中移出团队
            self.quit_team(player_qq)
        self.players.pop(player_qq)  # 将玩家移出对局
        return f"{assets.accounts[player_qq]} 退出了对局 {self.game_id}\n目前还有 {self.player_count} 名玩家"

    def set_character(self, player_qq: str, character: str):
        _player = self.players[player_qq]
        if _player.character.id:  # 玩家已选择角色时
            self.character_status[_player.character.id] = 0 # 玩家选择的上一个角色变为可用
        self.character_status[character] = 1 # 玩家当前角色被占用
        return _player.set_character(self.character_available[character])

    def ban_character(self, player_qq: str, character: str):
        self.players[player_qq].banned.append(character)
        self.character_status[character] = 2 # 禁用该角色
        return f"已禁用角色 {character}"

    def unban_character(self, player_qq: str, character: str):
        self.players[player_qq].banned.remove(character)
        self.character_status[character] = 0  # 使该角色可用
        return f"{character} 目前可用"

    def set_ban_number(self, num: int):
        self.ban_num = num
        return f"当前可禁用角色个数为{num}个"

    def save(self, is_complete: bool, is_canceled: bool = False):
        pass

    def create_team(self, player_qq: str, name: str):
        self.team_count += 1
        self.teams[name] = [player_qq]
        self.players[player_qq].team = name
        return f"{accounts[player_qq]} 创建了队伍 {name}！"

    def set_team(self, player_qq: str, name: str):
        self.teams[name].append(player_qq)
        self.players[player_qq].team = name
        return f"{accounts[player_qq]} 加入了队伍 {name}！"

    def quit_team(self, player_qq: str):
        _player = self.players[player_qq]
        self.teams[_player.team].remove(player_qq)
        _name = _player.team
        _player.team = ''
        return f"{accounts[player_qq]} 退出了队伍 {_name}！"

    def delete_team(self, player_qq: str):
        self.team_count -= 1
        _player = self.players[player_qq]
        _name = _player.team
        _player.team = ''
        self.teams.pop(_name)
        return f"队伍 {_name} 人数为0，已自动解散！"

    def choose_skill(self, player_qq: str) -> str:
        _pl = self.players[player_qq]
        _s = ""
        while not _s and _s not in self.skill_banned:
            _s = random.choice(list(self.skill_deck.keys()))
        _pl.skill[_s] = 0
        _pl.skill_status[_s] = 0
        self.skill_banned.append(_s)
        return _s

    def set_deck(self, deck_name: str):
        self.deck_name = deck_name
        self.deck = assets.PROPCARD[deck_name].copy()
        return f"卡包变更为 {deck_name} ！"

    def start_game(self, player_qq: str):
        self.game_status = 1
        self.round = 1
        self.turn = 1
        return self._init_game()

    def add_card(self, player_qq: str, card: str, add_type: str = 'draw'): # add_type为未完成字段
        self.players[player_qq].card.append(card)

    def remove_card(self, player_qq: str, card: str, remove_type: str = 'discard'):
        self.players[player_qq].card.remove(card)

    @staticmethod
    def has_tag(card: str, tag: str):
        return True if tag in assets.TAG[card] else False

    def draw(self, player_qq: str, num: int):
        _ret = []
        for i in range(num):
            _c = self.deck.pop()
            self.add_card(player_qq, _c)
            self.players[player_qq].count_card()
            _ret.append(_c)
        return _ret

    def get_player_from_id(self, num: int):
        for _pl in self.players.values():
            if _pl.id == num:
                return _pl
        return None

    def get_player_from_chara(self, character: str):
        for _pl in self.players.values():
            if _pl.character.id == character:
                return _pl
        return None

    def _init_game(self):
        _rst = ""
        random.shuffle(self.deck)
        self.game_sequence = [i for i in range(1, self.player_count + 1)]
        # random.shuffle(self.game_sequence)
        _rst += "战斗开始！出牌顺序如下——\n"
        for qq, _pl in self.players.items():  # 选择技能
            if _pl.character.id not in [k for k in CHARA_EXCLUSIVE.keys()]:
                _s1, _s2 = self.choose_skill(qq), self.choose_skill(qq)
            else:
                _pl.skill[CHARA_EXCLUSIVE[_pl.character.id]] = 0
                _pl.skill_status[CHARA_EXCLUSIVE[_pl.character.id]] = 0
            _c = self.draw(qq, 2) # 分发起始手牌
            if _pl.character.id == MAP['chinro']:
                self.add_hidden_status(_pl.qq, 'encourage', -1) # 保存特质状态，0为未发动，1为发动
            if _pl.character.id == MAP['neko']:
                self.play_trait(_pl.qq, trait=MAP['distinct_road']) # 妮卡欧“明晰的来时路”特质开局发动
            if _pl.character.id == MAP['darkstar']:
                self.add_hidden_status(_pl.qq, 'massacre', -1)
            if _pl.character.id == MAP['sumoggu']:
                self.add_hidden_status(_pl.qq, 'alcohol', -1) # 保存酒水点数
        self.start_turn()
        _rst += self.player_info()
        return _rst

    def player_info(self):
        _rst = f'回合：{self.round} 轮次：{self.turn}\n'
        for i in self.game_sequence:
            for pl in self.players.values():
                if i == pl.id:
                    _rst += pl.player_info()
        return _rst

    def dice(self, player_qq: str, size: int, times: int):
        _d: int = 0
        for i in range(times):
            _d += random.randint(1, size)

        return _d

    def player_died(self, player_qq: str):
        _pl = self.players[player_qq]
        _ret = f"{_pl.character.id} 已阵亡……\n"
        self.died[player_qq] = _pl
        _pl.is_dead = True

        # self.players.pop(player_qq)
        return _ret

    def add_attribute(self, player_qq: str, attribute: str, value: int):
        _pl = self.players[player_qq]
        if attribute == "attack":
            _pl.character.attack += value
        elif attribute == "defense":
            _pl.character.defense += value
        elif attribute == 'max_hp':
            _pl.character.max_hp += value
        elif attribute == 'armor':
            _pl.character.armor += value
        elif attribute == "move_point":
            _pl.character.move_point += value
        elif attribute == 'health':
            _pl.character.hp += value

    def move_init(self, player_qq: str):
        _pl = self.players[player_qq]
        _rt = _pl.character.regenerate_type
        _mr = _pl.character.move_regenerate
        _c = _pl.character
        if _rt == 0:
            _mr = _c.move_regenerate
        elif _rt == 1:
            pass
        elif _rt == 2:
            _mr = _c.max_move
        elif _rt == 3:
            _mr = math.ceil(float(_pl.card_count) / 2)
        elif _rt == 4:
            _mr = _c.max_move
        if _pl.has_status(MAP['slowness']):
            _mr -= 1
        if _pl.has_status(MAP['swift']):
            _mr += 1
        self.add_attribute(player_qq, 'move_point', _mr)

    def move_regenerate(self, player_qq: str):
        _pl = self.players[player_qq]
        _rt = _pl.character.regenerate_type
        _mr = 0
        _c = _pl.character
        if _rt == 0: # 设置行动点回复量
            _mr = _c.move_regenerate
        elif _rt == 1:
            pass
        elif _rt == 2:
            _mr = _c.max_move
        elif _rt == 3:
            _mr = math.ceil(float(_pl.card_count) / 2)
        elif _rt == 4:
            pass
        if _pl.has_status(MAP['slowness']): # 迟缓效果结算
            _mr -= 1
        if _pl.has_status(MAP['swift']): # 迅捷效果结算
            _mr += 1
        if _c.max_move - _c.move_point < _mr:  # 防止行动点溢出
            _mr = _c.max_move - _c.move_point
        if (self.round - 1) % _c.regenerate_turns == 0 and (_rt == 0 or _rt == 3):
            self.add_attribute(player_qq, 'move_point', _mr)
        if _c.move_point == 0 and _rt == 2:
            self.add_attribute(player_qq, 'move_point', _mr)

    def add_status(self, player_qq: str, status: str, duration: int):
        _pl = self.players[player_qq]
        is_immune = False
        if status not in STATUS_STACKABLE:
            if status in [MAP['frost'], MAP['frozen']] and _pl.character.id == MAP['shigure']:
                self.play_trait(player_qq, trait=MAP['icy_blood'])
            if _pl.has_hidden_status('ice_immunity'):
                is_immune = True
                self.remove_hidden_status(player_qq, 'ice_immunity')
            if not is_immune:
                try:
                    _pl.character.status[status][0] += duration  # 储存持续回合数
                    _pl.character.status[status][1] += duration * self.player_count
                except KeyError:
                    _pl.character.status[status] = [0, 0, 0]
                    _pl.character.status[status][0] = duration
                    _pl.character.status[status][1] = duration * self.player_count
                    if status == MAP['frozen']:
                        _pl.character.status[status][1] += 1 # 保证轮到该玩家时冰封效果仍存在
                    if status == MAP['frost']:
                        self.add_attribute(player_qq, 'attack', -20)
                    elif status == MAP['strength']:
                        self.add_attribute(player_qq, 'attack', 15)
                    elif status == MAP['strength_ii']:
                        self.add_attribute(player_qq, 'attack', 30)
                    elif status == MAP['exhausted']:
                        self.add_attribute(player_qq, 'attack', -(_pl.character.hidden_status['aurora'][2]))
                    elif status == MAP['fragility']:
                        self.add_attribute(player_qq, 'defense', -15)
                    elif status == MAP['weakness']:
                        self.add_attribute(player_qq, 'attack', -15)
                    elif status == MAP['cold']:
                        self.add_attribute(player_qq, 'attack', -5)
                    elif status == MAP['cold_ii']:
                        self.add_attribute(player_qq, 'attack', -10)
        else:
            pass

    def remove_status(self, player_qq: str, status: str):
        _pl = self.players[player_qq]
        _pl.character.status.pop(status)
        if status == MAP['frost']:
            self.add_attribute(player_qq, 'attack', 20)
        elif status == MAP['strength']:
            self.add_attribute(player_qq, 'attack', -15)
        elif status == MAP['strength_ii']:
            self.add_attribute(player_qq, 'attack', -30)
        elif status == MAP['exhausted']:
            self.add_attribute(player_qq, 'attack', _pl.character.hidden_status['aurora'][2])
            self.remove_hidden_status(player_qq, 'aurora')
        elif status == MAP['fragility']:
            self.add_attribute(player_qq, 'defense', 15)
        elif status == MAP['weakness']:
            self.add_attribute(player_qq, 'attack', 15)
        elif status == MAP['cold']:
            self.add_attribute(player_qq, 'attack', 5)
        elif status == MAP['cold_ii']:
            self.add_attribute(player_qq, 'attack', 10)

    def add_hidden_status(self, player_qq: str, status: str, duration: int):
        _pl = self.players[player_qq]
        if status not in STATUS_STACKABLE:
            try:
                _pl.character.hidden_status[status][0] += duration
                _pl.character.hidden_status[status][1] += duration * self.player_count
            except KeyError:
                _pl.character.hidden_status[status] = [0, 0, 0]
                _pl.character.hidden_status[status][0] = duration
                _pl.character.hidden_status[status][1] = duration * self.player_count
                if status == 'hero_legend':
                    self.add_attribute(player_qq, 'attack', 10)
                elif status == 'dream_shelter':
                    self.add_attribute(player_qq, 'defense', 10)
                elif status == 'spirit_bind':
                    self.add_attribute(player_qq, 'attack', -10)
                    self.add_attribute(player_qq, 'defense', -10)
        else:
            pass

    def remove_hidden_status(self, player_qq: str, status: str):
        _pl = self.players[player_qq]
        _pl.character.hidden_status.pop(status)
        if status == 'hero_legend':
            self.add_attribute(player_qq, 'attack', -10)
        elif status == 'dream_shelter':
            self.add_attribute(player_qq, 'defense', -10)
        elif status == 'spirit_bind':
            self.add_attribute(player_qq, 'attack', 10)
            self.add_attribute(player_qq, 'defense', 10)

    def recall(self, card: str):
        self.discard.append(card)
        return

    def recharge(self):
        random.shuffle(self.discard)
        self.deck.extend(self.discard)
        self.discard.clear()
        return

    def play_card(self, player_qq: str, target_qq_list: list, cards: list, extra: list):
        _pl = self.players[player_qq]
        _cost = 0  # 计算行动点消耗
        for _c in cards:
            _cost += 1
            if _pl.has_hidden_status('non_flying'):
                _cost += 1
            if _c == MAP['rest']:
                _cost -= 2
        if not cards:
            _cost = 1
            if _pl.has_hidden_status('non_flying'):
                _cost += 1
        if _cost > _pl.character.move_point:
            return "你的行动点不足哦"
        if not 'fission' in _pl.character.hidden_status and len(target_qq_list) > 1:
            return "你不能同时攻击多个玩家哦"
        _ret = ''
        target_qq = target_qq_list[0]
        _tg = self.players[target_qq]
        target2_qq = '' # 分裂技能攻击的对象
        _tg2 = ''
        if len(target_qq_list) > 1:
            target2_qq = target_qq_list[1]
            _tg2 = self.players[target2_qq]
        if not cards:
            _ret += f'{_pl.character.id} 对 {_tg.character.id} 发起了攻击！\n'
            self.add_attribute(player_qq, 'move_point', -_cost)
            self.action_stack.append(Action(_tg, _pl, 'action')) # 事件栈入栈action实例
            _pl.has_played_card = True
            if 'fission' in _pl.character.hidden_status.keys() and len(target_qq_list) > 1:
                _ret += f'{_pl.character.id} 对 {_tg2.character.id} 发起了攻击！\n'
                self.action_stack[0].is_fission = True
                self.action_stack[0].fission_target = _tg2
            _act_dice = self.dice(player_qq, self.action_stack[0].dice_size, 1)
            self.action_stack[0].dice_point = _act_dice
            _ret += f'命运的骰子显现了结果，朝上的点数是 {_act_dice} ！\n'
            return _ret
        else:
            card_str = ''
            ext_ind = 0 # extra数据下标
            self.add_attribute(player_qq, 'move_point', -_cost)
            self.action_stack.append(Action(_tg, _pl, action_type='action')) # 事件栈入栈action实例
            for _c in cards:
                if player_qq == target_qq and _c not in [MAP['curing'], MAP['regenerating']]:
                    return f'你不能对自己出牌哦'
            _pl.has_played_card = True
            for _c in cards:
                card_str += (_c + ' ')
            _ret += f'{_pl.character.id} 对 {_tg.character.id} 使用了 {card_str}！\n'
            if 'fission' in _pl.character.hidden_status.keys() and len(target_qq_list) > 1:
                _ret += f'{_pl.character.id} 对 {_tg2.character.id} 使用了 {card_str}！\n'
                self.action_stack[0].is_fission = True
                self.action_stack[0].fission_target = _tg2
            _extra_ind = 0
            for _c in cards:
                self.remove_card(player_qq, _c) # 玩家手牌移除卡牌
                self.discard.append(_c) # 出牌堆加入卡牌
            if _pl.character.id == MAP['ting_xinyu']:
                self.play_trait(player_qq, target_qq_list, MAP['aurelysium'], cards)
            for _c in cards:
                card_able = True
                if _pl.character.id == MAP['ting_xinyu'] and len(assets.TAG[_c]) >= 2:
                    card_able = False
                if card_able:
                    if _c == MAP['end_crystal']:
                        _hp_dice = self.dice(player_qq, 4, 2)
                        _dmg_dice = self.dice(player_qq, 8, 1)
                        self.action_stack.append(Action(_pl, action_type='damage', damage_point=30 + 15 * _hp_dice))
                        for _tgs in self.players.values():
                            if _tgs != _pl:
                                self.action_stack.append(Action(_tgs, _pl, action_type='damage', damage_type='magical',
                                                                damage_point=40 + 15 * _dmg_dice, is_aoe=True))
                        _ret += f'破片水晶的生命损失点数为 {_hp_dice} ，伤害点数为 {_dmg_dice} ！\n'
                    elif _c == MAP['hero_legend']:
                        self.add_hidden_status(player_qq, 'hero_legend', -100)
                        self.action_stack.append(Action(_pl, _pl, action_type='heal', damage_point=100))
                    elif _c == MAP['wood_sword']:
                        self.add_attribute(player_qq, 'attack', 10)
                    elif _c == MAP['dream_shelter']:
                        self.add_hidden_status(player_qq, 'dream_shelter', -100)
                        self.action_stack.append(Action(_pl, _pl, action_type='heal', damage_point=100))
                    elif _c == MAP['shield']:
                        self.add_attribute(player_qq, 'armor', 100)
                        self.add_attribute(player_qq, 'defense', 5)
                    elif _c == MAP['ascension_stair']:
                        _min_d = 100
                        _max_d = 0
                        tg_list: list[Player] = []
                        for _tgs in self.players.values():
                            _d = self.dice(_tgs.qq, 6, 1)
                            _ret += f'混乱力场迸发，{_tgs.character.id} 的魔能点数为 {_d} ！\n'
                            if _d < _min_d:
                                _min_d = _d
                                tg_list.clear()
                                tg_list.append(_tgs)
                            elif _d == _min_d:
                                tg_list.append(_tgs)
                            if _d > _max_d:
                                _max_d = _d
                        for _tgs2 in tg_list:
                            self.action_stack.append(Action(_tgs2, _pl, action_type='damage', damage_type='magical',
                                                            damage_point=50 * _max_d, is_aoe=True))
                    elif _c == MAP['critical_strike']:
                        self.action_stack[0].is_pierce = True
                    elif _c == MAP['curing']:
                        self.action_stack.append(Action(_pl, _pl, action_type='heal', damage_point=120))
                        self.action_stack[0].is_void = True
                    elif _c == MAP['regenerating']:
                        self.add_status(player_qq, MAP['regeneration'], 2)
                        self.action_stack[0].is_void = True
                    elif _c == MAP['strength_spell']:
                        self.add_status(player_qq, MAP['strength'], 2)
                    elif _c == MAP['strength_spell_ii']:
                        self.add_status(player_qq, MAP['strength_ii'], 2)
                    elif _c == MAP['hexastal']:
                        self.action_stack[0].dice_size = 6
                    elif _c == MAP['octastal']:
                        self.action_stack[0].dice_size = 8
                    elif _c == MAP['decastal']:
                        self.action_stack[0].dice_size = 10
                    elif _c == MAP['chaotic_drill']:
                        self.add_status(target_qq, MAP['confusion'], 1)
                    elif _c == MAP['fragment']:
                        self.action_stack[0].damage_plus += 45
                        self.draw(player_qq, 2)
                    elif _c == MAP['refreshment']:
                        for _k in _pl.skill.keys():
                            _pl.skill[_k] = 0
                    elif _c == MAP['aurora_concussion']:
                        self.action_stack[0].is_void = True
                        for _tgs in self.players.values():
                            if _tgs != _pl:
                                _aur_dice = self.dice(_tgs.qq, 2, 1)
                                _ret += f'璀璨的极光四散而开，{_tgs.character.id} 的极光点数为 {_aur_dice} ！\n'
                                if _aur_dice == 1:
                                    self.add_hidden_status(_tgs.qq, 'aurora', -1)
                                    _tgs.character.hidden_status['aurora'][2] = math.ceil(_tgs.character.attack * 0.5)
                                    self.add_status(_tgs.qq, MAP['exhausted'], 1)
                    elif _c == MAP['mace']:
                        self.action_stack[0].damage_plus += 90
                        self.add_status(target_qq, MAP['fractured'], 2)
                    elif _c == MAP['redstone']:
                        _stat = random.choice(list(_tg.character.status.keys()))
                        self.add_status(target_qq, _stat, 1)
                        _ret += f'{_tg.character.id} 的 {_stat} 效果被延长了…\n'
                    elif _c == MAP['nano_permeation']:
                        self.add_hidden_status(player_qq, 'nano', 1)
                    elif _c == MAP['filching']:
                        self.action_stack[0].is_void = True
                        fil_card = random.choice(_tg.card)
                        self.remove_card(target_qq, fil_card)
                        self.add_card(player_qq, fil_card)
                    elif _c == MAP['declaration']:
                        _card_str = ''
                        for _card in _tg.card:
                            _card_str += f'{_card} '
                        _skill_str = ''
                        for _skill in _tg.skill.keys():
                            _skill_str += f'{_skill} '
                            if _tg.skill_status[_skill] == 0:
                                _tg.skill_status[_skill] = 1
                        rem_card = random.choice(_tg.card)
                        self.remove_card(target_qq, rem_card)
                        _ret += f'{_tg.character.id} 的手牌有 {_card_str}，技能有 {_skill_str}！\n{rem_card} 被弃置了！\n'
                    elif _c == MAP['hologram']:
                        _skill = self.choose_skill(player_qq)
                        _pl.skill_status[_skill] = 2
                        self.action_stack[0].is_void = True
                    elif _c == MAP['pyrotheum']:
                        self.add_status(target_qq, MAP['flaming'], 3)
                    elif _c == MAP['passing_gaze']:
                        self.action_stack[0].damage_plus += 100
                        self.add_status(target_qq, MAP['dissociated'], 1)
                    elif _c == MAP['cryotheum']:
                        self.add_status(target_qq, MAP['frost'], 2)
                    elif _c == MAP['corrupt_pendant']:
                        self.add_attribute(player_qq, 'attack', 5)
                        self.add_attribute(target_qq, 'attack', -5)
                        self.action_stack.append(Action(_pl, _pl, action_type='heal', damage_point=60))
                        self.action_stack.append(Action(_tg, _pl, action_type='damage', damage_point=60))
                    elif _c == MAP['heart_locket']:
                        self.add_attribute(player_qq, 'defense', 10)
                    elif _c == MAP['amethyst']:
                        _ame_dice = self.dice(player_qq, 2, 1)
                        _ret += f'折射水晶闪耀，{_pl.character.id} 的折射点数为 {_ame_dice} ！\n'
                        if _ame_dice == 1:
                            self.action_stack[0].damage_plus += 80
                        elif _ame_dice == 2:
                            self.action_stack[0].damage_plus -= 40
                    elif _c == MAP['bow']:
                        self.add_hidden_status(player_qq, 'bow', 1)  # 见 Line 852 后于残片结算
                    elif _c == MAP['track']:
                        if _tg.has_status(MAP['dodge']):
                            self.action_stack[0].damage_multi *= 1.5
                            self.action_stack[0].is_track = True
                    elif _c == MAP['penetrate']:
                        if _tg.character.armor != 0:
                            self.action_stack[0].damage_multi *= 1.5
                            self.action_stack[0].is_penetrate = True
                    elif _c == MAP['end_halberd']:
                        self.action_stack[0].damage_multi *= 1.5
                    elif _c == MAP['slowness_spell']:
                        self.add_status(target_qq, MAP['slowness'], 2)
                    elif _c == MAP['swift_spell']:
                        self.add_status(player_qq, MAP['swift'], 3)
                    elif _c == MAP['invisibility_spell']:
                        self.add_status(player_qq, MAP['dodge'], -1)
                        self.action_stack[0].is_void = True
                    elif _c == MAP['arrow']:
                        self.action_stack[0].damage_plus += 50
                    elif _c == MAP['rapier']:
                        self.add_attribute(player_qq, 'attack', 15)
                    elif _c == MAP['arctic_heart']:
                        _arc_sk = extra[ext_ind]
                        _pl.skill[_arc_sk] -= 1
                        ext_ind += 1
            if 'fission' in _pl.character.hidden_status.keys():
                for _c in cards:
                    card_able = True
                    if card_able:
                        if _c == MAP['chaotic_drill']:
                            self.add_status(target2_qq, MAP['confusion'], 1)
                        if _c == MAP['filching']:
                            self.action_stack[0].is_void = True
                            fil_card = random.choice(_tg2.card)
                            self.remove_card(target2_qq, fil_card)
                            self.add_card(player_qq, fil_card)
                        if _c == MAP['pyrotheum']:
                            self.add_status(target2_qq, MAP['flaming'], 3)
                        if _c == MAP['cryotheum']:
                            self.add_status(target2_qq, MAP['frost'], 2)
                        if _c == MAP['passing_gaze']:
                            self.add_status(target2_qq, MAP['dissociated'], 1)
                        if _c == MAP['corrupt_pendant']:
                            self.add_attribute(target2_qq, 'attack', -5)
                            self.action_stack.append(Action(_tg2, _pl, action_type='damage', damage_point=60))
                self.action_stack[0].damage_multi *= 0.8
            if _pl.has_hidden_status('bow'): # 复合弓结算
                card_count = _pl.count_card()
                self.action_stack.append(Action(_tg, _pl, action_type='damage', damage_point=75 * card_count))
                self.remove_hidden_status(player_qq, 'bow')
                _pl.clear_hand()
            if not self.action_stack[0].is_void: # 若未使用不造成伤害的道具，则投掷骰子
                _act_dice = self.dice(player_qq, self.action_stack[0].dice_size, 1)
                self.action_stack[0].dice_point = _act_dice
                _ret += f'命运的骰子显现了结果，朝上的点数是 {_act_dice} ！\n'
            return _ret

    def play_skill(self, player_qq:str, target_qq_list: list, skill: str, extra: list):
        _pl = self.players[player_qq]
        _tg = self.players[target_qq_list[0]]
        _ret = ''
        skill_able = True
        if _pl.has_status(MAP['confusion']):
            skill_able = False
            _ret += '混乱状态下不能使用技能哦\n'
        if  _pl.has_status(MAP['silence']):
            skill_able = False
            _ret += '静默状态下不能使用技能哦\n'
        if skill_able:
            if skill == MAP['benevolence']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['benevolence'], action_type='skill'))
            elif skill == MAP['phase_transition']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['phase_transition'], action_type='skill'))
            elif skill == MAP['heaven_delivery']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['heaven_delivery'], action_type='skill'))
            elif skill == MAP['purification']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['purification'], action_type='skill'))
            elif skill == MAP['blood_thirsty']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['blood_thirsty'], action_type='skill'))
            elif skill == MAP['reticence']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['reticence'], action_type='skill'))
            elif skill == MAP['laser']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['laser'], action_type='skill'))
            elif skill == MAP['fission']:
                self.skill_stack.append(
                    Action(target=_pl, source=_pl, name=MAP['fission'], action_type='skill'))
                self.add_hidden_status(player_qq, 'fission', 1)
            elif skill == MAP['massacre']:
                self.add_attribute(player_qq, 'attack', 5)
                self.action_stack_post.append(Action(_pl, _pl, action_type='heal', damage_point=100))
                if not _pl.has_hidden_status('extra'):
                   self.add_hidden_status(player_qq, 'extra', 1)
            elif skill == MAP['ice_splinter']:
                self.skill_stack.append(
                    Action(target=_tg, source=_pl, name=MAP['ice_splinter'], action_type='skill'))
            _tgs_c_id = ''
            for _tgs in target_qq_list:
                _tgs_c_id += (self.players[_tgs].character.id + ' ')
            _ret += f'{_pl.character.id} 对 {_tgs_c_id}使用了 {skill} !\n'
            if _pl.skill_status[skill] == 0:  # 技能状态由未使用变为已使用
                _pl.skill_status[skill] = 1
            if skill in assets.SKILL.keys(): # 设置技能CD
                _pl.skill[skill] = assets.SKILL[skill]
            elif skill in SKILL_EXCLUSIVE.keys():
                _pl.skill[skill] = SKILL_EXCLUSIVE[skill]
            if _pl.character.id == MAP['neko']: # 妮卡欧特质结算
                self.play_trait(player_qq, trait=MAP['tireless_observer'], extra=[skill])
            if _pl.skill_status[skill] == 2:  # 技能由全息投影产生，为一次性
                _pl.skill.pop(skill)
                _pl.skill_status.pop(skill)
                _ret += f'{skill} 的投影缓缓破碎了…\n'
        else:
            _ret += f'你处于混乱状态，无法使用技能哦\n'
        return _ret

    def play_trait(self, player_qq: str, target_qq_list = None, trait: str = '', extra: list = None):
        if target_qq_list is None:
            target_qq_list = []
        _pl = self.players[player_qq]
        try:
            target_qq = target_qq_list[0]
            _tg = self.players[target_qq_list[0]]
        except IndexError:
            target_qq = None
            _tg = None
        _ret = ''
        _mp_cost = 0
        trait_able = True
        if _pl.has_status(MAP['confusion']):
            trait_able = False
            _ret += f'处于混乱状态，无法使用特质哦\n'
        if _pl.has_hidden_status('demon_seal'):
            trait_able = False
            _ret += f'特质被封印了哦\n'
        if _pl.has_hidden_status('non_flying'):
            _mp_cost += 1
        if _pl.has_status(MAP['weakness']) and trait == MAP['decree']:
            trait_able = False
            _ret += f'处于虚弱状态，无法布置律令哦\n'
        if _pl.character.id == MAP['darkstar']:
            trait_able = True
        if trait_able:
            if trait == MAP['tireless_observer'] and _pl.character.id == MAP['neko']:
                _pl.skill[extra[0]] -= 1 # extra传入技能名字
            elif trait == MAP['distinct_road'] and _pl.character.id == MAP['neko']:
                _s = self.choose_skill(player_qq)
            elif trait == MAP['dusk_void'] and _pl.character.id == MAP['yun']:
                self.add_hidden_status(player_qq, 'dusk', -1)
            elif trait == MAP['lucky_shield'] and _pl.character.id == MAP['starduster']:
                _star_dice = self.dice(player_qq, 6, 1)
                _ret += f'星尘的幸运壁垒发动，幸运点数为 {_star_dice} ！\n'
                if _star_dice in [1, 6]:
                    self.add_hidden_status(player_qq, 'invincible', 1)
                    _ret += f'星尘闪避了一次伤害!\n'
            elif trait == MAP['resolution'] and _pl.character.id == MAP['darkstar']:
                _res_dice = self.dice(player_qq, 6, 1)
                _ret += f'黯星的决心发动，决心点数为 {_res_dice} ！\n'
                if _res_dice in [1, 5, 6]:
                    _pl.character.hp = 1
                    _ret += f'黯星充满了决心，不会就此倒下！\n'
                else:
                    _ret += self.player_died(player_qq)
            elif trait == MAP['dont_forget_me'] and _pl.character.id == MAP['loveless']:
                if extra[0] == 0:
                    self.action_stack[0].damage_multi *= 3.3
                elif extra[0] == 1:
                    self.action_stack[0].damage_multi *= 2.7
                elif extra[0] == 2:
                    _pl.character.hp = 1
                    self.add_hidden_status(player_qq, 'dont_forget_me', 2)
                    _ret += f'不要忘记恋慕……\n'
            elif trait == MAP['icy_blood'] and _pl.character.id == MAP['shigure']:
                self.add_hidden_status(player_qq, 'ice_immunity', 1)
            elif trait == MAP['arctic_seal'] and _pl.character.id == MAP['shigure']:
                _ice_dice = self.dice(player_qq, 6, 1)
                _ret += f'时雨令冰元素侵蚀目标，冰封点数为 {_ice_dice} !\n'
                if _ice_dice in [1, 3, 6]:
                    self.add_status(_tg.qq, MAP['frozen'], 1)
                    _ret += f'{_tg.character.id} 被冻成冰雕了，无法行动！\n'
            elif trait == MAP['im_drunk'] and _pl.character.id == MAP['sumoggu']:
                _pl.character.hidden_status['alcohol'][2] += 0.4 * extra[0] # extra传入造成的伤害
                if extra[0] >= 300:
                    self.action_stack_post.append(Action(_tg, _pl, damage_point=round(_pl.character.hidden_status['alcohol'][2])))
                    _pl.character.hidden_status['alcohol'][2] = 0
                    self.add_status(player_qq, MAP['weakness'], 1)
                    self.add_status(target_qq, MAP['nausea'], 2)
            elif trait == MAP['decree'] and _pl.character.id == MAP['sumoggu']:
                _mp_cost += 1
                if _pl.character.move_point < _mp_cost:
                    _ret += '你的行动点不足哦\n'
                elif _pl.has_hidden_status(' '):
                    _ret += '你处于虚弱状态，无法布置律令哦\n'
                elif (_tg.has_hidden_status('decree1') and extra[0] == '禁空' or _tg.has_hidden_status('decree2')
                      and extra[0] == '天锁' or _tg.has_hidden_status('decree3') and extra[0] == '封魔'
                      or _tg.has_hidden_status('decree4') and extra[0] == '缚灵'):
                    _ret += '你不能对同一玩家连续布置同一律令哦\n'
                else:
                    self.add_attribute(player_qq, 'move_point', -_mp_cost)
                    if extra[0] == '禁空':
                        self.add_hidden_status(target_qq_list[0], 'non_flying', 1)
                        self.add_hidden_status(target_qq_list[0], 'decree1', 2)
                    elif extra[0] == '天锁':
                        self.add_hidden_status(target_qq_list[0], 'sky_lock', 1)
                        self.add_hidden_status(target_qq_list[0], 'decree2', 2)
                    elif extra[0] == '封魔':
                        self.add_hidden_status(target_qq_list[0], 'demon_seal', 1)
                        self.add_hidden_status(target_qq_list[0], 'decree3', 2)
                    elif extra[0] == '缚灵':
                        self.add_hidden_status(target_qq_list[0], 'spirit_bind', 1)
                        self.add_hidden_status(target_qq_list[0], 'decree4', 2)
                    _ret += f'{_pl.character.id} 对 {_tg.character.id} 布置了 律令·{extra[0]} ！\n'
            elif trait == MAP['aurelysium'] and _pl.character.id == MAP['ting_xinyu']:
                is_double = False
                cards = extra
                tags = []
                for _c in cards: # tag总数是否≥5
                    _tag = assets.TAG[_c]
                    for _t in _tag:
                        if not _t in tags:
                            tags.append(_tag)
                if len(tags) >= 5:
                    is_double = True
                _c = extra[0]
                if not is_double:
                    for _c in cards:
                        if self.has_tag(_c, MAP['sharp']):
                            self.add_attribute(player_qq, 'attack', 5)
                        if self.has_tag(_c, MAP['protect']):
                            self.add_attribute(player_qq, 'defense', 5)
                        if self.has_tag(_c, MAP['vital']):
                            self.action_stack.append(Action(_pl, _pl, action_type='heal', damage_point=50))
                        if self.has_tag(_c, MAP['destiny']):
                            self.add_hidden_status(player_qq, 'destiny', 1)
                        if self.has_tag(_c, MAP['mystique']):
                            for _s in _pl.character.status.keys():
                                if assets.STATUS[_s][0] == 1:
                                    self.add_status(player_qq, _s, 1)
                                print(assets.STATUS[_s][0])
                        if self.has_tag(_c, MAP['phantom']):
                            self.draw(player_qq, 1)
                        if self.has_tag(_c, MAP['magic']):
                            self.add_attribute(target_qq, 'armor', -_tg.character.armor)
                            if _tg.has_status(MAP['dodge']):
                                self.remove_status(target_qq, MAP['dodge'])
                        if self.has_tag(_c, MAP['weird']):
                            self.add_status(target_qq, MAP['silence'], 1)
                        if self.has_tag(_c, MAP['disorder']):
                            _dis_dice = self.dice(player_qq, 10, 1)
                            self.action_stack.append(Action(_tg, _pl, damage_point=55 - 10 * _dis_dice))
                        if self.has_tag(_c, MAP['sense']):
                            self.add_attribute(player_qq, 'move_point', 1)
                        if self.has_tag(_c, MAP['heat']):
                            self.action_stack.append(Action(_tg, _pl, damage_point=30, damage_type='fire'))
                        if self.has_tag(_c, MAP['chill']):
                            self.add_status(target_qq, MAP['cold'], 1)
                else:
                    for _c in cards:
                        if self.has_tag(_c, MAP['sharp']):
                            self.add_attribute(player_qq, 'attack', 10)
                        if self.has_tag(_c, MAP['protect']):
                            self.add_attribute(player_qq, 'defense', 10)
                        if self.has_tag(_c, MAP['vital']):
                            self.action_stack.append(Action(_pl, _pl, action_type='heal', damage_point=100))
                        if self.has_tag(_c, MAP['destiny']):
                            self.add_hidden_status(player_qq, 'destiny2', 1)
                        if self.has_tag(_c, MAP['mystique']):
                            for _s in _pl.character.status.keys():
                                if assets.STATUS[_s][0] == 1:
                                    self.add_status(player_qq, _s, 2)
                        if self.has_tag(_c, MAP['phantom']):
                            self.draw(player_qq, 2)
                        if self.has_tag(_c, MAP['magic']):
                            self.add_attribute(target_qq, 'armor', -_tg.character.armor)
                            if _tg.has_status(MAP['dodge']):
                                self.remove_status(target_qq, MAP['dodge'])
                            for _s in list(_tg.character.status.keys()):
                                if assets.STATUS[_s][0] == 1:
                                    self.remove_status(target_qq, _s)
                        if self.has_tag(_c, MAP['weird']):
                            self.add_status(target_qq, MAP['confusion'], 1)
                        if self.has_tag(_c, MAP['disorder']):
                            _dis_dice = self.dice(player_qq, 10, 1)
                            self.action_stack.append(Action(_tg, _pl, damage_point=110 - 20 * _dis_dice))
                        if self.has_tag(_c, MAP['sense']):
                            self.add_attribute(player_qq, 'move_point', 2)
                        if self.has_tag(_c, MAP['heat']):
                            self.action_stack.append(Action(_tg, _pl, damage_point=60, damage_type='fire'))
                        if self.has_tag(_c, MAP['chill']):
                            self.add_status(target_qq, MAP['cold_ii'], 1)
        return _ret

    def fold_card(self, player_qq: str, cards: list):
        _pl = self.players[player_qq]
        _cards = ''
        for _c in cards:
            self.remove_card(player_qq, _c)
            _cards += f'{_c} '
        _ret = f'{_pl.character.id} 弃掉了 {_cards}！\n'
        return _ret

    def start_turn(self):
        player_qq = ''
        _ret = ''
        for _pl in self.players.values():
            if self.game_sequence[self.turn - 1] == _pl.id:
                player_qq = _pl.qq
        _player = self.players[player_qq]
        _player.has_played_card = False
        _player.set_max_card(6)
        _player.character.damage_dealt_round = 0
        if _player.has_hidden_status('sky_lock'):
            _player.set_max_card(3)
        if self.get_player_from_chara(MAP['loveless']): # 恋慕特质结算
            _pl_love = self.get_player_from_chara(MAP['loveless'])
            if _pl_love.has_hidden_status('dont_forget_me') and self.round == 2:
               _ret += self.player_died(_pl_love.qq)
        if _player.character.id == MAP['darkstar']:
            _player.character.hidden_status['massacre'][2] = 0 # 屠杀统计归零
        if _player.has_status(MAP['stellar_cage']): # 星牢效果结算
            self.end_turn()
        else:
            if not _player.has_hidden_status('extra'):
                if self.round == 1: # 行动点回复
                    self.move_init(player_qq)
                else:
                    self.move_regenerate(player_qq)
            if not _player.has_status(MAP['confusion']):  # 处于混乱状态的角色无法发动特质
                if _player.character.id == MAP['nepst']:
                    _stat = list(_player.character.status.keys())
                    for _k in _stat:
                        self.remove_status(player_qq, _k)
            if _player.has_status(MAP['frozen']):  # 冰冻状态下将跳过回合 # 未完成
                self.end_turn()
            else:
                if not _player.has_hidden_status('extra'): # 抽牌
                    _c = self.draw(player_qq, 2)
                if _player.has_hidden_status('heaven'):
                    self.draw(player_qq, 1)
        return _ret

    def end_turn(self):
        def damage(action: Action):
            _hp = action.target.character.hp + action.target.character.armor  # 受伤时先减损护甲，再减损生命值
            _hp -= action.damage_point
            if _hp - action.target.character.hp < 0:
                action.target.character.armor = 0
                action.target.character.hp = _hp
            else:
                action.target.character.armor = _hp - action.target.character.hp

        def action_event(action: Action):
            _act_ret = ''
            if action == EMPTY_ACTION:
                return ''
            if action.source.character.id == MAP['loveless']:  # 恋慕【勿忘我】特质
                self.play_trait(action.source.qq, trait=MAP['dont_forget_me'], extra=[0])
            if action.target.character.id == MAP['loveless']:
                self.play_trait(action.target.qq, trait=MAP['dont_forget_me'], extra=[1])
            if action.source.has_hidden_status('destiny'): # 亭歆雨【彼岸之金·命运】特质
                action.dice_point += 1
            if action.source.has_hidden_status('destiny2'):
                action.dice_point += 2
            if not action.target.has_status(MAP['confusion']):
                if action.target.character.id == MAP['tussiu']:  # 图西乌特质结算
                    action.damage_multi = 1
                    action.damage_plus = 0
                    if action.dice_point > 5:
                        action.dice_point = 5
            if action.target.character.id == MAP['starduster'] and not action.is_void:  # 星尘【幸运壁垒】特质
                _act_ret += self.play_trait(action.target.qq, trait=MAP['lucky_shield'])
                if action.target.has_hidden_status('invincible'):
                    action.is_void = True
                    self.remove_hidden_status(action.target.qq, 'invincible')
            if action.target.character.id == MAP['shigure']: # 时雨特质结算
                self.play_trait(action.target.qq, trait=MAP['icy_blood'])
                if action.target.has_hidden_status('ice_immunity'):
                    action.damage_plus -= action.source.get_status_duration(MAP['frost']) * 75
                    self.remove_hidden_status(action.target.qq, 'ice_immunity')
            if action.source.has_hidden_status('nano'): # 纳米渗透结算
                action.attack_plus += action.target.character.defense
            action.set_damage_point(action.calculate())
            if action.is_aoe: # 奈普斯特特质结算
                if action.target.character.id == MAP['nepst']:
                    action.damage_point = 0
            if action.source.character.id == MAP['yun']: # 云云子特质结算
                self.play_trait(action.source.qq, trait=MAP['dusk_void'])
                if action.source.has_hidden_status('dusk'):
                    action.damage_point = (action.dice_point - 1) * (action.source.character.attack - 30)
                    action.is_penetrate = True
                    self.remove_hidden_status(action.source.qq, 'dusk')
            if action.is_track and action.target.has_status(MAP['dodge']): # 闪避效果结算
                self.remove_status(action.target.qq, MAP['dodge'])
            if action.target.has_status(MAP['dodge']):
                action.is_void = True
                self.remove_status(action.target.qq, MAP['dodge'])
                _act_ret += f'{action.target.character.id} 闪避了一次伤害!\n'
            if action.source.has_status(MAP['nausea']): # 反胃效果结算
                _nau_dice = self.dice(action.source.qq, 6, 1)
                _act_ret += f'{action.source.character.id} 感到一阵恶心，反胃点数为 {_nau_dice} ！'
                if _nau_dice in [2, 4, 6]:
                    action.is_void = True
                    _act_ret += f'{action.source.character.id} 由于反胃，攻击没有击中目标…\n'
            if not action.is_void:
                if action.is_pierce or action.target.has_status(MAP['fractured']) or action.is_penetrate:
                    action.target.character.hp -= action.damage_point
                else:
                    damage(action)
                if action.source.has_hidden_status('leeching'):
                    action.source.character.hidden_status['leeching'][2] += 0.5 * action.damage_point
                if action.target.character.id == MAP['sumoggu']: # 长霾特质结算
                    self.play_trait(action.target.qq, [action.source.qq], MAP['im_drunk'], [action.damage_point])
                action.source.character.damage_dealt_total += action.damage_point  # 统计总伤和总承伤
                action.target.character.damage_received_total += action.damage_point
                action.source.character.damage_dealt_round += action.damage_point  # 统计每回合造成的总伤
                _act_ret += f'{action.source.character.id} 对 {action.target.character.id} 造成了 {action.damage_point} 点伤害！\n'
            if action.source.has_hidden_status('hero_legend'):
                self.remove_hidden_status(action.source.qq, 'hero_legend')
            if action.target.has_hidden_status('dream_shelter'):
                self.remove_hidden_status(action.target.qq, 'dream_shelter')
            return _act_ret

        def damage_event(action: Action):
            _dmg_ret = ''
            if action.is_aoe:
                if action.target.character.id in ['奈普斯特', "格白"]:
                    action.damage_point = 0
            if action.damage_type == 'magical':
                if action.target.character.id == MAP['starduster']: # 星尘特质结算
                    _dmg_ret += self.play_trait(action.target.qq, trait=MAP['lucky_shield'])
                if action.target.has_hidden_status('invincible'):
                    action.is_void = True
                if not action.is_void:
                    if action.source.has_hidden_status('leeching'):
                        action.source.character.hidden_status['leeching'][2] += 0.5 * action.damage_point
                    if action.target.has_status(MAP['fractured']):
                        action.target.character.hp -= action.damage_point
                    else:
                        damage(action)
            else:
                action.target.character.hp -= action.damage_point
            if not action.is_void:
                if action.damage_type == 'magical':
                    _dmg_ret += f'{action.target.character.id} 被 {action.source.character.id} 的魔法击中，失去了 {action.damage_point} 点生命！\n'
                if action.damage_type == 'fire':
                    _dmg_ret += f'{action.target.character.id} 受到烈焰灼烧，失去了 {action.damage_point} 点生命！\n'
                if action.damage_type == 'ice':
                    if self.get_player_from_chara(MAP['shigure']) and action.target.character.id != MAP['shigure']: # 时雨特质结算
                        _pl_shi = self.get_player_from_chara(MAP['shigure'])
                        _dmg_ret += self.play_trait(_pl_shi.qq, [action.target.qq], MAP['arctic_seal'])
                    _dmg_ret += f'{action.target.character.id} 受到冰霜侵袭，失去了 {action.damage_point} 点生命！\n'
                if action.damage_type == 'physical':
                       _dmg_ret += f'{action.target.character.id} 失去了 {action.damage_point} 点生命！\n'
                action.target.character.damage_received_total += action.damage_point # 总承伤统计
                if action.source != EMPTY_PLAYER:
                    action.source.character.damage_dealt_total += action.damage_point # 总伤统计
                    action.source.character.damage_dealt_round += action.damage_point  # 回合伤害统计
                if action.target.character.id == MAP['sumoggu']:
                    self.play_trait(action.target.qq, [action.source.qq], MAP['im_drunk'], [action.damage_point])
            return _dmg_ret

        def heal_event(action: Action):
            _heal_ret = ''
            if action.target.has_status(MAP['dissociated']):
                _heal_ret += f'{action.target.character.id} 处于游离状态，无法回复生命……\n'
            else:
                if action.target.character.hp + action.damage_point >= action.target.character.max_hp:
                    action.damage_point = action.target.character.max_hp - action.target.character.hp
                action.target.character.hp += action.damage_point
                _heal_ret += f'{action.target.character.id} 受 {action.source.character.id} 治疗，回复了 {action.damage_point} 点生命！\n'
            return _heal_ret

        _pl_now = self.get_player_from_id(self.game_sequence[self.turn-1]) # 获取当前turn对应的玩家
        _pl_stat = _pl_now.character.status
        if len(self.action_stack) == 0:
            self.action_stack.append(EMPTY_ACTION)
        if self.action_stack[0].is_fission:
            _action = self.action_stack[0]
            fission_damage = _action.calculate()
            self.action_stack.append(Action(_action.fission_target, _action.source, damage_point=fission_damage,
                                            is_pierce=_action.is_pierce, is_aoe=True))
        if _pl_now.has_status(MAP['flaming']) and _pl_now.has_status(MAP['frost']):  # 冰火相消
            while _pl_now.get_status_duration(MAP['flaming']) > 0 and _pl_now.get_status_duration(MAP['frost']) > 0:
                _pl_stat[MAP['flaming']] -= 1
                _pl_stat[MAP['frost']] -= 1
            if _pl_stat[MAP['flaming']] == 0:
                self.remove_status(_pl_now.qq, MAP['flaming'])
            if _pl_stat[MAP['frost']] == 0:
                self.remove_status(_pl_now.qq, MAP['frost'])

        _ret = ''
        #self.skill_stack.reverse() # 技能结算（后置先结算）
        for _s in self.skill_stack:
            if not _s.is_silenced:
                if _s.name == MAP['benevolence']:
                    pass
                elif _s.name == MAP['phase_transition']:
                    for action in self.action_stack:
                        if action.target == _s.source and action.type in ['action', 'damage']:
                            action.target = _s.target
                elif _s.name == MAP['heaven_delivery']:
                    self.add_hidden_status(_s.target.qq, 'heaven', 2)
                    self.add_hidden_status(_s.source.qq, 'heaven', 2)
                elif _s.name == MAP['purification']:
                    if _s.target.character.status:
                        for _stat in list(_s.target.character.status.keys()):
                            self.remove_status(_s.target.qq, _stat)
                elif _s.name == MAP['blood_thirsty']:
                    self.add_hidden_status(_s.source.qq, 'leeching', 1)
                    _s.source.character.hidden_status['leeching'].append(0)
                elif _s.name == MAP['laser']:
                    self.action_stack.append(Action(_s.target, _s.source, damage_point=60))
                    self.add_status(_s.target.qq, MAP['fragility'], 2)
                elif _s.name == MAP['reticence']:
                    _s_ind = self.skill_stack.index(_s)
                    if _s_ind > 0:
                        self.skill_stack[_s_ind - 1].is_silenced = True
                elif _s.name == MAP['ice_splinter']:
                    self.add_status(_s.target.qq, MAP['frost'], 1)
                    self.action_stack.append(Action(_s.target, _s.source, action_type='damage', damage_point=80))
        self.skill_stack.clear()

        _stat = _pl_now.character.status # 造成伤害的状态结算
        _h_stat = _pl_now.character.hidden_status
        _skill = _pl_now.skill
        if _pl_now.has_status(MAP['flaming']):
            self.action_stack.append(Action(_pl_now, damage_point=50, damage_type='fire'))
        if _pl_now.has_status(MAP['frost']):
            self.action_stack.append(Action(_pl_now, damage_point=30, damage_type='ice'))
        if _pl_now.has_status(MAP['regeneration']):
            self.action_stack.append(Action(_pl_now, _pl_now, action_type='heal', damage_point=120))

        # self.action_stack.reverse() # 行动结算（后置行动先结算）
        for _a in self.action_stack:
            if _a.type == 'action': # 结算角色的攻击行为
                _ret += action_event(_a)
            elif _a.type == 'damage': # 结算冰火等造成的生命损失
                _ret += damage_event(_a)
            elif _a.type == 'heal': # 结算治疗
                _ret += heal_event(_a)
        self.action_stack.clear()

        for _pl in self.players.values(): # 结算玩家死亡
            if _pl.character.hp <= 0:
                if _pl.character.id == MAP['loveless'] and self.round == 1: # 恋慕特质结算
                    _ret += self.play_trait(_pl.qq, trait=MAP['dont_forget_me'], extra=[2]) # extra标识同名被动的不同功能
                if _pl.character.id == MAP['darkstar']: # 黯星特质结算
                    _ret += self.play_trait(_pl.qq, trait=MAP['resolution'])
                else:
                    _ret += self.player_died(_pl.qq)

        if self.game_type == 0 and len(self.died) == len(self.players) - 1:
            _ret += f'仅剩一人存活，游戏结束！'
            for pl in self.players.values():
                if not pl.is_dead:
                    _ret += f'胜利者是 {pl.character.id} ！'
            self.game_status = 2
            return _ret

        for _pl in self.players.values(): # 回合结束，玩家特质/技能结算
            if (_pl.character.id == MAP['chinro'] and _pl.character.hp <= _pl.character.max_hp * 0.5
                    and _pl.character.hidden_status['encourage'][2] == 0): # 晴箬特质结算
                _ret += f'{_pl.character.id} 决定好好休息一下，打起精神！\n'
                _pl.character.hidden_status['encourage'][2] = 1
                self.action_stack_post.append(
                    Action(_pl, _pl, action_type='heal', damage_point=int(_pl.character.max_hp * 0.8) - _pl.character.hp))

        if _pl_now.character.id == MAP['darkstar'] and _pl_now.character.damage_dealt_round >= 250:
            _ret += f'{_pl_now.character.id} 刀尖泛起了红光…屠杀开始了！\n'
            self.play_skill(_pl_now.qq, [_pl_now.qq], MAP['massacre'], [])
        if _pl_now.has_hidden_status('leeching'): # 嗜血技能结算
            self.action_stack_post.append(Action(_pl_now, _pl_now, action_type='heal', damage_point=int(_pl_now.character.hidden_status['leeching'][2])))

        for _pl in self.players.values(): # 状态/隐藏状态持续时间-1
            _stat_be_removed = []
            _h_stat_be_removed = []
            for _k, _v in _pl.character.status.items():
                _v[1] -= 1
                if math.ceil(_v[1] / self.player_count) < _v[0]:
                    _v[0] -= 1
                if _v[0] == 0:
                    _stat_be_removed.append(_k)
            for _k2, _v2 in _pl.character.hidden_status.items():
                _v2[1] -= 1
                if math.ceil(_v2[1] / self.player_count) < _v2[0]:
                    _v2[0] -= 1
                if _v2[0] == 0:
                    _h_stat_be_removed.append(_k2)
            for _s in _stat_be_removed:
                self.remove_status(_pl.qq, _s)
            for _s2 in _h_stat_be_removed:
                self.remove_hidden_status(_pl.qq, _s2)
        for _k in list(_skill.keys()): # 技能CD-1
            if _skill[_k] > 0:
                _skill[_k] -= 1

        for _a in self.action_stack_post: # 回合结束的一些特质结算
            if _a.type == 'damage': # 结算冰火等造成的生命损失
                _ret += damage_event(_a)
            elif _a.type == 'heal': # 结算治疗
                _ret += heal_event(_a)
        self.action_stack_post.clear()

        _ret += '\n'
        if not _pl_now.has_hidden_status('extra'):
            self.turn += 1 # 轮次更换
            if self.turn > self.player_count:
                self.turn = 1
                self.round += 1
            while self.get_player_from_id(self.game_sequence[self.turn-1]) in self.died.values():
                self.turn += 1
                if self.turn > self.player_count:
                    self.turn = 1
                    self.round += 1
        if self.turn == 1 and self.round == 6: # 第6轮开始，揭露所有技能
            for _pl in self.players.values():
                for _sk in _pl.skill_status.keys():
                    if _pl.skill_status[_sk] == 0:
                        _pl.skill_status[_sk] = 1
        _ret += self.player_info()
        _ret += f'\n{_pl_now.name} 结束了回合！'
        _ret += self.start_turn()
        return _ret