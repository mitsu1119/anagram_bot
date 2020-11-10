import sys
import discord
import string
import random
import time
import redis
import os

TOKEN = os.environ["DISCORD_BOT_TOKEN"]
point_name = os.environ["POINT_NAME"]

client = discord.Client()

# {user: {point: p}}
conn = redis.from_url(url=os.environ["REDIS_URL"], decode_responses=True)

# ------------------------ utils -----------------------------------------
# primirity test
def MR(n):
    if n == 2:
        return True
    if n == 1:
        return False
    if n & 1 == 0:
        return False

    d = (n - 1) >> 1
    while d & 1 == 0:
        d //= 2

    for i in range(100):
        a = random.randint(1, n - 1)
        x = pow(a, d, n)
        t = d

        while t != n - 1 and x != 1 and x != n - 1:
            x = pow(x, 2, n)
            t *= 2
        if x != n - 1 and x & 1 == 0:
            return False
    return True

# random shuffle
def sh(st):
    res = list(st)
    random.shuffle(res)
    return "".join(res)

# palindrome test
def is_palindrome(string):
    return string.find(string[::-1])

# playing gacha 
def play_gacha():
    exrate = [40, 30, 22, 5, 3]
    p = random.randint(1, 100)
    s = 0
    for rarity in range(len(exrate)):
        s += exrate[rarity]
        if p <= s:
            break
    types = ["火", "水", "風", "土", "闇", "光"]
    t = types[random.randint(0, len(types) - 1)]
    return rarity + 1, t

# give user point
async def give_point(user, point):
    if conn.exists(user.name) != 0:
        dic = conn.hgetall(user.name)
        conn.hset(user.name, "point", int(dic["point"]) + point)

# ------------------------------ functions -------------------------------------
@client.event
async def on_ready():
    print("login success")

async def how_to(message):
    reply = f"""
    {message.author.mention}
    【使い方】
    ・!signup: 一部の機能を利用するためのユーザ登録ができます。
    ・!gacha: ガチャが引けます。
    ・/[str]: strのアナグラムを生成します。空白区切りで複数のアナグラムを作成できます。
    ・[palindrome]: 回文であることを指摘してくれます。
    ・{{prime_number}}: 素数であることを指摘してくれます。

    【コマンドの見方】
    ・!から始まる機能は、!hoge help とすればその機能の詳細な使い方を表示することができます。
    ・[]でくくられた変数に関するコマンドは、その前後にある文章の条件に合致したときのみbotが動きます。
    ・{{}}でくくられた変数に関するコマンドは、メッセージ中のどこにあってもトラップしてbotが動きます。
    """
    await message.channel.send(reply)

async def signup(args, user, channel):
    if len(args) == 1:
        if conn.exists(user.name) != 0:
            reply = f"{user.mention} 登録済みです。"
        else :
            dic = {"point": 0}
            conn.hset(user.name, "point", 0)
            reply = f"{user.mention} 登録できました。"
        await channel.send(reply)
        return

    if args[1] == "list":
        reply = f"{user.mention}"
        for name in conn.keys():
            reply += f"\n・{name}"
        await channel.send(reply)
        return

    if args[1] == "help":
        reply = f"""{user.mention}
!signup [OPTION]
  botへのユーザ登録をしてくれます。ガチャ機能など、ユーザ登録をしないと利用できない機能があります。

  [OPTION]
 help:  ヘルプを表示します。
 list:  登録済みのユーザを表示します。
 """
        await channel.send(reply)
        return

# args: args[0] = "!gacha", args[1..] = options
async def gacha(args, message):
    user = message.author

    if len(args) > 1 and args[1] == "help":
        reply = f"""{message.author.mention}
!gacha [OPTION]
  3{point_name}で単発ガチャを引かせてくれます。まとめて10回分引けば11連できます。出てくるキャラの属性は火、水、風、土、闇、光のいずれかで確率は一様です。また、ポイントについてはメッセージをどこかに投稿する毎に1{point_name}手に入れることができます。

  [OPTION]
 help:   ヘルプを表示します
 info:   自身の{point_name}を確認します。
 10:     30{point_name}11連ガチャが引けます。

 【排出率】
 ☆:      40%
 ☆☆:     30%
 ☆☆☆:    22%
 ☆☆☆☆:    5%
 ☆☆☆☆☆:   3%
        """
        await message.channel.send(reply)
        return

    if conn.exists(user.name) == 0:
        reply = f"{message.author.mention}\n先にユーザ登録をして{point_name}を獲得できる状態にしてください。"
        await message.channel.send(reply)
        return

    if len(args) == 1:
        if int(conn.hget(user.name, "point")) < 3:
            reply = f"{message.author.mention} {point_name}が足りません。"
        else:
            rarity, t = play_gacha()
            reply = f"{message.author.mention}\n" + f"({t}) " + "☆" * rarity 
            await give_point(user, -3)
        await message.channel.send(reply)
        return

    if args[1] == "info":
        reply = f"{message.author.mention}\n"
        point = conn.hget(user.name, "point")
        reply += f"{point_name}: {point}"
        await message.channel.send(reply)
        return

    if args[1] == "10":
        reply = f"{message.author.mention}"
        if int(conn.hget(user.name, "point")) < 30:
            reply += f" {point_name}が足りません。"
        else:
            for i in range(11):
                rarity, t = play_gacha()
                reply += "\n" + f"({t}) " + "☆" * rarity
            await give_point(user, -30)
        await message.channel.send(reply)
        return

# ------------------------------ main process ----------------------------------
@client.event
async def on_message(message):
    if message.author.bot:
        return

    m = message.content
    if len(m) == 0:
        return

    messages = m.split()

    if client.user in message.mentions and len(messages) == 1:
        await how_to(message)
        return

    # function
    if m[0] == "!":
        if messages[0] == "!signup":
            await signup(messages, message.author, message.channel)
        if messages[0] == "!gacha":
            await gacha(messages, message)
        return

    # give point
    if conn.exists(message.author.name) != 0:
        await give_point(message.author, 1)

    # anagram
    if m[0] == "/":
        st = m[1:]
        st = st.split(" ")
        res = []
        for i in st:
            res.append(sh(i))
        await message.channel.send(" ".join(res))
        return

    # palindrome
    if len(m) > 1 and is_palindrome(m) == 0:
        rep = f"{message.author.mention} 回文です。"
        await message.channel.send(rep)

    # prime number
    m += "\x00"
    cnt = 0
    digits = ""
    while cnt < len(m):
        if m[cnt].isdigit():
            while m[cnt].isdigit():
                digits += m[cnt]
                cnt += 1
            cnt -= 1
        else:
            if digits != "" and MR(int(digits)):
                rep = f"{message.author.mention} 素数ですね……。"
                await message.channel.send(rep)
                break
            digits = ""
        cnt += 1
    m = m[:-1]

client.run(TOKEN)
# conn.flushall()
