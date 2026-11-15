import os
import asyncio
import aiohttp
import selectors
import discord
from discord.ext import commands

class myBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = '!', intents = discord.Intents.all())
        self.session = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        for file in os.listdir('./cogs'):
            if file.endswith('.py'):
                await self.load_extension(f'cogs.{file[:-3]}')

    async def on_ready(self):
        await self.change_presence(activity = discord.Streaming(name = f'Active in {len(self.guilds)} Servers', url = 'https://www.twitch.tv/roses_buds'))
        synced = await self.tree.sync() #here tree refers to the slash commands we have. think of it like an actual tree containing bracnhes for each command/cog 
        print(f'{self.user.name} Status: Online | Commands Sycned: {len(synced)}')

    async def close(self):
        try:
            super().close()
        finally:
            if self.session is not None and not self.session.closed:
                await self.session.close()

with open('token.txt') as token_file:
    token_file = token_file.read().strip()
    
bot = myBot()

def create_event_loop():
    loop = asyncio.SelectorEventLoop(selectors.SelectSelector())
    asyncio.set_event_loop(loop)
    return loop

async def main():
    async with bot:
        await bot.start(token_file)

discord.utils.setup_logging()
asyncio.run(main(), loop_factory = create_event_loop)