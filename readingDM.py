# -*- coding: utf-8 -*-
import asyncio

from src.blivedm import blivedm

async def runClient():
    """
    演示监听一个直播间
    """
    room_id = 24924777
    #room_id = 768756

    # 如果SSL验证失败就把ssl设为False，B站真的有过忘续证书的情况
    client = blivedm.BLiveClient(room_id, ssl = True)
    handler = MyHandler()
    client.add_handler(handler)
    client.start()
    try:
        await client.join()
    finally:
        await client.stop_and_close()

class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    #async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
    #    print(f'当前人气值：{message.popularity}')

    # 新功能函数只需在models.py添加新class(具体返回的值), 并在handler.py中BaseHandler中添加函数原型(有三个需要添加的部分, 注意检查IGNORED_CMDS), 具体功能实现在本程序中重载
    async def _on_interact(self, client: blivedm.BLiveClient, message: blivedm.InteractMessage):
        print(f'欢迎 {message.uname} 进入直播间!')
        dm = f'欢迎 {message.uname} 进入直播间!'
        open('temp/headBubble.txt', 'w', encoding = 'utf-8').write(dm)   # 将读取到的弹幕写入头部气泡

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        print(f'{message.uname}：{message.msg}')
        dm = f'{message.uname}：{message.msg}'
        open('temp/liveDM.txt', 'w', encoding = 'utf-8').write(dm)   # 将读取到的弹幕写入头部气泡

    #async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
    #    print(f'{message.uname} 赠送{message.gift_name}x{message.num}'
    #          f' （{message.coin_type}瓜子x{message.total_coin}）')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        print(f'{message.username} 购买{message.gift_name}')
        dm = f'{message.username} 购买{message.gift_name}'

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        print(f'醒目留言 ¥{message.price} {message.uname}：{message.message}')
        dm = f'醒目留言 ¥{message.price} {message.uname}：{message.message}'

asyncio.run(runClient())