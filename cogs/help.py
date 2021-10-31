import discord
from discord.ext import commands

cmds = {
    'end':
        'Ends the game.',
    'guess':
        'Can only be used by spies in DM\'s. Used to guess the location.',
    'join':
        'Used to join a lobby.',
    'leave':
        'Used to leave a lobby.',
    'lobby':
        'Used to see all of the members in a lobby.',
    'locations':
        'Used to see a full list of all of the possible locations.',
    'rules':
        'A list of rules about how to play the game.',
    'spyfall':
        'Used to start a lobby.',
    'start':
        'Used to start a game once a lobby has been created.',
    'switch':
        'Switches which version the location is chosen from.',
    'vote':
        'Used to vote out whoever you think the spy is.'
}

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx, args=None):
        help_embed = discord.Embed(title="Help", color=0x00ffe3)
        command_names_list = [x.name for x in self.client.commands]

        if not args:
            help_embed.add_field(
                name="Commands:",
                value="\n".join([x.name for x in self.client.commands]),
                inline=False
            )
            help_embed.add_field(
                name="Details",
                value="Type `%help <command name>` for more details about each command.",
                inline=False
            )

        elif args in command_names_list:
            help_embed.add_field(
                name=args,
                value=cmds[args]
            )

        else:
            help_embed.add_field(
                name="Whoops!",
                value="That\'s not a command!"
            )

        await ctx.send(embed=help_embed)

def setup(client):
    client.add_cog(Help(client))