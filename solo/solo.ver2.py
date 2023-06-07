import os
import discord
#import keep_alive

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

num1 = None
num2 = None
daze = 0
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
show_player1_daze = None
show_player2_daze = None

net = None


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
    global daze
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
    global show_player1_daze
    global show_player2_daze
    global net
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
                        #main_talk = os.environ['main_talk']
                        #talk = int(main_talk)
                        channel = client.get_channel(1058806485280374825)
                        net = tmp[11:]
                        await channel.send(f'隱藏盃單挑 {playmap} (https://aoe2.net/j/{net}) -1')
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

            if (num2 >= 0):
                
                if num2 < 1100:
                    daze = 0
                else:
                    daze = (num2 - 1000) // 100 * 25
                await message.author.send(f'遊戲開始需要發呆{daze}秒後，才可以動作')
                await message.author.send('遊戲開始時請先把右下角的分數關掉，10分鐘後再打開。5分鐘前不能偷動物、圍資源或攻擊對手。')
                await message.channel.send("-----我是分隔線，期待您再次使用本系統-----")
                show_player2_daze = daze
                daze = None

                if (tmp != None):
                    #main_talk = os.environ['main_talk']
                    #talk = int(main_talk)
                    channel = client.get_channel(1058806485280374825)
                    tmp = "aoe2de://1/" + tmp[11:]
                        
                    #hidden_talk = os.environ['hidden_talk']
                    await channel.send(f'遊戲開始了(https://aoe2.net/s/{net})快到 {1058806485280374825} 一起參與討論吧!')
                    tmp = None
                else:
                    print("")

            if (num1 >= 0):
                user1 = await client.fetch_user(user1_id)
                if num1 < 1100:
                    daze = 0
                else:
                    daze = (num1 - 1000) // 100 * 25

                await user1.send(':heart:準備開始對戰:heart:')
                await user1.send(f'遊戲開始需要發呆{daze}秒後，才可以動作')
                await user1.send('遊戲開始時請先把右下角的分數關掉，10分鐘後再打開。5分鐘前不能偷動物、圍資源或攻擊對手。')
                await user1.send("-----我是分隔線，期待您再次使用本系統-----")
                show_player1_daze = daze
                daze = None
                
            else:
                await message.author.send(f'分數小於0是來鬧的吧')
            
            num1 = None
            num2 = None
            user1_id = None
            user1_name = None
            user2_name = None

    if message.content.startswith("!公布答案"):
        await message.channel.send(
        f"玩家一是{show_player1},輸入的分數是{show_player1_score},等待的時間為{show_player1_daze}秒\n玩家二是{show_player2},輸入的分數為{show_player2_score},等待的時間為{show_player2_daze}秒"
    )
        show_player1 = None
        show_player2 = None
        show_player1_score = None
        show_player2_score = None
        show_player1_daze = None
        show_player2_daze = None

my_token = os.environ['token']
#keep_alive.keep_alive()
try:
    client.run(my_token)

except:
    os.system("kill 1")