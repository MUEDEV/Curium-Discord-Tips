import discord, os
from discord.ext import commands
from utils import checks, output
from aiohttp import ClientSession
import requests
import json

class Stats:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def stats(self, amount=1):
        """
        Show stats about CRU
        """
        headers={"user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
        try:
                    btcapi = 'https://coinlib.io/api/v1/coin?key=7f291e8e177748eb&pref=BTC&symbol=CRU'
                    btcprice = requests.get(btcapi)
                    volume = btcprice.json()['total_volume_24h']
                    low = btcprice.json()['low_24h']
                    high = btcprice.json()['high_24h']
                    price = btcprice.json()['price']
					
                    embed = discord.Embed(title="Curium Stats", colour=0x00FF00)
                    embed.add_field(name="24-hour Volume", value=+ volume + " BTC")
                    embed.add_field(name="24-hour Low", value=+ low +" BTC")
                    embed.add_field(name="24-hour High", value=+ high +" BTC")
                    embed.add_field(name="Price", value=+ price +" BTC")
                    await self.bot.say(embed=embed)
        except:
           self.bot.say(":warning: Error fetching prices!")


def setup(bot):
    bot.add_cog(Stats(bot))
