#把指令由!轉換成/
import asyncio
import json
import math
import os
import random
import signal
from typing import Optional
import discord
import logging
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import requests
import re
from discord import AppCommandOptionType, app_commands

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

global bet
global png
# 設置中文字體
font = FontProperties(fname=r"discord/point/NotoSerifTC-SemiBold.otf", size=14)
font1 = FontProperties(fname=r"discord/point/NotoSerifTC-Regular.otf", size=14)

# 设置日志记录器
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord/point/discord.log', encoding='utf-8', mode='a')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logging.Formatter.converter = time.localtime
handler.setFormatter(formatter)
logger.addHandler(handler)

@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    game = discord.Game('Age of Empires II: Definitive Edition')
    await client.change_presence(status=discord.Status.online, activity=game)
    await tree.sync(guild=discord.Object(id=1084715410768805958))
    logger.info(f'{client.user} 開始運作' )


# 記錄每個用戶的點數
member_id = {}
member_list = []
start_time = 0
tmp = 0
total_sum = 0
total_sum_A = 0
total_sum_B = 0
selected_options={}
update = False
bet = False
voice_channel = [1084715410768805962,1084757284879609926]
png = True
option_list = []
question = None
target_channel_id = None
target_channel = None
low_morals=[]
examine_message_ids = []
examine_message_ids1 = []
task_elapsed = None
replace = None

@tree.command(name = "query_coin", description = "查詢自己的社畜幣", guild=discord.Object(id=1084715410768805958))
async def querycoin_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/query_coin")
    global voice_channel
    global start_time
    global tmp
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中查詢社畜幣餘額。")
        return
    user_id = interaction.user.id
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    if points[str(user_id)]["start_time"] != None:
        start_time = datetime.fromtimestamp(points[str(user_id)]['start_time'])
        current_time = datetime.now()
        elapsed_time = current_time - start_time
        elapsed_seconds = elapsed_time.total_seconds()
        while elapsed_seconds > 0:
            if elapsed_seconds >= 60:
                elapsed_seconds -= 60
                tmp += 2
            else:
                elapsed_seconds = 0
        points[str(user_id)]['points'] += tmp
            
        guild_id = 1084715410768805958  # 輸入伺服器 ID
        guild = client.get_guild(guild_id)
        member = guild.get_member(interaction.user.id)
        if member.voice.channel.id in voice_channel:
            points[str(user_id)]["start_time"] = datetime.now().timestamp()
        else:
            points[str(user_id)]["start_time"] = None
        tmp = 0
        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
            json.dump(points, f, indent=2)

    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    user_points = points[str(user_id)]['points']    
    await interaction.response.send_message(f"{interaction.user.mention}現在有社畜幣 {user_points} 點")

@tree.command(name = "myrank", description = "查詢自己的社畜幣排名", guild=discord.Object(id=1084715410768805958))
async def myrank_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/myrank")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中查詢自己的社畜幣排名。")
        return
    user_id = interaction.user.id
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    ranked_list = sorted(points.items(),key=lambda x: x[1]["points"],reverse=True)
    num_iterations = math.ceil(len(ranked_list) / 50)
    my_rank = None
    for j in range(num_iterations):
        for myrank, (userid, points) in enumerate(ranked_list[j * 50:(j + 1) * 50],start=j * 50 + 1):
            if myrank > len(ranked_list):
                break
            # 新增變數以紀錄自己的排名
            if userid == str(user_id):
                my_rank = myrank
    if my_rank:
        await interaction.response.send_message(f"{interaction.user.mention}目前的社畜幣排名是第{my_rank}名！")
    else:
        await interaction.response.send_message(f"很抱歉，{interaction.user.mention}目前沒有排名。")
        
@tree.command(name = "steal", description = "偷走別人財產", guild=discord.Object(id=1084715410768805958))
async def steal_command(interaction,user:discord.Member,amount:int):
    """
    Description of the command.

    :param user: 選擇偷竊的對象
    :type user: str
    :param amount: 輸入偷竊金額(整數)
    :type amount: int
    """
    logger.info(f"{interaction.user.name} 輸入指令:/steal 選擇偷竊的對象:{user.mention} 輸入偷竊金額:{amount}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中使用偷竊。")
        return
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    global low_morals
    members = user
    amount = amount
    user_id = interaction.user.id
    user_name = interaction.user.name
    members_id = members.id
    if str(members_id) in points:
        if amount > 0:
            if points[str(user_id)]["points"] >= amount and points[str(members_id)]["points"] >= amount:
                random_number = random.randint(0, 100)
                if user_id in low_morals:
                    if random_number == 100:
                        points[str(user_id)]["points"] += math.ceil(amount*1.5)
                        points[str(members_id)]["points"] -= amount
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                        await interaction.response.send_message(f"{interaction.user.mention} 運氣爆棚，達成{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣，並且獲得額外獎勵{math.ceil(amount*0.5)}點社畜幣！(由於道德低下，只有獲得一半的獎勵)\n{interaction.user.mention} 道德值沒有下降")
                    elif random_number >= 95:
                        points[str(user_id)]["points"] += amount
                        points[str(members_id)]["points"] -= amount
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                        await interaction.response.send_message(f"{interaction.user.mention} 靠著{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣！\n{interaction.user.mention} 道德值下降(需在 <#888410932722683935> 反省一小時來消除心中的罪惡感)")
                        logger.info(f"{user_name} 道德值下降")
                    else:
                        points[str(user_id)]["points"] -= amount
                        points["1084715001593475082"]["points"] += math.floor(amount*0.6)
                        points[str(members_id)]["points"] += math.ceil(amount*0.4)
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                        await interaction.response.send_message(f"{interaction.user.mention} 此次偷竊的成功率為 {random_number}%，但可惜功虧一簣，損失了 {amount} 點社畜幣！(由於你是個道德低下的人，成功機率須達95%以上，才可偷竊成功)\n{members.mention} 成功守住自己的財務，獲得了 {math.ceil(amount*0.4)} 點社畜幣！")
                else:
                    if random_number == 100:
                        points[str(user_id)]["points"] += amount*2
                        points[str(members_id)]["points"] -= amount
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                        await interaction.response.send_message(f"{interaction.user.mention} 運氣爆棚，達成{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣，並且獲得額外獎勵{amount}點社畜幣！\n{interaction.user.mention} 道德值沒有下降")
                    elif random_number >= 85:
                        points[str(user_id)]["points"] += amount
                        points[str(members_id)]["points"] -= amount
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                        await interaction.response.send_message(f"{interaction.user.mention} 靠著{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣！\n{interaction.user.mention} 道德值下降(需在 <#888410932722683935> 反省一小時來消除心中的罪惡感)")
                        logger.info(f"{user_name} 道德值下降")
                        low_morals.append(user_id)
                    else:
                        points[str(user_id)]["points"] -= amount
                        points["1084715001593475082"]["points"] += math.floor(amount*0.6)
                        points[str(members_id)]["points"] += math.ceil(amount*0.4)
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                        await interaction.response.send_message(f"{interaction.user.mention} 此次偷竊的成功率為 {random_number}%，但可惜功虧一簣，損失了 {amount} 點社畜幣！(成功機率須達85%以上，才可偷竊成功)\n{members.mention} 成功守住自己的財務，獲得了 {math.ceil(amount*0.4)} 點社畜幣！")
            else:
                await interaction.response.send_message(f"{interaction.user.mention} 或是 {members.mention} 沒這麼多社畜幣\n但我不告訴你他有多少社畜幣，偷竊此風不可長啊")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} 不能偷0或負數 :rage: ")
    else:
        await interaction.response.send_message(f"機器人翻遍了資料庫，但還是找不到 {members.mention} 的資料")

@tree.command(name = "moral_value", description = "道德值", guild=discord.Object(id=1084715410768805958))
async def moralvalue_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/moral_value")
    global low_morals
    user_id = interaction.user.id
    if user_id in low_morals:
        await interaction.response.send_message(f"{interaction.user.mention}是一名道德低下之人，還不趕緊去讓我靜靜<#888410932722683935>坐坐\n(要在裡面待一小時以上，然後離開語音頻道才會觸發，期間不可使用查詢等功能)")
    else:
        await interaction.response.send_message(f"道德值是一種很玄奧的道理，請施主靜下心來仔細感受。\ntip:江湖相傳在讓我靜靜<#888410932722683935>坐坐後，會心靈祥和")

@tree.command(name = "ranklist", description = "查詢所有人社畜幣排名", guild=discord.Object(id=1084715410768805958))
async def ranklist_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/ranklist_command")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    member = interaction.user
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中查詢社畜幣排名。")
        return
    if "測試" not in [role.name for role in member.roles]:
        await interaction.response.send_message("你沒有權限查詢社畜幣排名。")
        return
    
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    ranked_list = sorted(points.items(),key=lambda x: x[1]["points"],reverse=True)
    num_iterations = math.ceil(len(ranked_list) / 50)
    await interaction.response.send_message("社畜幣排行榜")
    for j in range(num_iterations):
        table = "排名\t\t名稱\t\t社畜幣\n"
        for i, (user_id, points) in enumerate(ranked_list[j * 50:(j + 1) * 50],start=j * 50 + 1):
            if i > len(ranked_list):
                break
            name = points['name']
            points = points['points']
            table += f"**No.{i}**\t\t{name}\t\t*{points}*\n"
            
        messagechannel = client.get_channel(1084715410768805961)# 限定的頻道 ID
        message = await messagechannel.send(f"\n{table}")

@tree.command(name = "create_poll", description = "創建投票", guild=discord.Object(id=1084715410768805958))
async def createpoll_command(interaction,title:str,option_a:str,option_b:str):
    """
    Description of the command.

    :param title: 投票標題
    :type title: str
    :param option_a: 選項A
    :type option_a: str
    :param option_b: 選項B
    :type option_b: str
    """
    logger.info(f"{interaction.user.name} 輸入指令:/create_poll 投票標題:{title} 選項A:{option_a} 選項B:{option_b}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    member = interaction.user
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中創建投票。")
        return
    if "測試" not in [role.name for role in member.roles]:
        await interaction.response.send_message("你沒有權限創建投票。")
        return
    global bet
    global question
    global option_list
    bet = True
    question = title
    option_list = [option_a,option_b]

    embed = discord.Embed(title=title, description="選項", color=0x00ff00)
    embed.add_field(name="選項A", value=option_a, inline=False)
    embed.add_field(name="選項B", value=option_b, inline=False)
    messagechannel = client.get_channel(1084715410768805961)# 限定的頻道 ID
    message = await messagechannel.send(embed=embed)
    await message.add_reaction("\U0001F1E6")
    await message.add_reaction("\U0001F171")
    await interaction.response.send_message("5分鐘後下注截止，請有意下注者動作迅速，感謝配合")
    asyncio.ensure_future(clear_reactions(message))

@tree.command(name = "poll_result", description = "投票結果", guild=discord.Object(id=1084715410768805958))
@app_commands.choices(result=[
        app_commands.Choice(name="選項A", value="0"),
        app_commands.Choice(name="選項B", value="1")
    ])
async def createpoll_command(interaction,result:app_commands.Choice[str]):
    """
    Description of the command.

    :param result: 選擇結果
    :type result: str
    """
    logger.info(f"{interaction.user.name} 輸入指令:/poll_result 選擇結果:{result.name}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    member = interaction.user
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中選擇投票結果。")
        return
    if "測試" not in [role.name for role in member.roles]:
        await interaction.response.send_message("你沒有權限選擇投票結果。")
        return
    global selected_options
    global update
    global bet
    global png
    global option_list
    global question
    ans = result.name
    with open('discord/point/option.json', 'r', encoding='UTF-8') as file:
        option = json.load(file)
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    if option_list == []:
        await interaction.response.send_message("找不到題目，請重新輸入")
        return
    if ans == "選項A":
        for user_id, info in option["option_A"]["betting"].items():
            betting = info["betting"]
            magnification = option["option_A"]["magnification"]
            points[str(user_id)]['points'] += int(betting * magnification)
            with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                json.dump(points, f, indent=2)
            user = await client.fetch_user(user_id)
            with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                points = json.load(file)
            user_points = points[user_id]['points']
            await user.send(f'恭喜你獲得{int(betting * magnification)}點，目前社畜幣為{user_points}')
            logger.info(f'{user.name} 在{question}，選擇A選項:{option_list[0]}，成功獲得{int(betting * magnification)}點社畜幣')
        await interaction.response.send_message(f"恭喜選項A {option_list[0]} 獲勝")
        selected_options={}
        option["option_A"]["total"] = 0
        option["option_A"]["magnification"] = 0.0
        option["option_A"]["people"] = 0
        option["option_A"]["betting"] ={}
        
        option["option_B"]["total"] = 0
        option["option_B"]["magnification"] = 0.0
        option["option_B"]["people"] = 0
        option["option_B"]["betting"] ={}
        
        with open('discord/point/option.json', 'w', encoding='UTF-8') as f:
            json.dump(option, f, indent=2)
        update = False
        bet = False
        png = True
        option_list = []
        question = None
    elif ans == "選項B":
        for user_id, info in option["option_B"]["betting"].items():
            betting = info["betting"]
            magnification = option["option_B"]["magnification"]
            points[str(user_id)]['points'] += int(betting * magnification)
            with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                json.dump(points, f, indent=2)
            user = await client.fetch_user(user_id)
            with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                points = json.load(file)
            user_points = points[user_id]['points']
            await user.send(f'恭喜你獲得{int(betting * magnification)}點，目前社畜幣為{user_points}')
            logger.info(f'{user.name} 在{question}，選擇B選項:{option_list[1]}，成功獲得{int(betting * magnification)}點社畜幣')
        await interaction.response.send_message(f"恭喜選項B {option_list[1]} 獲勝")
        selected_options={}
        option["option_A"]["total"] = 0
        option["option_A"]["magnification"] = 0.0
        option["option_A"]["people"] = 0
        option["option_A"]["betting"] ={}
        
        option["option_B"]["total"] = 0
        option["option_B"]["magnification"] = 0.0
        option["option_B"]["people"] = 0
        option["option_B"]["betting"] ={}
        
        with open('discord/point/option.json', 'w', encoding='UTF-8') as f:
            json.dump(option, f, indent=2)
        update = False
        bet = False
        png = True
        option_list = []
        question = None

@tree.command(name = "update_png", description = "刷新投票圖片", guild=discord.Object(id=1084715410768805958))
async def ranklist_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/update_png")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    member = interaction.user
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中刷新投票圖片。")
        return
    if "測試" not in [role.name for role in member.roles]:
        await interaction.response.send_message("你沒有權限刷新投票圖片。")
        return
    global update
    global png
    update = True
    png = True
    await interaction.response.send_message("正在刷新圖片")
    await chart_task()
 
@tree.command(name = "stopupdate_png", description = "停止刷新投票圖片", guild=discord.Object(id=1084715410768805958))
async def ranklist_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/stopupdate_png")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    member = interaction.user
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中停止刷新投票圖片。")
        return
    if "測試" not in [role.name for role in member.roles]:
        await interaction.response.send_message("你沒有權限停止刷新投票圖片。")
        return
    global update
    update = False
    await interaction.response.send_message("已停止刷新")

@tree.command(name = "query_bounty", description = "查詢現有的懸賞", guild=discord.Object(id=1084715410768805958))
async def querybounty_command(interaction):
    logger.info(f"{interaction.user.name} 輸入指令:/query_bounty")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中查詢現有的懸賞。")
        return
    table = await send_task_table(interaction.channel)
    if table:
        await interaction.response.send_message(content=table)
    else:
        await interaction.response.send_message(content="**懸賞列表**")


@tree.command(name="post_bounty", description="發布懸賞", guild=discord.Object(id=1084715410768805958))
@app_commands.choices(type=[
        app_commands.Choice(name="記錄檔檢討", value="510"),
        app_commands.Choice(name="實戰佐為教學", value="1020"),
        app_commands.Choice(name="單挑", value="600"),
        app_commands.Choice(name="團戰陪打", value="500"),
        app_commands.Choice(name="遊戲內容教學", value="800"),
        app_commands.Choice(name="遊戲表演", value="400"),
        app_commands.Choice(name="其他", value="1000")
    ])
@app_commands.choices(score=[
        app_commands.Choice(name="1000分以下", value="1.01"),
        app_commands.Choice(name="1000-1199分", value="1.04"),
        app_commands.Choice(name="1200-1399分", value="1.07"),
        app_commands.Choice(name="1400-1599分", value="1.15"),
        app_commands.Choice(name="1600-1799分", value="1.35"),
        app_commands.Choice(name="1800-1999分", value="1.55"),
        app_commands.Choice(name="2000分↑", value="1.95")
    ])
@app_commands.choices(limit_score=[
        app_commands.Choice(name="不限分數", value="1"),
        app_commands.Choice(name="1000-1199分", value="1.2"),
        app_commands.Choice(name="1200-1399分", value="1.4"),
        app_commands.Choice(name="1400-1599分", value="1.6"),
        app_commands.Choice(name="1600-1799分", value="1.8"),
        app_commands.Choice(name="1800-1999分", value="2.1"),
        app_commands.Choice(name="2000分↑", value="2.5")
    ])
async def postbounty_command(interaction,type:app_commands.Choice[str],other:Optional[str],score:app_commands.Choice[str],limit_score:app_commands.Choice[str],games:int):
    """
    Description of the command.

    :param type: 懸賞類型
    :type type: str
    :param other: 戰術內容描述(選填)
    :type other: str
    :param score: 目前分數
    :type score: str
    :param limit_score: 接單人分數需求
    :type limit_score: str
    :param games: 場數(請填整數)
    :type games: int
    """
    if other:
        logger.info(f"{interaction.user.name} 輸入指令:/post_bounty 懸賞類型:{type.name} 戰術內容描述:{other} 目前分數:{score.name} 接單人分數需求:{limit_score.name} 場數:{games}場")
    else:
        logger.info(f"{interaction.user.name} 輸入指令:/post_bounty 懸賞類型:{type.name} 目前分數:{score.name} 接單人分數需求:{limit_score.name} 場數:{games}場")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中發布懸賞。")
        return
    global release_word
    global release_reward
    global release_id
    global release_name
    release_id = interaction.user.id
    release_name = interaction.user.name
    release_reward = math.ceil(float(type.value)*float(score.value)*float(limit_score.value)*games)
    
    with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
        task = json.load(file)
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    if other:
        release_word = release_name+":懸賞類型:"+type.name+"，內容描述:"+other+"，目前分數:"+score.name+"，接單人分數需求:"+limit_score.name+"，場數:"+str(games)+"場"
    else:
        release_word = release_name+":懸賞類型:"+type.name+"，目前分數:"+score.name+"，接單人分數需求:"+limit_score.name+"，場數:"+str(games)+"場"
    if release_word not in task:
        if points[str(release_id)]["points"] >= release_reward:
            points[str(release_id)]["points"] -= release_reward
            with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                json.dump(points, f, indent=2)
            await interaction.response.send_message(f"此懸賞預計花費{release_reward}點社畜幣，確定要發布嗎")
            check = client.get_channel(1097354533337825400)#check
            embed = discord.Embed(title='發布懸賞', description=f"{release_word} {release_reward}")
            embed.set_footer(text=f"請發布人:{release_name}自行按表情確認喔")            
            message = await check.send(embed=embed)
            await message.add_reaction("⭕")
            await message.add_reaction("❌")
        else:
            await interaction.response.send_message(f"發布懸賞失敗，{interaction.user.mention}沒有這麼多社畜幣:sob:，這個懸賞需要{release_reward}點社畜幣")
    else:
        await interaction.response.send_message(f"{release_word}懸賞已經存在")

@tree.command(name = "accept_bounty", description = "接取懸賞", guild=discord.Object(id=1084715410768805958))
async def acceptbounty_command(interaction,title:str):
    """
    Description of the command.

    :param title: 懸賞名稱
    :type title: str
    """
    logger.info(f"{interaction.user.name} 輸入指令:/accept_bounty 懸賞名稱:{title}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中接取懸賞。")
        return
    user_id = interaction.user.id
    user_name = interaction.user.name
    with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
        task = json.load(file)
    word = title
    if word in task:
        if task[word]["receiver"] is None:
            if task[word]["release"] != user_name:
                task[word]["receiver"] = user_name
                task[word]["receiver_id"] = user_id
                task[word]["task_time"] = datetime.now().timestamp()
                release_id = task[word]["release_id"]
                with open('discord/point/task.json', 'w', encoding='UTF-8') as f:
                    json.dump(task, f, indent=2)
                await interaction.response.send_message(f"{interaction.user.mention} 成功接取懸賞：{word} 72小時內需要完成任務，否則自動放棄。通知發布者<@{release_id}>\n注意:完成懸賞後請截圖給管理員來結算，並且系統會抽取20%報酬")
            else:
                await interaction.response.send_message(f"{interaction.user.mention} 不能接取自己發布懸賞")
        else:
            await interaction.response.send_message(f"{word} 懸賞已被接取")
    else:
        await interaction.response.send_message(f"{word} 懸賞不存在")

@tree.command(name = "finish_bounty", description = "完成懸賞", guild=discord.Object(id=1084715410768805958))
async def finishbounty_command(interaction,title:str):
    """
    Description of the command.

    :param title: 懸賞名稱
    :type title: str
    """
    logger.info(f"{interaction.user.name} 輸入指令:/finish_bounty 懸賞名稱:{title}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中完成懸賞。")
        return
    global release_words
    global release_name
    global release_id
    with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
        task = json.load(file)
    release_words = title
    release_name = interaction.user.name
    release_id = interaction.user.id
    if release_words in task:
        if task[release_words]["release_id"] == interaction.user.id or interaction.user.id == 525348260399939594:
            if task[release_words]["receiver"] is not None:
                await interaction.response.send_message("管理員審核中。注意:請截圖給管理員以證明完成!\n**(有洗分嫌疑的不會通過)**")
                check = client.get_channel(1097354533337825400)#check
                embed = discord.Embed(title='完成懸賞', description=f"{release_words}")
                embed.set_footer(text=f"發布人:{release_name}")
                message = await check.send(embed=embed)
                await message.add_reaction("🙆")
                await message.add_reaction("🙅")
            else:
                await interaction.response.send_message(f"{release_words} 懸賞還沒有人接取")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} 你不是這個懸賞的發布者")
    else:
        await interaction.response.send_message(f"{release_words} 懸賞不存在")

@tree.command(name = "cancel_bounty", description = "取消懸賞", guild=discord.Object(id=1084715410768805958))
async def cancelbounty_command(interaction,title:str):
    """
    Description of the command.

    :param title: 懸賞名稱
    :type title: str
    """
    logger.info(f"{interaction.user.name} 輸入指令:/cancel_bounty 懸賞名稱:{title}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中取消懸賞。")
        return
    user_id = interaction.user.id
    with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
        task = json.load(file)
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    word = title
    if word in task:
        if task[word]["release_id"] == user_id or user_id == 525348260399939594:
            if task[word]["receiver"] is None or user_id == 525348260399939594:
                reward = int(task[word]["reward"])
                release_id = task[word]["release_id"]
                points[str(release_id)]["points"] += reward
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)
                await interaction.response.send_message(f"<@{release_id}> 成功取消懸賞:{word}，取回報酬:{reward}點社畜幣")
                del task[word]
                with open('discord/point/task.json', 'w', encoding='UTF-8') as f:
                    json.dump(task, f, indent=2)
            else:
                await interaction.response.send_message(f"{word} 懸賞已被接取，無法進行取消")
        else:
            await interaction.response.send_message(f"{interaction.user.mention} 你不是這個懸賞的發布者")
    else:
        await interaction.response.send_message(f"{word} 懸賞不存在")

@tree.command(name = "abandonment_bounty", description = "放棄懸賞", guild=discord.Object(id=1084715410768805958))
async def abandonmentbounty_command(interaction,title:str):
    """
    Description of the command.

    :param title: 懸賞名稱
    :type title: str
    """
    logger.info(f"{interaction.user.name} 輸入指令:/abandonment_bounty 懸賞名稱:{title}")
    channel_id = 1084715410768805961 # 限定的頻道 ID
    if interaction.channel_id != channel_id:
        await interaction.response.send_message(f"你只能在<#1084715410768805961>中放棄懸賞。")
        return
    user_id = interaction.user.id
    with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
        task = json.load(file)
    word = title
    if word in task:
        if task[word]["receiver_id"] == user_id or user_id == 525348260399939594:
            release_id = task[word]["release_id"]
            receiver_id = task[word]["receiver_id"]
            await interaction.response.send_message(f"<@{receiver_id}> 成功放棄懸賞:{word}。通知發布者<@{release_id}>")
            task[word]["receiver"] = None
            task[word]["receiver_id"] = None
            task[word]["task_time"] = None
            with open('discord/point/task.json', 'w', encoding='UTF-8') as f:
                json.dump(task, f, indent=2)
        else:
            await interaction.response.send_message(f"{interaction.user.mention} 你不是這個懸賞的接取者")
    else:
        await interaction.response.send_message(f"{word} 懸賞不存在")

@client.event
async def on_voice_state_update(member, before, after):
    global start_time
    global tmp
    global nothing #沒意義 取代print("")
    global voice_channel
    global target_channel_id
    global target_channel
    global low_morals
    
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    
    if before.channel is not None:
        logger.info(f"{member.name} 離開語音頻道 {before.channel.name}")
        if after.channel is not None and after.channel.id in voice_channel:
            if points[str(member.id)]["start_time"] != None:
                start_time = datetime.fromtimestamp(points[str(member.id)]['start_time'])
                current_time = datetime.now()
                elapsed_time = current_time - start_time
                #print(f"{member.name} is leave，all time：{elapsed_time}")
                #await member.send(f"{member.name}已離開語音頻道，總共在頻道內的時間為：{elapsed_time}")
                elapsed_seconds = elapsed_time.total_seconds()
                while elapsed_seconds > 0:
                    if before.channel.id == 888410932722683935 and elapsed_seconds >= 3600 and elapsed_seconds < 3660:
                        target_channel_id = 1084715410768805961
                        target_channel = await client.fetch_channel(target_channel_id)  # 獲取目標文本頻道對象
                        await target_channel.send(f"{member.mention}一番靜坐後，頓時感到心靈祥和，彷彿內心的罪惡感都消除了")
                        logger.info(f"{member.name} 道德值恢復")
                        if member.id in low_morals:
                            low_morals.remove(member.id)
                    if elapsed_seconds >= 60:
                        elapsed_seconds -= 60
                        tmp += 2
                    else:
                        elapsed_seconds = 0
                    
                points[str(member.id)]['points'] += tmp
                
                # 重置計時器
                points[str(member.id)]["start_time"] = None
                start_time = None
                tmp = 0
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)
            else:
                points[str(member.id)]["start_time"] = datetime.now().timestamp()
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)
        else:
            if points[str(member.id)]["start_time"] != None:
                start_time = datetime.fromtimestamp(points[str(member.id)]['start_time'])
                current_time = datetime.now()
                elapsed_time = current_time - start_time
                #print(f"{member.name} is leave，all time：{elapsed_time}")
                #await member.send(f"{member.name}已離開語音頻道，總共在頻道內的時間為：{elapsed_time}")
                elapsed_seconds = elapsed_time.total_seconds()
                while elapsed_seconds > 0:
                    if before.channel.id == 888410932722683935 and elapsed_seconds >= 3600 and elapsed_seconds < 3660:
                        target_channel_id = 1084715410768805961
                        target_channel = await client.fetch_channel(target_channel_id)  # 獲取目標文本頻道對象
                        await target_channel.send(f"{member.mention}一番靜坐後，頓時感到心靈祥和，彷彿內心的罪惡感都消除了")
                        logger.info(f"{member.name} 道德值恢復")
                        if member.id in low_morals:
                            low_morals.remove(member.id)
                    if elapsed_seconds >= 60:
                        elapsed_seconds -= 60
                        tmp += 2
                    else:
                        elapsed_seconds = 0
                    
                points[str(member.id)]['points'] += tmp
                
                # 重置計時器
                points[str(member.id)]["start_time"] = None
                start_time = None
                tmp = 0
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)
            else:
                nothing = None
                #print("left other voice")
                
    if after.channel is not None:
        if str(member.id) in points:
            if points[str(member.id)]["name"] != member.name:
                points[str(member.id)]["name"] = member.name
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)
                logger.info(f"{member.id} 變更使用者名稱 {member.name}")
        logger.info(f"{member.name} 進入語音頻道 {after.channel.name}")
        if after.channel is not None and after.channel.id in voice_channel:
            member_id[member.id] = member.id
            if str(member.id) not in points:
                if member_id[member.id] in member_list:
                    nothing = None #沒意義 但不想print("")
                    #print("使用者已存在於列表中")
                else:
                    if str(member.id) not in points:
                        points[member.id] = {"name": member.name, "points": 300 ,"start_time": None}
                        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                            json.dump(points, f, indent=2)
                    member_list.append(member_id[member.id])
                    logger.info(f'新增成員 {member.name} 第一次進入語音頻道')
            else:      
                if points[str(member.id)]["start_time"] != None:
                    start_time = datetime.fromtimestamp(points[str(member.id)]['start_time'])
                    current_time = datetime.now()
                    elapsed_time = current_time - start_time
                    #print(f"{member.name} is leave，all time：{elapsed_time}")
                    #await member.send(f"{member.name}已離開語音頻道，總共在頻道內的時間為：{elapsed_time}")
                    elapsed_seconds = elapsed_time.total_seconds()
                    while elapsed_seconds > 0:
                        if elapsed_seconds >= 60:
                            elapsed_seconds -= 60
                            tmp += 2
                        else:
                            elapsed_seconds = 0
                        
                    points[str(member.id)]['points'] += tmp
        
                    # 重置計時器
                    points[str(member.id)]["start_time"] = None
                    start_time = None
                    tmp = 0
                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                        json.dump(points, f, indent=2)
                else:
                    points[str(member.id)]["start_time"] = datetime.now().timestamp()
                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                        json.dump(points, f, indent=2)
        else:
            if points[str(member.id)]["start_time"] != None:
                start_time = datetime.fromtimestamp(points[str(member.id)]['start_time'])
                current_time = datetime.now()
                elapsed_time = current_time - start_time
                #print(f"{member.name} is leave，all time：{elapsed_time}")
                #await member.send(f"{member.name}已離開語音頻道，總共在頻道內的時間為：{elapsed_time}")
                elapsed_seconds = elapsed_time.total_seconds()
                while elapsed_seconds > 0:
                    if elapsed_seconds >= 60:
                        elapsed_seconds -= 60
                        tmp += 2
                    else:
                        elapsed_seconds = 0
                    
                points[str(member.id)]['points'] += tmp
                
                # 重置計時器
                points[str(member.id)]["start_time"] = None
                start_time = None
                tmp = 0
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)
            else:
                nothing = None

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!"):
        logger.info(f"{message.author.name} 輸入指令:{message.content}")
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
        
    with open('discord/point/option.json', 'r', encoding='UTF-8') as file:
        option = json.load(file)
    user_id = str(message.author.id)
    user_name = message.author.name
    
    num1 = None
    global option_list
    global question
    global user_points
    global release_word
    global release_words
    global release_reward
    global release_name
    global release_id
    global replace
    
    if message.channel.id == 1084715410768805961:
        #指令由 marshmello#1357 提供
        if message.content.startswith("aoe2de://"):
            replace = message.content
            print(replace)
            m = re.match(r"aoe2de://(?P<link_type>\d)/(?P<number>\d{9})(?P<rest>.*)", replace)
            if m:
                link_type, number, rest = m.group('link_type'), m.group('number'), m.group('rest')
                if link_type == '0':
                    res = f'(https://aoe2.net/j/{number}){rest}'
                    await message.channel.send(res)
                if link_type == '1':
                    res = f'(https://aoe2.net/s/{number}){rest}'
                    await message.channel.send(res)   
            
    if isinstance(message.channel, discord.DMChannel):       
        global selected_options
        global total_sum
        global total_sum_A
        global total_sum_B
        global update
        global bet
        global png
        with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
            points = json.load(file)
        user_points = points[user_id]['points']
            
        if (selected_options) != {}:
            if num1 is None:
                try:
                    num1 = int(message.content)
                    logger.info(f"{message.author.name} 下注:{num1}點社畜幣")
                    if num1 <= user_points and num1 > 0:
                        if bet == True:
                            user_points -= num1
                            if user_id not in option["option_A"]["betting"] and (selected_options[int(user_id)]) == "A":
                                option["option_A"]["betting"][user_id] = {"name": user_name, "betting": 0}
                            
                            if user_id not in option["option_B"]["betting"] and (selected_options[int(user_id)]) == "B":
                                option["option_B"]["betting"][user_id] = {"name": user_name, "betting": 0} 
                                                             
                            await message.channel.send(f'成功下注{num1}點，目前剩餘社畜幣 {user_points} 點')
                            points[str(user_id)]['points'] -= num1
                            with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                json.dump(points, f, indent=2)
        
                            if (selected_options[int(user_id)]) == "A":
                                option["option_A"]["total"] += num1
                                option["option_A"]["magnification"] += 0
                                if option["option_A"]["betting"][user_id]["betting"] == 0:
                                    option["option_A"]["people"] += 1
                                else:
                                    option["option_A"]["people"] += 0
                                option["option_A"]["betting"][user_id]["betting"] += num1
                                
                            elif (selected_options[int(user_id)]) == "B":
                                option["option_B"]["total"] += num1
                                option["option_B"]["magnification"] += 0
                                if option["option_B"]["betting"][user_id]["betting"] == 0:
                                    option["option_B"]["people"] += 1
                                else:
                                    option["option_B"]["people"] += 0
                                option["option_B"]["betting"][user_id]["betting"] += num1

                            if option["option_A"]["total"] != 0:
                                total_sum_A = option["option_A"]["total"]
                            if option["option_B"]["total"] != 0:
                                total_sum_B = option["option_B"]["total"]
                                
                            total_sum = total_sum_A + total_sum_B
                            
                            if option["option_A"]["total"] != 0:
                                option["option_A"]["magnification"] = round(total_sum / option["option_A"]["total"],2)
                            if option["option_B"]["total"] != 0:
                                option["option_B"]["magnification"] = round(total_sum / option["option_B"]["total"],2)
                            
                            with open('discord/point/option.json', 'w', encoding='UTF-8') as f:
                                json.dump(option, f, indent=2)
                            num1 = None
                        else:
                            await message.channel.send("加注時間已過，下次請早 :smiling_face_with_tear:")
                    elif num1 <=0 :
                        await message.channel.send("來鬧的是不是 :rage:")
                    else:
                        await message.channel.send(f'下注{num1}點失敗，沒有這麼多社畜幣:sob:，目前剩餘社畜幣 {user_points} 點')
                except ValueError:
                    num1 = None #沒有意義 不想觸發錯誤
                    logger.error(f'{message.author.name} 觸發錯誤，錯誤內容如下:\n{ValueError}')
        
@client.event
async def on_reaction_add(reaction, user):    
    if user == client.user:
        return
    
    global option_list
    global question
    global release_word
    global release_words
    global release_reward
    global release_name
    global release_id
    global bet
    
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
    
    if str(reaction.emoji) == "\U0001F1E6" and bet == True:
        if user.id not in selected_options:
            selected_options[user.id] = None
            if selected_options[user.id] != "A":
                selected_options[user.id] = "A"
                user_points = points[str(user.id)]['points']
                await user.send(f"{question}，選擇A選項 {option_list[0]}")
                await user.send(f"請輸入下注金額，目前有社畜幣{user_points}點")
                logger.info(f'{user.name} 在{question}，選擇A選項:{option_list[0]}')
        else:
            await user.send(f"你已經選擇了{selected_options[user.id]}選項，無法選擇A選項")
        
    if str(reaction.emoji) == "\U0001F171" and bet == True:
        if user.id not in selected_options:
            selected_options[user.id] = None
            if selected_options[user.id] != "B":
                selected_options[user.id] = "B"
                user_points = points[str(user.id)]['points']
                await user.send(f"{question}，選擇B選項 {option_list[1]}")
                await user.send(f"請輸入下注金額，目前有社畜幣{user_points}點")
                logger.info(f'{user.name} 在{question}，選擇B選項:{option_list[1]}')
        else:
            await user.send(f"你已經選擇了{selected_options[user.id]}選項，無法選擇B選項")
            
    if str(reaction.emoji) == "⭕" and user.id == release_id:
        embed = discord.Embed(title='發布懸賞:同意', description=f"{release_word} {release_reward}")
        embed.set_footer(text=f"請發布人:{release_name}自行按表情確認喔\n審核人:{user.name}")
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        respond = client.get_channel(1084715410768805961)
        with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
            task = json.load(file)
        task[release_word] = {"taskname": release_word,"reward": release_reward ,"release" : release_name,"release_id" : release_id,"receiver" : None,"receiver_id" : None,"task_time": None}
        with open('discord/point/task.json', 'w', encoding='UTF-8') as f:
            json.dump(task, f, indent=2)
        await respond.send(f"<@{release_id}>發布懸賞成功：{release_word} 報酬:{task[release_word]['reward']}點社畜幣")
        release_word = None
        release_reward = None
        release_name = None
        release_id = None

    if str(reaction.emoji) == "❌" and user.id == release_id:
        embed = discord.Embed(title='發布懸賞:拒絕', description=f"{release_word} {release_reward}")
        embed.set_footer(text=f"請發布人:{release_name}自行按表情確認喔\n審核人:{user.name}")
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        respond = client.get_channel(1084715410768805961)
        with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
            points = json.load(file)
        points[str(release_id)]["points"] += release_reward
        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
            json.dump(points, f, indent=2)
        await respond.send(f"<@{release_id}>發布懸賞失敗：{release_word}")
        release_word = None
        release_reward = None
        release_name = None
        release_id = None

    if str(reaction.emoji) == "🙆" and "測試" in [role.name for role in user.roles]:
        embed = discord.Embed(title='完成懸賞:成功', description=f"{release_words}")
        embed.set_footer(text=f"發布人:{release_name}\n審核人:{user.name}")
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        respond = client.get_channel(1084715410768805961)
        
        with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
            task = json.load(file)
        with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
            points = json.load(file)
        reward = int(task[release_words]["reward"])
        receiver_id = task[release_words]["receiver_id"]
        points[str(receiver_id)]["points"] += math.ceil(reward*0.8) #抽取傭金20%
        with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
            json.dump(points, f, indent=2)
        await respond.send(f"<@{receiver_id}> 恭喜完成懸賞:{release_words}，獲得報酬:{math.ceil(reward*0.8)}點社畜幣(系統抽成20%)")
        del task[release_words]
        with open('discord/point/task.json', 'w', encoding='UTF-8') as f:
            json.dump(task, f, indent=2)
            
        release_words = None
    
    if str(reaction.emoji) == "🙅" and "測試" in [role.name for role in user.roles]:
        embed = discord.Embed(title='完成懸賞:失敗', description=f"{release_words}")
        embed.set_footer(text=f"發布人:{release_name}\n審核人:{user.name}")
        await reaction.message.edit(embed=embed)
        await reaction.message.clear_reactions()
        respond = client.get_channel(1084715410768805961)
        await respond.send(f"請私訊管理員{user.mention}詢問失敗原因(洗分的就不用來問了)")
        
        release_words = None
            
# 定義清除表情的函數
async def clear_reactions(message):
    global bet
    global update
    await asyncio.sleep(301)  # 等待 5 分鐘
    await message.clear_reactions()
    channel = message.channel
    await channel.send("投注時間截止")
    logger.info('成功關閉投票和下注入口')
    bet = False
    update = False
    
async def plot_chart():
    with open('discord/point/option.json', 'r', encoding='UTF-8') as file:
        option = json.load(file)
    global png
    # 创建图像
    total_left = int(option['option_A']['total']) # 左边总额度列表
    magnification_left = float(option['option_A']['magnification']) # 左边倍率列表
    people_left = int(option['option_A']['people']) # 左边人数列表
    if (int(option['option_A']['total']) + int(option['option_B']['total'])) != 0:
        percentage_left = (int(option['option_A']['total']) / (int(option['option_A']['total']) + int(option['option_B']['total']))) * 100 # 左边总额度占比列表

    total_right = int(option['option_B']['total']) # 右边总额度列表
    magnification_right = float(option['option_B']['magnification']) # 右边倍率列表
    people_right = int(option['option_B']['people']) # 右边人数列表
    if (int(option['option_A']['total']) + int(option['option_B']['total'])) != 0:
        percentage_right = (int(option['option_B']['total']) / (int(option['option_A']['total']) + int(option['option_B']['total']))) * 100 # 右边总额度占比列表
    
    # 创建画布和两个子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 2), gridspec_kw={"width_ratios": [1, 1.5]})
    ax1.axis('off')
    ax2.axis('off')
    #fig = plt.figure(figsize=(8, 4))
    fig.suptitle(f'{question}\n選項A:{option_list[0]}，選項B:{option_list[1]}', fontsize=20, fontproperties=font)

    # 在左边的子图上绘制信息
    ax1.text(0.5, 0.3, f'總額: {total_left}\n倍率: {magnification_left}\n人數: {people_left}',
            horizontalalignment='right', verticalalignment='center', fontproperties=font1)
    ax1.text(0.9, 0.3, f'{percentage_left:.0f}%', ha='center', va='center', fontsize=24)
    ax1.set_xticks([])
    ax1.set_yticks([])

    # 在右边的子图上绘制信息
    ax2.text(0.5, 0.3, f'總額: {total_right}\n倍率: {magnification_right}\n人數: {people_right}',
            horizontalalignment='left', verticalalignment='center', fontproperties=font1)
    ax2.text(0.3, 0.3, f'{percentage_right:.0f}%', ha='center', va='center', fontsize=24)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # 调整子图之间的距离和位置
    plt.subplots_adjust(wspace=0)
    # 將圖片存到檔案中
    plt.savefig('chart.png')
    global message_id
    channel = client.get_channel(1084715410768805961)
    if png == True:
        # 上傳圖片到 Discord 頻道
        with open('chart.png', 'rb') as f:
            chart_file = discord.File(f)
        message = await channel.send(file=chart_file)
        message_id = message.id
        png = False
    else:
        # 取得消息
        message_png = await channel.fetch_message(message_id) # message_id是目標消息的ID
        await message_png.delete()
        # 修改圖片
        with open('chart.png', 'rb') as f:
            chart_file = discord.File(f)
        message = await channel.send(file=chart_file)
        message_id = message.id
        
async def chart_task():
    with open('discord/point/option.json', 'r', encoding='UTF-8') as file:
        option = json.load(file)
    while update == True:
        if update == True and (option['option_A']['total'] != 0 or option['option_B']['total'] != 0):
            logger.info('開始繪製圖片')
            await plot_chart()
            await asyncio.sleep(10)  # 每10秒刷新一次


async def send_task_table(channel):
    global examine_message_ids
    global examine_message_ids1
    global task_elapsed
    with open('discord/point/task.json', 'r', encoding='UTF-8') as file:
        task = json.load(file)
    task_list = sorted(task.items())
    num_task = math.ceil(len(task_list) / 25)
    for a in range(num_task):
        table = ""
        for b, (taskname, taskinfo) in enumerate(task_list[a * 25:(a + 1) * 25], start=a * 25 + 1):
            if b > len(task_list):
                break
            taskname = taskinfo['taskname']
            reward = taskinfo['reward']
            release = taskinfo['release']
            release_id = taskinfo['release_id']
            receiver = taskinfo['receiver']
            receiver_id = taskinfo['receiver_id']
            if taskinfo['task_time'] != None:
                task_time = datetime.fromtimestamp(taskinfo['task_time'])
                task_now = datetime.now()
                task_elapsed_time = task_now - task_time
                task_elapsed_seconds = task_elapsed_time.total_seconds()
                task_elapsed = str(timedelta(seconds=task_elapsed_seconds)).split('.')[0]
                if task_elapsed_seconds > 259200:
                    await channel.send(f"<@{receiver_id}> 懸賞過期放棄懸賞:{taskname}。通知發布者<@{release_id}>")
                    taskinfo["receiver"] = None
                    taskinfo["receiver_id"] = None
                    taskinfo["task_time"] = None
                    with open('discord/point/task.json', 'w', encoding='UTF-8') as f:
                        json.dump(task, f, indent=2)
            else:
                task_elapsed = None
            table += f"**{b}.**懸賞名稱:{taskname}\t酬勞:{reward}點社畜幣\t發布人:{release}\t接取人:{receiver}\t已使用時間:{task_elapsed}\n"
        message = await channel.send(table)
        examine_message_ids.append(message.id)
        if len(examine_message_ids1) > 0:
            for message_id in examine_message_ids1:
                message = await channel.fetch_message(message_id)
                await message.delete()
            examine_message_ids1 = []
    examine_message_ids1 += examine_message_ids
    examine_message_ids = []
    if num_task == 0 :
        return "現在沒有任何懸賞"

def shutdown_handler(signum, frame):
    logger.info('機器人快睡著囉')
    requests.get("https://points.liang0312.repl.co")
    exit(0)
    
signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

my_token = os.environ['token']
keep_alive.keep_alive()
try:
    client.run(my_token)
except:
    os.system("kill 1")