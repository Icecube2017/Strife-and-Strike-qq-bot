# -*- coding:utf-8 -*-

from typing import Tuple, Dict
import time
from dataclasses import dataclass

from nonebot import get_driver, on_startswith, get_bot, on_message
from nonebot.rule import Rule
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.params import State, EventPlainText
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, GroupMessageEvent

sns = on_startswith({"sns", "SNS"}, priority=10)

