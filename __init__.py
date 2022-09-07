from nonebot import require
from nonebot.plugin.on import on_command
from nonebot.adapters.onebot.v11 import (
    GROUP,
    Bot,
    GroupMessageEvent,
    MessageSegment,
    )

import os
import random
import asyncio

try:
    import ujson as json
except ModuleNotFoundError:
    import json

from .utils import *

scheduler = require("nonebot_plugin_apscheduler").scheduler

# 娶群友

record_waifu = {}

waifu = on_command("娶群友", permission=GROUP, priority = 90, block = True)

no_waifu = [
    "你没有娶到群友，强者注定孤独，加油！",
    "找不到对象.jpg",
    "恭喜你没有娶到老婆~",
    "さんが群友で結婚するであろうヒロインは、\n『自分の左手』です！"
    ]
happy_end= [
    "好耶~",
    "需要咱主持婚礼吗qwq",
    "不许秀恩爱！",
    "(响起婚礼进行曲♪)",
    "祝你们生八个。"
    ]

@waifu.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    global record_waifu
    record_waifu.setdefault(group_id,{})
    at = get_message_at(event.json())
    if at and at != user_id:
        if record_waifu[group_id].get(user_id,0) == 0:
            if record_waifu[group_id].get(at[0],0) in (0, at[0]):
                if random.randint(1,6) == 6:
                    record_waifu[group_id].update(
                        {
                            user_id: at[0],
                            at[0]: user_id
                            }
                        )
                    await waifu.send("恭喜你娶到了群友" + MessageSegment.at(at[0]), at_sender=True)
                    await asyncio.sleep(1)
                else:
                    record_waifu[group_id].update({user_id: user_id})

                member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][user_id])
            else:
                if random.randint(1,6) == 6: # 彩蛋
                    await waifu.send(
                        "人家已经名花有主了~" + 
                        MessageSegment.image(file = await user_img(record_waifu[group_id][at[0]])) +
                        MessageSegment.at(record_waifu[group_id][at[0]]) +
                        "但是...",
                        at_sender=True
                        )
                    record_waifu[group_id].pop(record_waifu[group_id][at[0]])
                    record_waifu[group_id].update(
                        {
                            user_id: at[0],
                            at[0]: user_id
                            }
                        )
                    await asyncio.sleep(1)
                else:
                    await waifu.finish(
                        "人家已经名花有主啦！" + 
                        MessageSegment.image(file = await user_img(record_waifu[group_id][at[0]])) +
                        "ta的CP：" +MessageSegment.at(record_waifu[group_id][at[0]]),
                        at_sender=True
                        )
        elif record_waifu[group_id][user_id] == at[0]:
            await waifu.finish(
                "这是你的CP！"+ MessageSegment.at(record_waifu[group_id][user_id]) + '\n' +
                random.choice(happy_end) +
                MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])),
                at_sender=True
                )
        elif record_waifu[group_id][user_id] == user_id:
            await waifu.finish(random.choice(no_waifu), at_sender=True)
        else:
            await waifu.finish(
                "你已经有CP了，不许花心哦~" +
                MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])) +
                "你的CP：" + MessageSegment.at(record_waifu[group_id][user_id]),
                at_sender=True
                )

    if record_waifu[group_id].get(user_id,0) == 0:
        member_list = await bot.get_group_member_list(group_id = event.group_id)
        i = 0
        while i < len(member_list):
            if member_list[i]['user_id'] in record_waifu[group_id].keys():
                del member_list[i]
            else:
                i += 1
        else:
            if member_list:
                member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
                member = random.choice(member_list[:80])
                record_waifu[group_id].update(
                    {
                        user_id: member['user_id'],
                        member['user_id']: user_id
                        }
                    )
            else:
                record_waifu[group_id][user_id] = 1
    else:
        member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][user_id])

    if record_waifu[group_id][user_id] == event.user_id:
        msg = random.choice(no_waifu)
    elif record_waifu[group_id][user_id] == 1:
        msg = "群友已经被娶光了、\n" + random.choice(no_waifu)
    else:
        nickname = member['card'] or member['nickname']
        msg = (
            "さん的群友結婚对象是、\n",
            MessageSegment.image(file = await user_img(record_waifu[group_id][user_id])),
            f"『{nickname}』です！"
            )
    await waifu.finish(msg, at_sender=True)

# 查看娶群友卡池

waifu_list = on_command("查看群友卡池", aliases = {"群友卡池"}, permission=GROUP, priority = 90, block = True)

@waifu_list.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    member_list = await bot.get_group_member_list(group_id = event.group_id)
    i = 0
    while i < len(member_list):
        if member_list[i]['user_id'] in record_waifu.setdefault(event.group_id,{}).keys():
            del member_list[i]
        else:
            i += 1
    else:
        if member_list:
            member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
            msg ="卡池：\n——————————————\n"
            for i in range(len(member_list[:80])):
                nickname = member_list[i]['card'] or member_list[i]['nickname']
                msg += f"{nickname}\n"
            else:
                output = text_to_png(msg[:-1])
                await waifu_list.finish(MessageSegment.image(output))
        else:
            await waifu_list.finish("卡池为空，群友已经被娶光了...")

# 查看本群CP

cp_list = on_command("本群CP", aliases = {"本群cp"}, permission=GROUP, priority = 90, block = True)

@cp_list.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    global record_waifu
    record_waifu.setdefault(group_id,{})
    lst = record_waifu[group_id].keys()
    if lst:
        listA = []
        listB = []
        for A in lst:
            listA.append(A)
            B = record_waifu[group_id][A]
            if B not in listA and B != A:
                listB.append(B)

        msg = "本群CP：\n——————————————\n"
        for user_id in listB:
            member = await bot.get_group_member_info(group_id = group_id, user_id = record_waifu[group_id][user_id])
            niknameA = member['card'] or member['nickname']
            member = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
            niknameB = member['card'] or member['nickname']
            msg += f"♥ {niknameA} | {niknameB}\n"

        output = text_to_png(msg[:-1])
        await cp_list.finish(MessageSegment.image(output))

    else:
        await cp_list.finish("本群暂无cp哦~")


# 透群友

record_yinpa = {}

yinpa = on_command("透群友", permission=GROUP, priority = 90, block = True)

@yinpa.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    group_id = event.group_id
    user_id = event.user_id
    member_list = await bot.get_group_member_list(group_id = event.group_id)
    member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
    member = random.choice(member_list[:80])

    if member["user_id"] == event.user_id:
        msg = "不可以涩涩！"
    else:
        nickname = member['card'] or member['nickname']
        global record_yinpa
        record_yinpa.setdefault(member['user_id'],0)
        record_yinpa[member['user_id']] += 1
        msg = (
            "さんが群友で涩涩するであろうヒロインは、\n",
            MessageSegment.image(file = await user_img(member["user_id"])),
            f"『{nickname}』です！"
            )
    await yinpa.finish(msg, at_sender=True)

# 查看涩涩记录

yinpa_list = on_command("涩涩记录",aliases = {"色色记录"}, permission=GROUP, priority = 90, block = True)

@yinpa_list.handle()
async def _(bot:Bot, event: GroupMessageEvent):
    member_list = await bot.get_group_member_list(group_id = event.group_id)
    member_list.sort(key = lambda x:x["last_sent_time"] ,reverse = True)
    record = []
    for i in range(len(member_list)):
        nickname = member_list[i]['card'] or member_list[i]['nickname']
        global record_yinpa
        times = record_yinpa.get(member_list[i]['user_id'],0)
        if times:
            record.append([nickname,times])
    else:
        record.sort(key = lambda x:x[1],reverse = True)

    msg_list =[]
    msg ="卡池：\n——————————————\n"
    for i in range(len(member_list[:80])):
        nickname = member_list[i]['card'] or member_list[i]['nickname']
        msg += f"{nickname}\n"
    else:
        output = text_to_png(msg[:-1])
        msg_list.append(
            {
                "type": "node",
                "data": {
                    "name": "卡池",
                    "uin": event.self_id,
                    "content": MessageSegment.image(output)
                    }
                }
            )

    msg =""
    for i in range(len(record)):
        msg += f"{i+1}.【{record[i][0]}】\n        今日被透 {record[i][1]} 次\n"
    else:
        if msg:
            output = text_to_png("涩涩记录：\n——————————————\n" + msg[:-1])
            msg_list.append(
                {
                    "type": "node",
                    "data": {
                        "name": "记录",
                        "uin": event.self_id,
                        "content": MessageSegment.image(output)
                        }
                    }
                )
        else:
            pass
    await bot.send_group_forward_msg(group_id = event.group_id, messages = msg_list)

# 重置娶群友记录

@scheduler.scheduled_job("cron",hour = 0)
def _():
    global record_waifu,record_yinpa
    record_waifu = {}
    record_yinpa = {}