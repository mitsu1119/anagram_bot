import discord
import string
import random
import time
import os

TOKEN = os.environ["DISCORD_BOT_TOKEN"]

client = discord.Client()

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

def sh(st):
    res = list(st)
    random.shuffle(res)
    return "".join(res)

def is_palindrome(string):
    return string.find(string[::-1])

# ------------------------------ functions -------------------------------------
@client.event
async def on_ready():
    print("login success")

async def how_to(message):
    reply = f"""
    {message.author.mention}
    【使い方】

    ・/[str]: strのアナグラムを生成します。


    ・[prime_number]: 素数であることを指摘してくれます。

    ・だまれ @hoge: hogeのメッセージを約30秒間逐次削除してくれます。
    """
    await message.channel.send(reply)

silent_now = None
silent_time = 0
async def silent(silent_user, speaker, channel):
    global silent_now
    global silent_time

    if silent_now == None:
        silent_now = silent_user
        silent_time = time.time()
        return

async def delete(message):
    global silent_now
    global silent_time

    if time.time() >= silent_time + 30:
        silent_now = None
        silent_time = 0
        return
    await message.delete()

# ------------------------------ main process ----------------------------------
@client.event
async def on_message(message):
    if message.author.bot:
        return

    if message.author == silent_now:
        await delete(message)
        return

    messages = message.content.split()
    if client.user in message.mentions and len(messages) == 1:
        await how_to(message)
        return

    if len(message.content) >= 1 and message.content.isnumeric() and MR(int(message.content)):
        rep = f"{message.author.mention} 素数ですね……。"
        await message.channel.send(rep)
    
    if len(message.content) > 1 and is_palindrome(message.content) == 0:
        rep = f"{message.author.mention} 回文です。"
        await message.channel.send(rep)

    if len(messages) == 2 and messages[0] == "だまれ":
        if message.mentions[0] in client.users:
            await silent(message.mentions[0], message.author, message.channel)
            return

    if len(message.content) >= 1 and message.content[0] == "/":
        st = message.content[1:]
        st = st.split(" ")
        res = []
        for i in st:
            res.append(sh(i))
        await message.channel.send(" ".join(res))
        return

client.run(TOKEN)
