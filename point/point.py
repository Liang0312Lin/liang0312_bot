import asyncio
import json
import math
import os
import random
import signal
import discord
import logging
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import requests
import re

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

global points
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

with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
    points = json.load(file)

@client.event
async def on_ready():
    print('目前登入身份：', client.user)
    game = discord.Game('Age of Empires II: Definitive Edition')
    await client.change_presence(status=discord.Status.online, activity=game)
    client.loop.create_task(chart_task())
    logger.info(f'{client.user} 開始運作' )
    while True:
        await send_latest_log()
        await asyncio.sleep(60)  # 每隔 60 秒执行一次

# 記錄每個用戶的點數
points = {}
member_id = {}
member_list = []
start_time = 0
tmp = 0
total_sum = 0
total_sum_A = 0
total_sum_B = 0
total_sum_C = 0
total_sum_D = 0
ranked_list = []
rank = []
selected_options={}
update = False
bet = False
voice_channel = [1084715410768805962,1084757284879609926]
png = True
i = 0
option_list = []
question = None
target_channel_id = None
target_channel = None
low_morals=[]
newvote = None
#bonuspool = 0
#reward = 0
examine_message_ids = []
examine_message_ids1 = []
task_elapsed = None

replace = None
replace_text = None
text = None

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
    emoji_numbers = ["\U0001F1E6", "\U0001F171","\U0001F1E8", "\U0001F1E9"]
    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
        points = json.load(file)
        
    with open('discord/point/option.json', 'r', encoding='UTF-8') as file:
        option = json.load(file)
    user_id = str(message.author.id)
    user_name = message.author.name
    
    num1 = None
    global option_list
    global question
    global myrank
    global user_points
    global low_morals
    global newvote
    global release_word
    global release_words
    global release_reward
    global release_name
    global release_id
    global replace
    global replace_text
    global text
    
    if message.channel.id == 1084715410768805961:
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
    
    if message.channel.id == 1084715410768805961:
        global voice_channel
        global start_time
        global tmp
        member = message.author
        if message.content.startswith("!查詢"):
            if points[str(member.id)]["start_time"] != None:
                start_time = datetime.fromtimestamp(points[str(member.id)]['start_time'])
                #print("start_time:",start_time)
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
                guild_id = 1084715410768805958  # 輸入伺服器 ID
                guild = client.get_guild(guild_id)
                member = guild.get_member(message.author.id)
                if member.voice.channel.id in voice_channel:
                    points[str(member.id)]["start_time"] = datetime.now().timestamp()
                else:
                    points[str(member.id)]["start_time"] = None
                tmp = 0
                with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                    json.dump(points, f, indent=2)

            with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                points = json.load(file)
            user_points = points[user_id]['points']    
            await message.channel.send(f'{member.mention}現在有社畜幣 {user_points} 點')
        
        if message.content.startswith('!偷'):
            try:
                with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                    points = json.load(file)
                words = message.content.split()

                members = message.mentions[0]
                amount = int(words[-1])
                
                members_id = members.id
                if str(members_id) in points:
                    if amount > 0:
                        if points[str(message.author.id)]["points"] >= amount and points[str(members_id)]["points"] >= amount:
                            random_number = random.randint(0, 100)
                            if message.author.id in low_morals:
                                if random_number == 100:
                                    points[str(message.author.id)]["points"] += math.ceil(amount*1.5)
                                    points[str(members_id)]["points"] -= amount
                                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                        json.dump(points, f, indent=2)
                                    await message.channel.send(f"{message.author.mention} 運氣爆棚，達成{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣，並且獲得額外獎勵{math.ceil(amount*0.5)}點社畜幣！(由於道德低下，只有獲得一半的獎勵)\n{message.author.mention} 道德值沒有下降")
                                elif random_number >= 95:
                                    points[str(message.author.id)]["points"] += amount
                                    points[str(members_id)]["points"] -= amount
                                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                        json.dump(points, f, indent=2)
                                    await message.channel.send(f"{message.author.mention} 靠著{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣！\n{message.author.mention} 道德值下降(需在 <#888410932722683935> 反省一小時來消除心中的罪惡感)")
                                    logger.info(f"{message.author.name} 道德值下降")
                                else:
                                    points[str(message.author.id)]["points"] -= amount
                                    points["1084715001593475082"]["points"] += math.floor(amount*0.6)
                                    points[str(members_id)]["points"] += math.ceil(amount*0.4)
                                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                        json.dump(points, f, indent=2)
                                    await message.channel.send(f"{message.author.mention} 此次偷竊的成功率為 {random_number}%，但可惜功虧一簣，損失了 {amount} 點社畜幣！(由於你是個道德低下的人，成功機率須達95%以上，才可偷竊成功)\n{members.mention} 成功守住自己的財務，獲得了 {math.ceil(amount*0.4)} 點社畜幣！")
                            else:
                                if random_number == 100:
                                    points[str(message.author.id)]["points"] += amount*2
                                    points[str(members_id)]["points"] -= amount
                                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                        json.dump(points, f, indent=2)
                                    await message.channel.send(f"{message.author.mention} 運氣爆棚，達成{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣，並且獲得額外獎勵{amount}點社畜幣！\n{message.author.mention} 道德值沒有下降")
                                elif random_number >= 85:
                                    points[str(message.author.id)]["points"] += amount
                                    points[str(members_id)]["points"] -= amount
                                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                        json.dump(points, f, indent=2)
                                    await message.channel.send(f"{message.author.mention} 靠著{random_number}%成功機率，偷走了 {members.mention} {amount} 點社畜幣！\n{message.author.mention} 道德值下降(需在 <#888410932722683935> 反省一小時來消除心中的罪惡感)")
                                    logger.info(f"{message.author.name} 道德值下降")
                                    low_morals.append(message.author.id)
                                else:
                                    points[str(message.author.id)]["points"] -= amount
                                    points["1084715001593475082"]["points"] += math.floor(amount*0.6)
                                    points[str(members_id)]["points"] += math.ceil(amount*0.4)
                                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                                        json.dump(points, f, indent=2)
                                    await message.channel.send(f"{message.author.mention} 此次偷竊的成功率為 {random_number}%，但可惜功虧一簣，損失了 {amount} 點社畜幣！(成功機率須達85%以上，才可偷竊成功)\n{members.mention} 成功守住自己的財務，獲得了 {math.ceil(amount*0.4)} 點社畜幣！")
                        else:
                            await message.channel.send(f"{message.author.mention} 或是 {members.mention} 沒這麼多社畜幣\n但我不告訴你他有多少社畜幣，偷竊此風不可長啊")
                    else:
                        await message.channel.send(f"{message.author.mention} 不能偷0或負數 :rage: ")
                else:
                    await message.channel.send(f"機器人翻遍了資料庫，但還是找不到 {members.mention} 的資料")
            except:
                await message.channel.send("輸入指令錯誤，範例: !偷 @liang0312#9415 312")
                
        if message.content.startswith('!道德值'):
            await message.channel.send(f"道德值是一種很玄奧的道理，請施主{message.author.mention}靜下心來仔細感受。\ntip:江湖相傳在讓我靜靜<#888410932722683935>坐坐後，會心靈祥和\n(要在裡面待一小時以上，然後離開語音頻道才會觸發，期間不可使用查詢等功能)")
            
        if message.content.startswith('!我的排名'):
            with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                points = json.load(file)
            ranked_list1 = sorted(points.items(),key=lambda x: x[1]["points"],reverse=True)
            num_iterations = math.ceil(len(ranked_list1) / 50)
            my_rank = None
            for j in range(num_iterations):
                for myrank, (user_id, points) in enumerate(ranked_list1[j * 50:(j + 1) * 50],start=j * 50 + 1):
                    if myrank > len(ranked_list1):
                        break
                    # 新增變數以紀錄自己的排名
                    if user_id == str(message.author.id):
                        my_rank = myrank
            if my_rank:
                await message.channel.send(f"{message.author.mention}目前的社畜幣排名是第{my_rank}名！")
            else:
                await message.channel.send(f"很抱歉，{message.author.mention}目前沒有排名。")
                
        if message.content.startswith('!指令'):
            embed = discord.Embed(title='目前可用指令', description="!查詢\n!偷 @人 點數\n!道德值\n!我的排名")          
            message = await message.channel.send(embed=embed)
            
        if message.content.startswith('!管理員指令'):
            embed = discord.Embed(title='目前可用指令', description="!創建投票 標題 A B\n!選擇結果 A\n!排行\n!刷新\n!停止刷新")          
            message = await message.channel.send(embed=embed)
            
        if message.content.startswith('!道德低下'):
            await message.channel.send(f"{low_morals}")
            
                
            
    if isinstance(message.channel, discord.DMChannel):       
        global selected_options
        global total_sum
        global total_sum_A
        global total_sum_B
        global total_sum_C
        global total_sum_D
        global ranked_list
        global rank
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
                                
                            if user_id not in option["option_C"]["betting"] and (selected_options[int(user_id)]) == "C":
                                option["option_C"]["betting"][user_id] = {"name": user_name, "betting": 0}    
                            
                            if user_id not in option["option_D"]["betting"] and (selected_options[int(user_id)]) == "D":
                                option["option_D"]["betting"][user_id] = {"name": user_name, "betting": 0}                        
                            
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

                            elif (selected_options[int(user_id)]) == "C":
                                option["option_C"]["total"] += num1
                                option["option_C"]["magnification"] += 0
                                if option["option_C"]["betting"][user_id]["betting"] == 0:
                                    option["option_C"]["people"] += 1
                                else:
                                    option["option_C"]["people"] += 0
                                option["option_C"]["betting"][user_id]["betting"] += num1

                            elif (selected_options[int(user_id)]) == "D":
                                option["option_D"]["total"] += num1
                                option["option_D"]["magnification"] += 0
                                if option["option_D"]["betting"][user_id]["betting"] == 0:
                                    option["option_D"]["people"] += 1
                                else:
                                    option["option_D"]["people"] += 0
                                option["option_D"]["betting"][user_id]["betting"] += num1

                            if option["option_A"]["total"] != 0:
                                total_sum_A = option["option_A"]["total"]
                            if option["option_B"]["total"] != 0:
                                total_sum_B = option["option_B"]["total"]
                            if option["option_C"]["total"] != 0:
                                total_sum_C = option["option_C"]["total"]
                            if option["option_D"]["total"] != 0:
                                total_sum_D = option["option_D"]["total"] 
                            total_sum = total_sum_A + total_sum_B + total_sum_C + total_sum_D
                            
                            if option["option_A"]["total"] != 0:
                                option["option_A"]["magnification"] = round(total_sum / option["option_A"]["total"],2)
                            if option["option_B"]["total"] != 0:
                                option["option_B"]["magnification"] = round(total_sum / option["option_B"]["total"],2)
                            if option["option_C"]["total"] != 0:
                                option["option_C"]["magnification"] = round(total_sum / option["option_C"]["total"],2)
                            if option["option_D"]["total"] != 0:
                                option["option_D"]["magnification"] = round(total_sum / option["option_D"]["total"],2)
                            
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
         
    elif "測試" in [role.name for role in message.author.roles]:
        if message.content.startswith('!創建投票'):
            # 創建投票
            bet = True
            newvote = message.content[6:]
            option_list = newvote.split(" ")
            question = option_list.pop(0)
            options = {}
            for i, option in enumerate(option_list):
                options[emoji_numbers[i]] = {"name": option.strip()}

            embed = discord.Embed(title=question, description="選項", color=0x00ff00)
            for option in options:
                embed.add_field(name=option, value=options[option]["name"], inline=False)

            msg = await message.channel.send(embed=embed)

            for option in options:
                await msg.add_reaction(option)
            await message.channel.send("5分鐘後下注截止，請有意下注者動作迅速，感謝配合")
            await chart_task()
            asyncio.ensure_future(clear_reactions(msg))
            
        
        if message.content.startswith('!選擇結果'):
            ans = message.content[6:]
            if ans == "A":
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
                await message.channel.send(f"恭喜選項A {option_list[0]} 獲勝")
            elif ans == "B":
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
                await message.channel.send(f"恭喜選項B {option_list[1]} 獲勝")
            elif ans == "C":
                for user_id, info in option["option_C"]["betting"].items():
                    betting = info["betting"]
                    magnification = option["option_C"]["magnification"]
                    points[str(user_id)]['points'] += int(betting * magnification)
                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                        json.dump(points, f, indent=2)
                    user = await client.fetch_user(user_id)
                    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                        points = json.load(file)
                    user_points = points[user_id]['points']
                    await user.send(f'恭喜你獲得{int(betting * magnification)}點，目前社畜幣為{user_points}')
                    logger.info(f'{user.name} 在{question}，選擇C選項:{option_list[2]}，成功獲得{int(betting * magnification)}點社畜幣')
                await message.channel.send(f"恭喜選項C {option_list[2]} 獲勝")
            elif ans == "D":
                for user_id, info in option["option_D"]["betting"].items():
                    betting = info["betting"]
                    magnification = option["option_D"]["magnification"]
                    points[str(user_id)]['points'] += int(betting * magnification)
                    with open('discord/point/point.json', 'w', encoding='UTF-8') as f:
                        json.dump(points, f, indent=2)
                    user = await client.fetch_user(user_id)
                    with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                        points = json.load(file)
                    user_points = points[user_id]['points']
                    await user.send(f'恭喜你獲得{int(betting * magnification)}點，目前社畜幣為{user_points}')
                    logger.info(f'{user.name} 在{question}，選擇D選項:{option_list[3]}，成功獲得{int(betting * magnification)}點社畜幣')
                await message.channel.send(f"恭喜選項D {option_list[3]} 獲勝")
            selected_options={}
            option["option_A"]["total"] = 0
            option["option_A"]["magnification"] = 0.0
            option["option_A"]["people"] = 0
            option["option_A"]["betting"] ={}
            
            option["option_B"]["total"] = 0
            option["option_B"]["magnification"] = 0.0
            option["option_B"]["people"] = 0
            option["option_B"]["betting"] ={}
            
            option["option_C"]["total"] = 0
            option["option_C"]["magnification"] = 0.0
            option["option_C"]["people"] = 0
            option["option_C"]["betting"] ={}
            
            option["option_D"]["total"] = 0
            option["option_D"]["magnification"] = 0.0
            option["option_D"]["people"] = 0
            option["option_D"]["betting"] ={}
            with open('discord/point/option.json', 'w', encoding='UTF-8') as f:
                json.dump(option, f, indent=2)
            update = False
            bet = False
            png = True
            option_list = []
            question = None
            
                
        if message.content.startswith('!排行'):
            with open('discord/point/point.json', 'r', encoding='UTF-8') as file:
                points = json.load(file)
            ranked_list = sorted(points.items(),key=lambda x: x[1]["points"],reverse=True)
            num_iterations = math.ceil(len(ranked_list) / 50)
            for j in range(num_iterations):
                table = "排名\t\t名稱\t\t社畜幣\n"
                for i, (user_id, points) in enumerate(ranked_list[j * 50:(j + 1) * 50],start=j * 50 + 1):
                    if i > len(ranked_list):
                        break
                    name = points['name']
                    points = points['points']
                    table += f"**No.{i}**\t\t{name}\t\t*{points}*\n"

                await message.channel.send(f"社畜幣排行榜：\n{table}")
            
        if message.content.startswith('!刷新'):
            update = True
            png = True
            await chart_task()
            
        if message.content.startswith('!停止刷新'):
            update = False
            await message.channel.send("已停止刷新")

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
        
    if str(reaction.emoji) == "\U0001F1E8":
        if user.id not in selected_options:
            selected_options[user.id] = None
            if selected_options[user.id] != "C":
                selected_options[user.id] = "C"
                user_points = points[str(user.id)]['points']
                await user.send(f"{question}，選擇C選項 {option_list[2]}")
                await user.send(f"請輸入下注金額，目前有社畜幣{user_points}點")
                logger.info(f'{user.name} 在{question}，選擇C選項:{option_list[2]}')
        else:
            await user.send(f"你已經選擇了{selected_options[user.id]}選項，無法選擇C選項")
                
    if str(reaction.emoji) == "\U0001F1E9":
        if user.id not in selected_options:
            selected_options[user.id] = None
            if selected_options[user.id] != "D":
                selected_options[user.id] = "D"
                user_points = points[str(user.id)]['points']
                await user.send(f"{question}，選擇D選項 {option_list[3]}")
                await user.send(f"請輸入下注金額，目前有社畜幣{user_points}點")
                logger.info(f'{user.name} 在{question}，選擇D選項:{option_list[3]}')
        else:
            await user.send(f"你已經選擇了{selected_options[user.id]}選項，無法選擇D選項")

            
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
        await asyncio.sleep(10)  # 每10秒刷新一次
        if update == True and (option['option_A']['total'] != 0 or option['option_B']['total'] != 0):
            logger.info('開始繪製圖片')
            await plot_chart()
            
async def send_latest_log():
    with open("discord/point/discord.log", "r", encoding='UTF-8') as f:
        log_lines = f.readlines()
        last_pos = int(os.environ.get("DISCORD_LOG_LAST_POSITION", "0"))
        new_lines = log_lines[last_pos:]
        if new_lines:
            channel = client.get_channel(1096251875352920086)
            for line in new_lines:
                await channel.send(line.strip())
            os.environ["DISCORD_LOG_LAST_POSITION"] = str(len(log_lines))


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