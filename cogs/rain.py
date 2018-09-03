import math
import discord
from discord.ext import commands
from utils import rpc_module, mysql_module, checks, parsing
import random

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Rain:
    def __init__(self, bot):
        self.bot = bot
        rain_config = parsing.parse_json('config.json')['rain']
        '''
        rain_max_recipients sets the max recipients for a rain. chosen randomly.
        rain_min_received sets the minimum possible rain received for a user.
        The number of rain recipients will be adjusted to fit these constraints
        if enabled via use_max_recipients and use_min_received
        '''
        self.rain_max_recipients = rain_config["rain_max_recipients"]
        self.use_max_recipients = rain_config["use_max_recipients"]
        self.rain_min_received = rain_config["rain_min_received"]
        self.use_min_received = rain_config["use_min_received"]

    @commands.command(pass_context=True)

    async def rain(self, ctx, amount: float):
        """Tip all online users"""
        if self.use_max_recipients and self.rain_max_recipients == 0:
            await self.bot.say("**:warning: Max users for rain is set to 0! Talk to the config owner. :warning:**")
            return

        snowflake = ctx.message.author.id

        mysql.check_for_user(snowflake)
        balance = mysql.get_balance(snowflake, check_update=True)

        if float(balance) < amount:
            await self.bot.say("{} **:warning: You cannot rain more money than you have! :warning:**".format(ctx.message.author.mention))
            return

        online_users1 = [x for x in ctx.message.server.members if x.status == discord.Status.online]
        online_users2 = [x for x in ctx.message.server.members if x.status == discord.Status.idle]
        online_users3 = [x for x in ctx.message.server.members if x.status == discord.Status.do_not_disturb]		
        online_users = online_users1 + online_users2 + online_users3
        if ctx.message.author in online_users:
            online_users.remove(ctx.message.author)

        for user in online_users:
            if user.bot:
                online_users.remove(user)

        if self.use_max_recipients:
            len_receivers = min(len(online_users), self.rain_max_recipients)
        else:
            len_receivers = len(online_users)

        if self.use_min_received:
            if amount < self.rain_min_received:
                await self.bot.say("{}, **:warning: {} is less than the minimum amount ({})  allowed to be rained! :warning:**".format(ctx.message.author.mention, amount, self.rain_min_received))
                return
            len_receivers = min(len_receivers, amount / self.rain_min_received)

        if len_receivers == 0:
            await self.bot.say("{}, **:warning:  you are all alone if you don't include bots! Try raining when people are online. :warning:**".format(ctx.message.author.mention))
            return

        amount_split = math.floor(float(amount) * 1e8 / len_receivers) / 1e8
        if amount_split == 0:
            await self.bot.say("{} **:warning: {} CRU is not enough to split between {} users! :warning:**".format(ctx.message.author.mention, amount, len_receivers))
            return
        receivers = []
        for i in range(int(len_receivers)):
            receivers.append(user)
            mysql.check_for_user(user.id)
            mysql.add_tip(snowflake, user.id, amount_split)
        long_rain_msg = ":moneybag: {} **Rained {} CRU on {} users [{}]** :moneybag: ".format(ctx.message.author.mention, str(amount_split), len_receivers, str(amount))

        if len(long_rain_msg) > 2000:
            await self.bot.say(":moneybag: {} **Rained {} CRU on {} users [{}]** :moneybag: ".format(ctx.message.author.mention, str(amount_split), len_receivers, str(amount)))
        else:
            await self.bot.say(long_rain_msg)

    @commands.command()
    async def rain_info(self):        
        """Display min rain amount and maximum rain recipients"""
        if self.use_max_recipients:
            st_max_users = str(self.rain_max_recipients)
        else:
            st_max_users = "<disabled>"

        if self.use_min_received:
            st_min_received = str(self.rain_min_received)
        else:
            st_min_received = "<disabled>"
            
        await self.bot.say(":information_source: Rain info: max recipients {}, min amount receivable {} :information_source:".format(st_max_users, st_min_received))

def setup(bot):
    bot.add_cog(Rain(bot))
