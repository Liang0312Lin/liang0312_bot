import os
import discord
import json
import asyncio
import math
#import keep_alive

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

global data

with open('discord/group.json', 'r', encoding='UTF-8') as file:
  data = json.load(file)


def reset_data():
    global user_name  #儲存使用者名字
    global user_list  #儲存8位玩家的地方
    global player_list  #根據使用者名字找分數
    global user  #儲存使用者名字和ID
    global users  #儲存使用者名字和ID
    global player  #儲存玩家
    global team_1
    global team_2
    global team_1_score
    global team_2_score
    global ranked_list
    global sum_player
    global diff
    global team_1_names_str
    global team_2_names_str
    global tmp
    global error
    global team_1_id
    global team_2_id
    global check_A
    global check_B
    
    user_name = {}
    user_list = []
    player_list = {}
    user = {}
    users = []
    player = None
    team_1 = []
    team_2 = []
    team_1_score = 0
    team_2_score = 0
    sum_player = None
    diff = None
    ranked_list = []
    team_1_names_str = None
    team_2_names_str = None
    tmp = None
    error = 0
    team_1_id = None
    team_2_id = None
    check_A = False
    check_B = False

@client.event
async def on_ready():
  print('目前登入身份：', client.user)
  game = discord.Game('Age of Empires II: Definitive Edition')
  await client.change_presence(status=discord.Status.online, activity=game)
  reset_data()


@client.event
async def on_message(message):
  await asyncio.sleep(1)
  if message.author == client.user:
    return

  if message.content == '!重啟內戰機器人':
    reset_data()
    await message.channel.send('已成功重啟機器人')

  if isinstance(message.channel, discord.DMChannel):
    global tmp
    global error
    if message.content.startswith('aoe2de://0/'):
        tmp = None
        tmp = message.content
        await message.channel.send('你想打的地圖是?請輸入地圖+空格+你想要打的圖(ex:地圖 阿拉伯)')
        # 等待使用者回應
    elif message.content.startswith('地圖'):
        playmap = message.content[3:]  # 去掉 '地圖' 前綴
        if len(tmp) == 20:
            await message.channel.send('房間已開啟')
            #main_talk = os.environ['main_talk']
            #talk = int(main_talk)
            channel = client.get_channel(1058806485280374825)
            await channel.send(f'隱藏盃團戰 {playmap} <{tmp}> -7')
        else:
            await message.channel.send("請輸入(aoe2de://0/XXXXXXXXX)就好")
            return
    else:
        error += 1
        await message.channel.send(f'輸入的不是房號喔:rage: 累積錯誤{error}次')
        if error >= 3:
            tmp = None
            error = None
            reset_data()
            await message.channel.send('錯誤已達三次，請重新開房間設定')
            return

  if message.content == '!大廳':
    embed = discord.Embed(title='大廳', description='歡迎來到大廳！')
    for i in range(8):
      embed.add_field(name=f"玩家 {i+1}", value="空位置", inline=False)

    embed.set_footer(text="按下➕：加入使用者到表格\n按下➖：從表格中移除使用者\n按下⚔️：將使用者平均分成兩隊")

    message = await message.channel.send(embed=embed)
    await message.add_reaction("➕")
    await message.add_reaction("➖")
    await message.add_reaction("⚔️")

  elif message.content == '!rank':
    with open('discord/group.json', 'r', encoding='UTF-8') as file:
      data = json.load(file)
    ranked_list = sorted(data.items(),
                         key=lambda x: x[1]["score"],
                         reverse=True)

    num_iterations = math.ceil(len(ranked_list) / 7)
    for i in range(num_iterations):
      embed = discord.Embed(title='社畜榜', description='照分數高低排序')
      embed.add_field(name='**Player**', value='\u200b', inline=True)
      embed.add_field(name='**分數**', value='\u200b', inline=True)
      embed.add_field(name='**win/ lose/ WinRate**',
                      value='\u200b',
                      inline=True)
      for j, item in enumerate(ranked_list[i * 7:(i + 1) * 7],
                               start=i * 7 + 1):
        if j > len(ranked_list):
          break
        if (item[1]['win'] + item[1]['lose']) > 0:
          win_rate = (item[1]['win'] /
                      (item[1]['win'] + item[1]['lose'])) * 100
        else:
          win_rate = (item[1]['win'] /
                      (item[1]['win'] + item[1]['lose'] + 1)) * 100
        embed.add_field(name=f'**No.{j}** {item[0]}',
                        value='\u200b',
                        inline=True)
        embed.add_field(name=f'{item[1]["score"]}',
                        value='\u200b',
                        inline=True)
        embed.add_field(
          name=f'{item[1]["win"]} / {item[1]["lose"]} / {win_rate:.2f}%',
          value='\u200b',
          inline=True)
      message = await message.channel.send(embed=embed)


@client.event
async def on_reaction_add(reaction, user):
  global check_A
  global check_B
  if user == client.user:
    return
  if str(reaction.emoji) == "➕":

    with open('discord/group.json', 'r', encoding='UTF-8') as file:
      data = json.load(file)

    user_name[user.name] = user.name

    if user_name[user.name] in user_list:
      print("使用者已存在於列表中")
    else:
      if user.name not in data:
        data[user.name] = {"uid": user.id, "score": 1000, "win": 0, "lose": 0}
        with open('discord/group.json', 'w', encoding='UTF-8') as f:
            json.dump(data, f, indent=2)

      user_list.append(user_name[user.name])
      player_list[f'{user.name}'] = data[f'{user.name}']

    user = {f'{user.name}:{user.id}'}
    if user in users:
      print("使用者已存在於列表中")
    else:
      users.append(user)

    embed = discord.Embed(title='大廳', description='歡迎來到大廳！')
    for i in range(8):
      if i < len(user_list):
        embed.add_field(name=f"玩家 {i+1}", value=user_list[i], inline=False)
      else:
        value = "空位置"
        embed.add_field(name=f"玩家 {i+1}", value=value, inline=False)

    embed.set_footer(text="按下➕：加入使用者到表格\n按下➖：從表格中移除使用者\n按下⚔️：將使用者平均分成兩隊")

    await reaction.message.edit(embed=embed)

  elif str(reaction.emoji) == "➖":
    if user.name in user_name:
      if user_name[user.name] in user_list:
        user_list.remove(user_name[user.name])
        player_list.pop(f'{user.name}')

        user_to_remove = {f'{user.name}:{user.id}'}
        users.remove(user_to_remove)
      else:
        print("使用者不在於列表中")

      del user_name[user.name]

    embed = discord.Embed(title='大廳', description='歡迎來到大廳！')
    for i in range(8):
      if i < len(user_list):
        embed.add_field(name=f"玩家 {i+1}", value=user_list[i], inline=False)
      else:
        value = "空位置"
        embed.add_field(name=f"玩家 {i+1}", value=value, inline=False)

    embed.set_footer(text="按下➕：加入使用者到表格\n按下➖：從表格中移除使用者\n按下⚔️：將使用者平均分成兩隊")

    await reaction.message.edit(embed=embed)

  elif str(reaction.emoji) == "⚔️":
    if len(user_list) < 2:
      await reaction.message.channel.send("人數不足兩人，無法分隊！")
      return

    embed = discord.Embed(title='大廳', description='歡迎來到大廳！')
    for i in range(8):
      if i < len(user_list):
        embed.add_field(name=f"玩家 {i+1}", value=user_list[i], inline=False)
      else:
        value = "空位置"
        embed.add_field(name=f"玩家 {i+1}", value=value, inline=False)

    embed.set_footer(
      text=f"按下➕：加入使用者到表格\n按下➖：從表格中移除使用者\n按下⚔️：將使用者平均分成兩隊\n{user.name}開啟對戰")

    await reaction.message.edit(embed=embed)
    await reaction.message.clear_reactions()

    team_1 = {}
    team_2 = {}

    team_1_score = 0
    team_2_score = 0

    sorted_players = sorted(player_list.items(),
                            key=lambda x: x[1]['score'],
                            reverse=True)

    for player, score in sorted_players:
      if abs(team_1_score + score['score'] - team_2_score) < abs(team_1_score -
                                                                 team_2_score):
        team_1[player] = score
        team_1_score += score['score']
      else:
        team_2[player] = score
        team_2_score += score['score']

    with open('discord/group.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)

    for member in team_1:
        team_1_id = f"{data[member]['uid']}\n"
        team1 = await client.fetch_user(team_1_id)
        await team1.send('你是隊伍一')
    for member in team_2:
        team_2_id = f"{data[member]['uid']}\n"
        team2 = await client.fetch_user(team_2_id)
        await team2.send('你是隊伍二')
	
    percentage_1 = (1 / (1 + 10**((team_2_score - team_1_score) / 400))) * 100
    formatted_percentage_1 = "{:.2f}%".format(percentage_1)
    percentage_2 = (1 / (1 + 10**((team_1_score - team_2_score) / 400))) * 100
    formatted_percentage_2 = "{:.2f}%".format(percentage_2)

    embed = discord.Embed(
      title='分隊結果',
      description=
      f'分隊完成！\n隊伍一勝率為 {formatted_percentage_1}\n隊伍二勝率為 {formatted_percentage_2}'
    )
    embed.add_field(name='隊伍 1', value='社畜\n社畜\n社畜\n社畜', inline=False)
    embed.add_field(name='隊伍 2', value='社畜\n社畜\n社畜\n社畜', inline=False)
    embed.set_footer(text=f"按下🅰：表示隊伍一獲勝\n按下🅱：表示隊伍二獲勝\n再按下✅表示確認隊伍獲勝\n我很脆弱，不要手殘按錯，我不會修QQ")
    message = await reaction.message.channel.send(embed=embed)
    await message.add_reaction("🅰")
    await message.add_reaction("🅱")
    await message.add_reaction("✅")
    
  if str(reaction.emoji) == "🅰":
    check_A = True
  if str(reaction.emoji) == "🅱":
    check_B = True
  if str(reaction.emoji) == "✅" and check_A == True:
    with open('discord/group.json', 'r', encoding='UTF-8') as file:
      data = json.load(file)

    team_1 = {}
    team_2 = {}
    team_1_score = 0
    team_2_score = 0
    sorted_players = sorted(player_list.items(),
                            key=lambda x: x[1]['score'],
                            reverse=True)

    for player, score in sorted_players:
      if abs(team_1_score + score['score'] - team_2_score) < abs(team_1_score -
                                                                 team_2_score):
        team_1[player] = score
        team_1_score += score['score']
      else:
        team_2[player] = score
        team_2_score += score['score']

    new_score = 32 * (1 - (1 /
                           (1 + 10**((team_2_score - team_1_score) / 400))))
    score = int(new_score)
    for team in team_1:
      data[team]["score"] += score
      data[team]["win"] += 1
    for team2 in team_2:
      data[team2]["score"] -= score
      data[team2]["lose"] += 1
    with open('discord/group.json', 'w', encoding='UTF-8') as f:
      json.dump(data, f, indent=2)

    embed = discord.Embed(title='成績結算', description='隊伍一獲勝！')
    team_1_string = ""
    for member in team_1:
      team_1_string += f"{member}: {data[member]['score']} (+{score})\n"
    embed.add_field(name='隊伍 1', value=team_1_string, inline=False)

    team_2_string = ""
    for member in team_2:
      team_2_string += f"{member}: {data[member]['score']} (-{score})\n"
    embed.add_field(name='隊伍 2', value=team_2_string, inline=False)

    embed.set_footer(text=f"{user.name}上傳結果")
    await reaction.message.edit(embed=embed)
    await reaction.message.clear_reactions()
    reset_data()

  elif str(reaction.emoji) == "✅" and check_B == True:
    with open('discord/group.json', 'r', encoding='UTF-8') as file:
      data = json.load(file)
    team_1 = {}
    team_2 = {}
    team_1_score = 0
    team_2_score = 0
    sorted_players = sorted(player_list.items(),
                            key=lambda x: x[1]['score'],
                            reverse=True)

    for player, score in sorted_players:
      if abs(team_1_score + score['score'] - team_2_score) < abs(team_1_score -
                                                                 team_2_score):
        team_1[player] = score
        team_1_score += score['score']
      else:
        team_2[player] = score
        team_2_score += score['score']

    new_score = 32 * (1 - (1 /
                           (1 + 10**((team_1_score - team_2_score) / 400))))
    score = int(new_score)
    for team in team_1:
      data[team]["score"] -= score
      data[team]["lose"] += 1
    for team2 in team_2:
      data[team2]["score"] += score
      data[team2]["win"] += 1
    with open('discord/group.json', 'w', encoding='UTF-8') as f:
      json.dump(data, f, indent=2)

    embed = discord.Embed(title='成績結算', description='隊伍二獲勝！')

    team_1_string = ""
    for member in team_1:
      team_1_string += f"{member}: {data[member]['score']} (-{score})\n"
    embed.add_field(name='隊伍 1', value=team_1_string, inline=False)

    team_2_string = ""
    for member in team_2:
      team_2_string += f"{member}: {data[member]['score']} (+{score})\n"
    embed.add_field(name='隊伍 2', value=team_2_string, inline=False)

    embed.set_footer(text=f"{user.name}上傳結果")
    await reaction.message.edit(embed=embed)
    await reaction.message.clear_reactions()
    reset_data()


my_token = os.environ['token']
#keep_alive.keep_alive()
try:
  client.run(my_token)
except:
  os.system("kill 1")
