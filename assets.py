# -*- coding:utf-8 -*-

import json

from pathlib import Path
from typing import List, Dict


__ASSETS_PATH = Path(__file__).parent / "assets"


def __get_file(file: str, suffix: str = "") -> str:
    if suffix:
        with open(__ASSETS_PATH / f"{file}.{suffix}", encoding="utf-8") as f:
            return f.read()
    else:
        with open(__ASSETS_PATH / f"{file}", encoding="utf-8") as f:
            return f.read()


# 以字典形式获取账户名和对应openid
def __get_accounts_list() -> dict:
    _val = __get_file("accounts", "txt").split(sep="\n")
    _dct: dict = {}
    for v1 in _val:
        if v1 != "":
            v2 = v1.split(sep=",")
            _dct[v2[0]] = v2[1]
    return _dct


accounts = __get_accounts_list()


# 以字典形式获取别名
def __get_aliases_old() -> dict:
    _val = __get_file("alias", "txt").split(sep="\n")
    _dct: dict = {}
    for v1 in _val:
        v2 = v1.split(sep=",")
        _dct[v2[0]] = []
        for u in v2:
            _dct[v2[0]].append(u)
        _dct[v2[0]].pop(0)
    return _dct


ALIAS = __get_aliases_old()


# 以列表形式获取名称与别名 （未使用）
def __get_aliases_list() -> list:
    _val = __get_file("alias", "txt").split(sep="\n")
    _lst: list = []
    for v1 in _val:
        l1 = v1.split(sep=",")
        _lst.append(l1)
    return _lst


# ALIAS_OLD = __get_aliases_list()


def __get_usage_list() -> dict:
    _val = __get_file("usage", "txt").split(sep="\n")
    _dct: dict = {}
    for v1 in _val:
        l1 = v1.split(sep=",")
        _dct[l1[0]] = l1[1]
    return _dct


USAGE = __get_usage_list()


# 以字典形式加载道具卡，技能卡和角色内部名称与显示名称
def __get_cards_mapping() -> dict:
    _val = __get_file("map", "txt").split(sep="\n")
    _dct: dict = {}
    for v1 in _val:
        v2 = v1.split(sep=",")
        if len(v2) == 2:
            _dct[v2[0]] = v2[1]
    return _dct


MAP = __get_cards_mapping()


# 以字典形式加载可用角色列表
def __get_character_list() -> dict:
    _characters: Dict[str, list] = {}

    _character_types: Dict[str, List[int]] = json.loads(
        __get_file("character_type", "json")
    )
    _regenerate_types: Dict[str, List[int]] = json.loads(
        __get_file("regenerate_type", "json")
    )
    _charas: Dict[str, List[str]] = json.loads(__get_file("character", "json"))
    for chara_id, _val in _charas.items():
        if chara_id != "角色":
            _temp = [chara_id]
            _temp.extend(_character_types[_val[0]])
            _temp.extend(_regenerate_types[_val[1]])
            _characters[chara_id] = _temp
    return _characters


CHARACTER = __get_character_list()


# 加载指定名字的卡包
def __get_propcard(deck_name: str) -> list:
    _prop: List[str] = []
    _val = __get_file(f"{deck_name}_prop", "txt").split("\n")
    for v in _val:
        v2 = v.split(",")
        for i in range(0, int(v2[1])):
            _prop.append(MAP[v2[0]])
    return _prop


# 以字典形式加载所有卡包
def __get_propcard_list() -> Dict[str, list]:
    _prop_list: Dict[str, list] = {}
    _val = __get_file("prop_names", "txt").split("\n")
    for v in _val:
        _prop_list[v] = __get_propcard(v)
    return _prop_list


PROPCARD = __get_propcard_list()


# 加载技能卡堆
def __get_skill_list() -> Dict[str, int]:
    _val = __get_file("skill", "txt").split(sep="\n")
    _dct: dict = {}
    for v in _val:
        v2 = v.split(sep=",")
        _dct[v2[0]] = int(v2[1])
    return _dct


SKILL = __get_skill_list()


def __get_private_skill_list() -> Dict[str, int]:
    _val = __get_file("private_skill", "txt").split(sep="\n")
    _dct: dict = {}
    for v in _val:
        v2 = v.split(sep=",")
        _dct[v2[0]] = int(v2[1])
    return _dct


PRIVATE_SKILL = __get_private_skill_list()


def __get_trait_list() -> Dict[str, list]:
    _val = __get_file("trait", "txt").split(sep="\n")
    _dct: dict = {}
    for v in _val:
        v2 = v.split(sep=",")
        _dct[v2[0]] = []
        for u in v2:
            _dct[v2[0]].append(u)
        _dct[v2[0]].pop(0)
    return _dct


TRAIT = __get_trait_list()


def __get_tag_list() -> Dict[str, list]:
    _val = __get_file("tag", "txt").split(sep="\n")
    _dct: dict = {}
    for v in _val:
        v2 = v.split(sep=",")
        _dct[v2[0]] = []
        for u in v2:
            _dct[v2[0]].append(u)
        _dct[v2[0]].pop(0)
    return _dct


TAG = __get_tag_list()

def __get_status_list() -> Dict[str, list]:
    _val = __get_file("status", "txt").split(sep="\n")
    _dct: dict = {}
    for v in _val:
        v2 = v.split(sep=",")
        _dct[MAP[v2[0]]] = []
        for u in v2:
            try:
                _dct[MAP[v2[0]]].append(int(u))
            except ValueError:
                _dct[MAP[v2[0]]].append(u)
        _dct[MAP[v2[0]]].pop(0)
    return _dct

STATUS = __get_status_list()

def search_alias(word: str):
    def part_same(part: str, whole: str):
        is_same = False
        _x = len(whole) - len(part)
        for i in range(0, _x + 1):
            if part == whole[i : i + len(part)]:
                is_same = True
        return is_same

    _ret: list = []
    for _k, _v in ALIAS.items():
        for _s in _v:
            if part_same(word, _s) and _k not in _ret:
                _ret.append(_k)
    return _ret

def match_alias(word: str):
    _ret = 'none'
    for _k, _v in ALIAS.items():
        if word in _v or word == MAP[_k]:
            return MAP[_k]
    return _ret


def __register(id: str, name: str):
    global accounts
    with open(__ASSETS_PATH / f"accounts.txt", "w", encoding="utf-8") as f:
        try:
            if accounts[id]:
                _str = ""
                for key in accounts.keys():
                    _str += f"{key},{accounts[key]}\n"
                f.write(_str)
                return "您已注册过账户！"
        except KeyError:
            accounts[id] = name
            _str = ""
            for key in accounts.keys():
                _str += f"{key},{accounts[key]}\n"
            f.write(_str)
            return f"注册了账户 {name}！"
