# -*- coding: utf-8 -*-
import asyncio
import os
import random
from cgitb import handler
from importlib.resources import contents

import assets
import game
import classes

import botpy
from botpy import logging, BotAPI
from botpy.ext.cog_yaml import read
from botpy.ext.command_util import Commands
from botpy.message import GroupMessage, Message, C2CMessage

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

GROUP_ID = "2410AB7265A435E36F39DC671B6D913A"

@Commands('/echo')
async def echo(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    _pl_lst = _par_lst[0].split(sep='，')
    _card_lst = _par_lst[1].split(sep='，')
    _extra_lst = _par_lst[2].split(sep='，')
    print(_pl_lst, _card_lst, _extra_lst)
    await message.reply(content=f'{params}')
    return True

@Commands("/alias")
async def alias(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _lst = assets.search_alias(_para)
    if len(_lst) == 1:
        _word = _lst[0]
        _tag_cnt = ''
        for _c in assets.TAG[_word]:
            _tag_cnt += f'{_c} '
        _cnt = f'[SnS Aliases]\n{_word}：{assets.USAGE[_word]}\n标签：{_tag_cnt}\n====================\n已查询到以下别名:\n'
        for i in range(0, len(assets.ALIAS[_word])):
            _cnt += f'({i+1}){assets.ALIAS[_word][i]}\n'
        await api.post_group_message(group_openid=message.group_openid ,content=_cnt,msg_id=message.id)
    elif len(_lst) > 1:
        _cnt = f'[SnS Aliases]\n====================\n匹配不唯一，请重新查询:\n'
        for i in range(0, len(_lst)):
            _cnt += f'({i+1}){assets.MAP[_lst[i]]}\n'
        await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)
    else:
        await api.post_group_message(group_openid=message.group_openid ,content=f'[SnS Aliases]\n未查询到对应别名！请检查是否有输入错误',msg_id=message.id)
    return True

@Commands("/newgame", "/new")
async def new_game(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.new_game(message.group_openid, message.author.member_openid, int(_para))
    print(message.group_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/cancel")
async def cancel_game(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.cancel_game(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/join")
async def join_game(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.join_game(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/quit")
async def quit_game(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.quit_game(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/character", "/chara")
async def set_chara(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.set_character(message.group_openid, message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/ban")
async def ban_chara(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.ban_character(message.group_openid, message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/unban")
async def unban_chara(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.unban_character(message.group_openid, message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/setbannum")
async def set_ban_num(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.set_ban_num(message.group_openid, message.author.member_openid, int(_para))
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/team")
async def set_team(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.set_team(message.group_openid, message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/withdraw")
async def quit_team(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.quit_team(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/deck")
async def set_deck(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.set_deck(message.group_openid, message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/start")
async def start_game(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.start_game(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/dice")
async def dice(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _rand = random.randint(1, int(_para))
    _cnt = f"你投掷了骰子……d{_para}={_rand}"
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/draw")
async def draw(api: BotAPI, message: C2CMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.draw(GROUP_ID, message.author.user_openid)
    await api.post_c2c_message(openid=message.author.user_openid, content=_cnt, msg_id=message.id)

@Commands("/card")
async def card(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    _tg_lst = _par_lst[0].split(sep='，')
    _card_lst = []
    _extra_lst = []
    if len(_par_lst) > 1:
        _card_lst = _par_lst[1].split(sep='，')
    if len(_par_lst) > 2:
        _extra_lst = _par_lst[2].split(sep='，')
    _cnt = game.play_card(message.group_openid, message.author.member_openid, _tg_lst, _card_lst, _extra_lst)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/skill")
async def skill(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    _tg_lst = _par_lst[0].split(sep='，')
    _skill_lst = _par_lst[1]
    _extra_lst = []
    if len(_par_lst) > 2:
        _extra_lst = _par_lst[2].split(sep='，')
    _cnt = game.play_skill(message.group_openid, message.author.member_openid, _tg_lst, _skill_lst, _extra_lst)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/trait")
async def trait(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    _tg_lst = _par_lst[0].split(sep='，')
    _skill_lst = _par_lst[1]
    _extra_lst = []
    if len(_par_lst) > 2:
        _extra_lst = _par_lst[2].split(sep='，')
    _cnt = game.play_trait(message.group_openid, message.author.member_openid, _tg_lst, _skill_lst, _extra_lst)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/fold")
async def fold(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    _card_lst = _par_lst[0].split(sep='，')
    _cnt = game.fold_card(message.group_openid, message.author.member_openid, _card_lst)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/pass")
async def pass_turn(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    _cnt = game.pass_turn(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/info")
async def player_info(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.player_info(message.group_openid, message.author.member_openid)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/init")
async def init(api: BotAPI, message: GroupMessage, params):
    _par_lst = params.split(sep=' ')
    game.new_game('2410AB7265A435E36F39DC671B6D913A', '7758FDF03BDCD44055806E9245E4F264', 0)
    game.join_game('2410AB7265A435E36F39DC671B6D913A', '9C74E4EEE32610EAF5DFEC1C1C968660')
    game.set_character('2410AB7265A435E36F39DC671B6D913A', '7758FDF03BDCD44055806E9245E4F264', '敏博士')
    game.set_character('2410AB7265A435E36F39DC671B6D913A', '9C74E4EEE32610EAF5DFEC1C1C968660', '安德宁')
    game.set_deck('2410AB7265A435E36F39DC671B6D913A', '7758FDF03BDCD44055806E9245E4F264', 'test')
    _cnt = game.start_game('2410AB7265A435E36F39DC671B6D913A','7758FDF03BDCD44055806E9245E4F264')
    game.set_skill('2410AB7265A435E36F39DC671B6D913A', '7758FDF03BDCD44055806E9245E4F264', '外星人')
    game.set_skill('2410AB7265A435E36F39DC671B6D913A', '9C74E4EEE32610EAF5DFEC1C1C968660', '相转移')
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

@Commands("/setskill")
async def set_skill(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = game.set_skill(message.group_openid, message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

_prop_card = assets.PROPCARD['basic'].copy()
@Commands("/adraw")
async def adraw(api: BotAPI, message: C2CMessage, params):
    global _prop_card
    _para = params.split(sep=' ')[0]
    print(len(_prop_card))
    if int(_para) > len(_prop_card):
        _cnt = "牌堆不够啦"
    else:
        _cnt = f"你抽到了："
        for i in range(0, int(_para)):
            _card = random.choice(_prop_card)
            _prop_card.remove(_card)
            _cnt += (_card + ' ')
    await api.post_c2c_message(openid=message.author.user_openid, content=_cnt, msg_id=message.id)

_skill_deck = assets.SKILL.copy()
@Commands("/askill")
async def askill(api: BotAPI, message: C2CMessage, params):
    global _skill_deck
    _para = params.split(sep=' ')[0]
    print(len(_skill_deck))
    if int(_para) > len(_skill_deck):
        _cnt = "牌堆不够啦"
    else:
        _cnt = f"你抽到了："
        for i in range(0, int(_para)):
            _rand = random.choice(list(_skill_deck.keys()))
            del _skill_deck[_rand]
            _cnt += (_rand + ' ')
    await api.post_c2c_message(openid=message.author.user_openid, content=_cnt, msg_id=message.id)

@Commands("/areset")
async def areset(api: BotAPI, message: GroupMessage, params):
    global _prop_card
    _prop_card = assets.PROPCARD['basic'].copy()
    await api.post_group_message(group_openid=message.group_openid, content="已重置牌堆！", msg_id=message.id)

@Commands("/register", "/reg")
async def register(api: BotAPI, message: GroupMessage, params):
    _para = params.split(sep=' ')[0]
    _cnt = assets.__register(message.author.member_openid, _para)
    await api.post_group_message(group_openid=message.group_openid, content=_cnt, msg_id=message.id)

class MyClient(botpy.Client):
    async def on_ready(self):

        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        handlers = [echo, init, alias, register, new_game, cancel_game, join_game, quit_game, set_chara, ban_chara,
                    unban_chara, set_ban_num, set_team, quit_team, set_deck, start_game, dice, card, skill, trait, fold,
                    pass_turn, player_info, areset, set_skill]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return 0
        # await message.reply(content="指令不在handlers中")

    async def on_c2c_message_create(self, message: C2CMessage):
        handlers = [adraw, draw, askill]
        for handler in handlers:
            if await handler(api=self.api, message=message):
                return 0


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents, is_sandbox=True)
    client.run(appid=test_config["appid"], secret=test_config["secret"])