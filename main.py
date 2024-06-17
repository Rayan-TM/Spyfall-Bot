import discord
from discord.ext import commands

cogs = [
    'cogs.spyfall',
    'cogs.help'
]

intents = discord.Intents.all()

TOKEN = 'BOT-TOKEN-HERE'

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='%',
            case_insensitive=True,
            intents=intents,
            help_command=None
        )

    async def on_ready(self):
        print('Bot is online.')

        print('\nLoading cogs...')
        for cog in cogs:
            try:
                await client.load_extension(cog)
                print(f'Loaded {cog}')

            except Exception as e:
                print(e)


client = Bot()
client.run(TOKEN)
client.remove_command('help')
