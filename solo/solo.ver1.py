import os
import discord
import random
#import keep_alive

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

num1 = None
num2 = None
num3 = None
num_options = None
options_list = None
user1_id = None
tmp = None
playmap = None
error = 0

user1_name = None
user2_name = None
show_player1 = None
show_player2 = None
show_player1_score = 0
show_player2_score = 0
show_player1_options = None
show_player2_options = None


@client.event
async def on_ready():
  print('目前登入身份：', client.user)
  game = discord.Game('Age of Empires II: Definitive Edition')
  await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message(message):
  global num_options
  global num1
  global num2
  global num3
  global options_list
  global user1_id
  global tmp
  global playmap
  global error
  global user1_name
  global user2_name
  global show_player1
  global show_player2
  global show_player1_score
  global show_player2_score
  global show_player1_options
  global show_player2_options
  if message.author == client.user:
    return

  if isinstance(message.channel, discord.DMChannel):
    if num1 is None:
      try:
        num1 = int(message.content)
        await message.channel.send('請等待第二位玩家輸入分數喔')
        user1_id = message.author.id
        user1_name = message.author.name
        show_player1_score = num1
        show_player1 = user1_name
      except ValueError:
        if message.content.startswith('aoe2de://0/'):
          tmp = message.content
          await message.channel.send('你想打的地圖是?請輸入地圖+空格+你想要打的圖(ex:地圖 阿拉伯)')
          # 等待使用者回應
        elif message.content.startswith('地圖'):
          playmap = message.content[3:]  # 去掉 '地圖' 前綴

          if len(tmp) == 20:
            await message.channel.send('房間已開啟，請輸入您的分數')
            main_talk = os.environ['main_talk']
            talk = int(main_talk)
            channel = client.get_channel(talk)
            await channel.send(f'隱藏盃單挑 {playmap} <{tmp}> -1')
          else:
            await message.channel.send("請輸入(aoe2de://0/XXXXXXXXX)就好")
            return
        else:
          error += 1
          await message.channel.send(f'輸入的不是數字喔:rage: 累積錯誤{error}次')
          if error >= 3:
            tmp = None
            num1 = None
            error = None
            await message.channel.send('錯誤已達三次，請重新開房間設定')
          return
    else:
      try:
        num2 = int(message.content)
        await message.channel.send(':heart:準備開始對戰:heart:')
        user2_name = message.author.name
        show_player2_score = num2
        show_player2 = user2_name
      except ValueError:
        error += 1
        await message.channel.send(f'輸入的不是數字喔:rage: 累積錯誤{error}次')
        if error >= 3:
          tmp = None
          num1 = None
          error = None
          await message.channel.send('錯誤已達三次，請重新開房間設定')
        return

      num3 = random.randint(min(num1, num2) - 300, min(num1, num2))

      if (num2 >= num3):
        diff = abs(num2 - num3)
        if diff >= 100 and diff < 200:
          num_options = 5
        elif diff >= 200 and diff < 300:
          num_options = 4
        elif diff >= 300 and diff < 400:
          num_options = 3
        elif diff >= 400 and diff < 600:
          num_options = 2
        elif diff >= 600:
          num_options = 1
        else:
          num_options = 6
        await message.author.send(f'可以使用軍事建築物的種類：{num_options}')
        if num_options is None:
          return

        else:
          options = "軍營,馬廄,射箭場,修道院,攻城器,城堡"
          options_list = options.split(',')
          selected_options = random.sample(options_list, num_options)
          selected_options_str = '、'.join(selected_options)
          response_message = f'抽到的種類是：{selected_options_str}'
          await message.channel.send(response_message)
          await message.channel.send("-----我是分隔線，期待您再次使用本系統-----")
          show_player2_options = selected_options_str
          num_options = None

          if (tmp != None):
            main_talk = os.environ['main_talk']
            talk = int(main_talk)
            channel = client.get_channel(talk)
            tmp = "aoe2de://1/" + tmp[11:]
            
            hidden_talk = os.environ['hidden_talk']
            await channel.send(
              f'遊戲開始了<{tmp}>快到 {hidden_talk} 一起參與討論吧!')
            tmp = None
          else:
            print("")

      if (num1 >= num3):
        user1 = await client.fetch_user(user1_id)
        diff = abs(num1 - num3)
        if diff >= 100 and diff < 200:
          num_options = 5
        elif diff >= 200 and diff < 300:
          num_options = 4
        elif diff >= 300 and diff < 400:
          num_options = 3
        elif diff >= 400 and diff < 600:
          num_options = 2
        elif diff >= 600:
          num_options = 1
        else:
          num_options = 6

        await user1.send(':heart:準備開始對戰:heart:')
        await user1.send(f'可以使用軍事建築物的種類：{num_options}')

        if num_options is None:
          return
        else:
          options = "軍營,馬廄,射箭場,修道院,攻城器,城堡"
          options_list = options.split(',')
          selected_options = random.sample(options_list, num_options)
          selected_options_str = '、'.join(selected_options)
          response_message = f'抽到的種類是：{selected_options_str}'
          await user1.send(response_message)
          await user1.send("-----我是分隔線，期待您再次使用本系統-----")
          show_player1_options = selected_options_str
          num_options = None

      num1 = None
      num2 = None
      num3 = None
      user1_id = None
      user1_name = None
      user2_name = None

  if message.content.startswith("!公布答案"):
    await message.channel.send(
      f"玩家一是{show_player1},輸入的分數是{show_player1_score},抽到的選項為{show_player1_options}\n玩家二是{show_player2},輸入的分數為{show_player2_score},抽到的選項為{show_player2_options}"
    )
    show_player1 = None
    show_player2 = None
    show_player1_score = None
    show_player2_score = None
    show_player1_options = None
    show_player2_options = None

my_token = os.environ['token']
#keep_alive.keep_alive()
try:
    client.run(my_token)

except:
    os.system("kill 1")