import discord
import os
from dotenv import load_dotenv
from server import keep_alive
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from weather_code import weather_code


load_dotenv('.env')

# 自分のBotのアクセストークンに置き換えてください
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

# 接続に必要なオブジェクトを生成
client = discord.Client(intents=intents)

cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries=5, backoff_factor= 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
weather_url = "https://api.open-meteo.com/v1/forecast"
w_params = {
    "latitude": 35.6895,
    "longitude": 139.6917,
    "current": ["temperature_2m", "apparent_temperature", "preciptation", "weather_code"],
    "timezone": "Asia/Tokyo",
    "forecast_days": 1
}

send_channels_id=[ 1238788719910326294 ]

# 起動時に動作する処理
@client.event
async def on_ready():
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    if message.content == '過疎':
        await message.channel.send('過疎ですか...そうですか...')

def wea_get(url, params=w_params, channels_id=send_channels_id):
    responses = openmeteo.weather_api(url=url, params=params)

    current = responses.Current()
    current_apparent_temperature = current.Variables(0).Value()
    current_precipitation = current.Variables(1).Value()
    current_weather_code = current.Variables(2).Value()

    daily = responses.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    
    for i in channels_id:
        channel=client.get_channel(i)
        data=f'''\
----------
# 本日の天気をお知らせします。
----------
天気：{ weather_code[current_weather_code] }
最高気温：{ daily_temperature_2m_max }℃
最低気温：{ daily_temperature_2m_min }℃
体感温度：{ current_apparent_temperature }℃
降水量：{ current_precipitation }mm

'''
        channel.send(data)



# Botの起動とDiscordサーバーへの接続
keep_alive()
client.run(TOKEN)