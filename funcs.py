# -*- coding:utf-8 -*-

from typing import Dict, List

import assets, classes


dice = classes.dice


def resolve_arg(arg: str) -> List[List[str]]:  # 字符串解析未完工
    cards: List[str] = []
    target: List[str] = []
    rough_resolution: List[str] = arg.split()
    if "to" in rough_resolution:
        sep = rough_resolution.index("to")
        cards = rough_resolution[:sep]
        target = rough_resolution[sep + 1 :]
    else:
        pass


class Damage:
    def __init__(self, source: classes.Player, target: classes.Player) -> None:
        self.damage_point: int = 0
        self.source: classes.Player = source
        self.target: classes.Player = target
        self.is_aoe: bool = False
        self.is_pierce: bool = False
        self.is_hplost: bool = False
        self.is_heal: bool = False
        self.is_det_rad = False
        self.dice_size: int = 4
        self.dice_point: int = 1
        self.atk_plus: int = 0
        self.atk_multi: int = 1
        self.dmg_plus: int = 0
        self.dmg_multi: int = 1

    def dice_multi(self):
        self.dice_point = dice(self.dice_size, 1)

    def calculate(self):
        self.damage_point = (
            (
                (self.atk_plus + self.source.character.attack) * self.atk_multi
                - self.target.character.defense
            )
            * self.dice_point
            + self.dmg_plus
        ) * self.dmg_multi

    def damage(self):
        if self.is_det_rad == True:
            self.damage_point = 0
            return
        if self.is_aoe == True:
            if self.target.character.id in ["奈普斯特", "格白"]:
                return
        if self.is_pierce == False:
            pass
        if self.is_hplost == True:
            self.target.character.hp -= self.damage_point
            return
        if self.is_heal == True:
            self.target.character.hp += self.damage_point
        else:
            # print(self.target.character.hp)
            self.target.character.hp -= self.damage_point
            # print(self.target.character.hp)
            # print(self.damage_point)
            return


def get_func(func: str, *args):
    def _group_attack_judge(player: classes.Player) -> bool:
        _ = True
        _ = _ & (player.character.id in ["奈普斯特"])
        _ = _ & (
            ("闪避" in player.character.status.keys())
            & ("凛冰之拥" not in player.character.status.keys())
        )

    # 卡牌
    def end_crystal(action: Action):
        _empty_pl = classes.Player(5364, -100, "None")
        _damage = Damage(_empty_pl, action.source)
        _damage.is_hplost = True
        _damage.damage_point = 30 + dice(4, 2) * 15
        _damage.damage()
        _dmg_point = 40 + dice(8, 1) * 15
        # player.character.hp -= 30 + dice(4, 2) * 15
        for pl in action.game.players.values():
            if (
                action.source.name != pl.name
                and pl.character.status.values() not in ["咕了"]
                and not (
                    pl.character.status.values() in ["梦境"]
                    and action.source.character.id == "卿别"
                )
            ):
                _damage2 = Damage(action.source, pl)
                _damage2.is_aoe = True
                _damage2.damage_point = _dmg_point
                _damage2.damage()

    def hero_legend(action: Action):
        action.source.character.hp += 100
        action.damage.atk_plus += 20
        action.source.character.hidden_status["hero"] = -1

    def wood_sword(action: Action):
        action.source.character.attack += 10

    def shield(action: Action):
        action.source.character.armor += 100
        action.source.character.defense += 5

    def ascension_stairs(action: Action):
        _empty_pl = classes.Player("1013", -101)
        _damage = Damage(_empty_pl, action.source)
        _damage.is_hplost = True
        _damage.damage_point = 0.1 * action.source.character.max_hp
        _damage.damage()
        _min = 6
        _max = 1
        _target = []
        # player.character.hp -= 0.1*player.character.max_hp
        for pl in action.game.players.values():
            if pl.character.status.values() not in ["咕了"] and not (
                pl.character.status.values() in ["梦境"]
                and action.source.character.id == "卿别"
            ):
                _dice = dice(6, 1)
                print(pl.name + str(_dice))
                if _dice < _min:
                    _min = _dice
                    _target = [pl]
                elif _dice == _min:
                    _target.append(pl)
                if _dice > _max:
                    _max = _dice
        _dmg_point = _max * 50
        for pl2 in _target:
            _damage2 = Damage(action.source, pl2)
            _damage2.is_aoe = True
            _damage2.damage_point = _dmg_point
            _damage2.damage()

    def critical_strike(action: Action):
        action.source.character.hidden_status["piercing"] = -1
        action.damage.is_pierce = True

    def self_curing(action: Action):
        action.damage.is_heal = True
        action.damage.damage_point = 120

    def regeneration(action: Action):
        action.source.character.status["持续再生"] = 2

    def strength(action: Action):
        if "力量" in action.source.character.status.keys():
            action.source.character.status["力量"] += 2
        else:
            action.source.character.status["力量"] = 2

    def strength_ii(action: Action):
        if "力量II" in action.source.character.status.keys():
            action.source.character.status["力量II"] += 2
        else:
            action.source.character.status["力量II"] = 2

    def hexastal(action: Action):
        action.damage.dice_size = 6

    def octastal(action: Action):
        action.damage.dice_size = 8

    def decastal(action: Action):
        action.damage.dice_size = 10

    def camelias_drill(action: Action):
        action.source.character.hidden_status["_pre_drill"] = -1

    def fragment(action: Action):
        action.source.character.hidden_status["frag"] = -1
        action.damage.dmg_plus += 45
        action.game.draw(action.source.name, 2)

    def data(action: Action):
        for _s in action.source.skill.keys():
            try:
                action.source.skill[_s] = assets.SKILL[_s]
            except KeyError:
                action.source.skill[_s] = assets.PRIVATE_SKILL[_s]

    def deterrent_radiance(action: Action):
        _empty_pl = classes.Player(3496, -135, "None")
        _damage = Damage(_empty_pl, action.source)
        _damage.is_hplost = True
        _damage.damage_point = 50
        _damage.damage()
        action.damage.is_det_rad == True
        # player.character.hp -= 50
        for pl in action.game.players.values():
            if dice(2) == 1:
                pl.character.status["浴霸"] = 1

    def netherite_axe(action: Action):
        action.damage.dmg_plus += 90
        action.source.character.hidden_status["ne_axe"] = -1
        action.target.character.status["破盾"] = 2

    def redstone(action: Action):
        _sta_count = len(action.target.character.status)
        _rand = dice(_sta_count, 1)
        action.target.character.status[_rand - 1] += 1

    def nanosword(action: Action):
        action.source.character.hidden_status["nano"] = -1

    def lead(action: Action):
        action.damage.is_heal = True
        action.damage.damage_point = 0
        action.source.character.hidden_status["lead"] = -1

    def spectral_arrow(action: Action):
        action.target.character.hidden_status["spectral"] = -1

    def hologram(action: Action):
        action.damage.is_heal = True
        action.damage.damage_point = 0
        _skill = action.game.choose_skill(action.source.name)
        _cd = action.game.skill_deck.get(_skill)
        action.source.skill[_skill] = _cd + 1

    def pyrotheum(action: Action):
        action.target.character.status["熔岩之触"] = 3

    def breath_of_reaper(action: Action):
        action.damage.dmg_plus += 100
        action.target.character.status["死灵"] = 2

    def cryotheum(action: Action):
        action.target.character.status["凛冰之拥"] = 2

    def heart_locket(action: Action):
        action.source.character.defense += 10

    def corrupt_pendant(action: Action):
        action.source.character.hp += 60
        action.source.character.attack += 5
        action.target.character.hp -= 60
        action.target.character.attack -= 5

    def amethyst(action: Action):
        action.damage.dmg_plus += 35
        _dice = dice(2, 1)
        if _dice == 2:
            action.damage.dmg_plus -= 45
        elif _dice == 1:
            action.damage.dmg_plus += 45

    def bow(action: Action):
        pass

    def tracking_arrow(action: Action):
        action.damage.is_pierce = True

    def penetrating_arrow(action: Action):
        action.damage.is_pierce = True

    def end_halberd(action: Action):
        action.damage.dmg_multi *= 1.5

    def slowness(action: Action):
        action.source.character.status["迟缓"] = 2

    def swiftness(action: Action):
        action.source.character.status["迅捷"] = 2

    def invisibility(action: Action):
        action.source.character.status["闪避"] = 2

    # 技能
    def benevolence(action: Action):
        pass

    def phase_transition(action: Action):
        pass

    with open("funcdict", "r", encoding="utf-8") as f:
        funcs: Dict[str, str] = eval(f.read())
    return funcs[func]


EMPTY_GAME = classes.Game("", "", 2, 0)
EMPTY_PLAYER = classes.Player(0, 0, "None")


class Action:
    def __init__(
        self,
        game: classes.Game,
        source: classes.Player,
        target: classes.Player = EMPTY_PLAYER,
        cards: list = [],
        extra: list = [],
    ) -> None:
        self.game = game
        self.source = source
        self.target = target
        self.damage = Damage(self.source, self.target)
        self.extra = extra
        for _c in cards:
            get_func(_c)(self)
        self.damage.dice_multi()
        self.damage.calculate()

    def enforce(self):
        self.damage.damage()


EMPTY_ACTION = Action(EMPTY_GAME, EMPTY_PLAYER)


class Skill:
    def __init__(
        self,
        game: classes.Game,
        source: classes.Player,
        target: classes.Player = EMPTY_PLAYER,
        extra: list = [],
    ) -> None:
        self.game = game
        self.source = source
        self.target = target
        self.extra = extra
        self.is_silenced = False

    def cast(self, skill: str):
        if not self.is_silenced:
            get_func(skill)(self)


class Skill_Action(Skill):
    def __init__(
        self,
        game: classes.Game,
        source: classes.Player,
        target: classes.Player = EMPTY_PLAYER,
        action: Action = EMPTY_ACTION,
        extra: List = [],
    ) -> None:
        super().__init__(game, source, target, extra)
        self.action = action


class Skill_Silence(Skill):
    def __init__(
        self,
        game: classes.Game,
        source: classes.Player,
        skill: Skill,
        target: classes.Player = EMPTY_PLAYER,
        extra: List = [],
    ) -> None:
        super().__init__(game, source, target, extra)
        self.skill = skill

    def cast(self):
        self.skill.is_silenced = True


g1 = classes.Game("", "", 1, 0)
g1.add_player("1")
g1.add_player("2")
g1.add_player("3")
p1 = g1.players["1"]
p2 = g1.players["2"]
p3 = g1.players["3"]
p1.set_character(["时雨", 1000, 95, 35, 6, 2, 1, 1])
p2.set_character(["飖", 1000, 95, 35, 6, 2, 1, 1])
p3.set_character(["方寒", 1000, 95, 35, 6, 2, 1, 1])
a = Action(g1, p1, p2)
a.enforce(["十面璃", "破片水晶"])
print(a.damage.dice_point)
print(p1.character.hp)
print(p2.character.hp)
print(p3.character.hp)
