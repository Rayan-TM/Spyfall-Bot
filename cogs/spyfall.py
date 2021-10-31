import discord
from discord.ext import commands, tasks
import random
import time
import math
from string import ascii_uppercase

locations = [
    "Airplane",
    "Bank",
    "Beach",
    "Broadway Theater",
    "Casino",
    "Cathedral",
    "Circus Tent",
    "Corporate Party",
    "Crusader Army",
    "Day Spa",
    "Embassy",
    "Hospital",
    "Hotel",
    "Airplane",
    "Military Base",
    "Movie Studio",
    "Ocean Liner",
    "Passenger Train",
    "Pirate Ship",
    "Polar Station",
    "Police Station",
    "Restaurant",
    "School",
    "Service Station",
    "Space Station",
    "Submarine",
    "Supermarket",
    "University"
]

locations_2 = [
    "Amusement Park",
    "Art Museum",
    "Candy Factory",
    "Cat Show",
    "Cemetery",
    "Coal Mine",
    "Construction Site",
    "Gaming Convention",
    "Gas Station",
    "Harbor Docks",
    "Ice Hockey Stadium",
    "Jail",
    "Jazz Club",
    "Library",
    "Night Club",
    "Race Track",
    "Retirement Home",
    "Rock Concert",
    "Sightseeing Bus",
    "Stadium",
    "Subway",
    "The U.N.",
    "Vineyard",
    "Wedding",
    "Zoo"
]

locations_list = ''
for location in locations:
    locations_list += f'\n{location}'
locations_embed = discord.Embed(title='Locations', description=locations_list, color=0x00ffb9)

locations_list_2 = ''
for location in locations_2:
    locations_list_2 += f'\n{location}'
locations_embed_2 = discord.Embed(title='Locations - 2', description=locations_list_2, color=0x00ffb9)

spy_embed = discord.Embed(title='You are the spy. Good Luck!',
                          description='For a list of locations, you can use `%locations` in this DM.\n'
                                      'If you think you figured out the location, you can use'
                                      '`%guess [location]` **in this DM**. Ex: `%guess ocean liner`\n'
                                      'Remember: you only have one guess, so use it wisely!')

sessions = {}

votes = {}

votekicks = {}


def time_fix(num):
    num = round(num)

    if num < 60:
        return f'{num} seconds'

    elif num == 60:
        return '1 minute'

    elif 3600 > num > 60:
        seconds = num % 60
        minutes = math.floor(num / 60)

        if seconds != 0:
            return f'{minutes} minutes {seconds} seconds'
        else:
            return f'{minutes} minutes'

    elif num == 3600:
        return '1 hour'

    elif num > 3600:
        minutes = num % 3600
        minutes = math.floor(minutes / 60)
        hours = math.floor(num / 3600)

        if minutes != 0:
            return f'{hours} hours {minutes} minutes'
        else:
            return f'{hours} hours'


def start_session(code):
    sessions[code] = {
        'owner': '',
        'game': False,
        'lobby': [],
        'timer': 0,
        'spy': '',
        'location': '',
        'channel': 0,
        'postgame': False,
        'version': 1
    }


def in_game(num):
    for session in sessions:
        if num in sessions[session]['lobby']:
            return True
    else:
        return False


def sweep(session):
    for message_id in votes:
        for user_id in sessions[session]['lobby']:
            if user_id == votes[message_id][0]:
                del votes[message_id]

    for message_id in votekicks:
        for user_id in sessions[session]['lobby']:
            if user_id == votekicks[message_id][0]:
                del votekicks[message_id]


class Spyfall(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.timer.start()

    @tasks.loop(seconds=1)
    async def timer(self):
        for session in sessions:
            if sessions[session]['game']:
                if time.time() >= sessions[session]['timer']:
                    sessions[session]['game'] = False
                    sessions[session]['postgame'] = True
                    sessions[session]['timer'] = round(time.time() + 60)

                    channel = await self.client.fetch_channel(sessions[session]['channel'])
                    await channel.send('Time\'s up! You have 1 minute to vote (`%vote @[player]`) before the spy wins.')

                elif 'seconds' not in time_fix(sessions[session]["timer"] - round(time.time())):
                    channel = await self.client.fetch_channel(sessions[session]['channel'])
                    await channel.send(f'{time_fix(sessions[session]["timer"] - round(time.time()))} left!')

            elif sessions[session]['postgame']:
                if time.time() >= sessions[session]['timer']:
                    sessions[session]['postgame'] = False

                    spy = await self.client.fetch_user(sessions[session]['spy'])
                    channel = await self.client.fetch_channel(sessions[session]['channel'])

                    spy_survived_embed = discord.Embed(title='Spy Wins!',
                                                       description='You did not vote out the spy in time.',
                                                       color=0xff0000)
                    spy_survived_embed.add_field(name='Spy', value=spy)
                    spy_survived_embed.add_field(name='Location', value=sessions[session]['location'])
                    spy_survived_embed.set_author(name=spy.name, icon_url=spy.avatar_url)

                    await channel.send(embed=spy_survived_embed)

                    try:
                        sweep(session)
                    except RuntimeError:
                        pass

    @commands.command()
    async def rules(self, ctx):
        rules_embed = discord.Embed(
            title='How To Play Spyfall',
            description='• This game takes at least 3 people to play\n'
                        '• When the game starts, one person is randomly chosen as the "spy"\n'
                        '• A random location is also chosen when the game starts (`%locations` for a list of possible locations)\n'
                        '• The location will be revealed to everyone except for the spy\n'
                        '• At the start of the game, one person is randomly chosen to ask someone a question about the location\n'
                        '• After the person answers the question, he/she will pick someone else to ask, and so on\n'
                        '• The spy\'s objective is to figure out the location based on everyone else\'s answers\n'
                        '• Everyone else\'s objective is to vote out the spy before the spy figures out the location\n'
                        '• Oh yeah there\'s also a 10-minute timer, and if you don\'t vote out the spy by then, you lose\n\n'
                        'Here is a link to the online game (originally a board game): [Click Me!](https://www.spyfall.app/)',
            color=0x0027ff
        )
        rules_embed.set_footer(text='i didnt invent spyfall please dont sue me')
        await ctx.send(embed=rules_embed)

    @commands.command()
    async def spyfall(self, ctx):
        if not in_game(ctx.author.id):
            code = ''.join(random.choice(ascii_uppercase) for i in range(4))

            start_session(code)
            sessions[code]['lobby'].append(ctx.author.id)
            sessions[code]['owner'] = ctx.author.id
            sessions[code]['channel'] = ctx.channel.id

            await ctx.send(f'{ctx.author.name} created a Spyfall lobby with the room code `{code}`.')

        else:
            await ctx.send('You\'re already in a game! Do `%leave` to leave, or wait for your game to finish.')

    @commands.command()
    async def join(self, ctx, *, code):
        if not in_game(ctx.author.id):
            for session in sessions:
                if session.lower() == code.lower():
                    sessions[session]['lobby'].append(ctx.author.id)
                    await ctx.send(f'{ctx.author.name} joined lobby {code.upper()}'
                                   f' ({len(sessions[session]["lobby"])} players).')

                    break
            else:
                await ctx.send('That lobby doesn\'t exist :/')

        else:
            await ctx.send('You\'re already in a game! Do `%leave` to leave, or wait for your game to finish.')

    @commands.command()
    async def leave(self, ctx):
        for session in sessions:
            if ctx.author.id in sessions[session]['lobby']:
                sessions[session]['lobby'].remove(ctx.author.id)
                await ctx.send(f'You left lobby {session}.')

                if sessions[session]['game']:
                    if ctx.author.id == sessions[session]['spy']:
                        sessions[session]['game'] = False
                        sessions[session]['postgame'] = False
                        await ctx.send(f'{ctx.author.name} was the spy. Game Over!')

                        try:
                            sweep(session)
                        except RuntimeError:
                            pass

                if ctx.author.id == sessions[session]['owner']:
                    try:
                        new_owner = random.choice(sessions[session]['lobby'])
                        sessions[session]['owner'] = new_owner

                        new_owner_name = await self.client.fetch_user(new_owner)

                        await ctx.send(f'{new_owner_name.name} is the new owner.')

                    except IndexError:
                        del sessions[session]
                        await ctx.send('The lobby was removed.')

                break
        else:
            await ctx.send('You are not in a game!')

    @commands.command()
    async def kick(self, ctx, member: discord.Member):
        for session in sessions:
            if ctx.author.id == sessions[session]['owner']:
                if member.id in sessions[session]['lobby']:
                    if member.id != ctx.author.id:
                        sessions[session]['lobby'].remove(member.id)
                        await ctx.send(f'Removed {member.name} from your lobby.')

                        if sessions[session]['game']:
                            if member.id == sessions[session]['spy']:
                                sessions[session]['game'] = False
                                sessions[session]['postgame'] = False

                                await ctx.send(f'{ctx.author.name} was the spy. Game Over!')

                                try:
                                    sweep(session)
                                except RuntimeError:
                                    pass

                    else:
                        await ctx.send('You can\'t kick yourself!')

                else:
                    await ctx.send('That person isn\'t in your lobby!')

                break

        else:
            await ctx.send('You have to own a lobby to use that command!')

    @commands.command()
    async def votekick(self, ctx, member: discord.Member):
        for session in sessions:
            if ctx.author.id in sessions[session]['lobby']:
                if member.id in sessions[session]['lobby']:
                    if member.id != ctx.author.id:
                        if len(sessions[session]['lobby']) > 2:
                            for message_id in votekicks:
                                if member.id in votekicks[message_id]:
                                    await ctx.send('There is already a vote to kick that person!')
                                    break

                            else:
                                votekick_embed = discord.Embed(title=f'Kick {member.name}?', description=':white_check_mark: - Yes',
                                                               color=0xffec00)
                                votekick_message = await ctx.send(embed=votekick_embed)

                                await votekick_message.add_reaction('✅')

                                votekicks[votekick_message.id] = [
                                    member.id,
                                    session,
                                    0
                                ]

                        else:
                            await ctx.send('There must be at least 3 people in the lobby to start a votekick!')

                    else:
                        await ctx.send('You can\'t votekick yourself!')

                else:
                    await ctx.send('That person isn\'t in your lobby!')

                break

        else:
            await ctx.send('You have to be in a lobby to use that command!')

    @commands.command()
    async def lobby(self, ctx):
        lobby = ''

        for session in sessions:
            if ctx.author.id in sessions[session]['lobby']:
                for player_id in sessions[session]['lobby']:
                    player_name = await self.client.fetch_user(player_id)
                    if player_id == sessions[session]['owner']:
                        lobby += f'\n{player_name.name} - Owner'
                    else:
                        lobby += f'\n{player_name.name}'

                break
        else:
            await ctx.send('You have to be in a lobby to use that command!')

        if lobby:
            lobby_embed = discord.Embed(title=f'Lobby - {session} ({len(sessions[session]["lobby"])} players)',
                                        description=lobby, color=0xfffefe)

            await ctx.send(embed=lobby_embed)

    @commands.command()
    async def start(self, ctx):
        for session in sessions:
            if ctx.author.id == sessions[session]['owner']:
                if len(sessions[session]['lobby']) >= 1:  # &EDIT
                    sessions[session]['game'] = True
                    sessions[session]['spy'] = random.choice(sessions[session]['lobby'])
                    if sessions[session]['version'] == 1:
                        sessions[session]['location'] = random.choice(locations)
                    elif sessions[session]['version'] == 2:
                        sessions[session]['location'] = random.choice(locations_2)
                    sessions[session]['channel'] = ctx.channel.id
                    sessions[session]['timer'] = round(time.time() + 600)

                    for player_id in sessions[session]['lobby']:
                        player = await self.client.fetch_user(player_id)
                        if player_id == sessions[session]['spy']:
                            await player.send(embed=spy_embed)
                        else:
                            await player.send(f'The location is `{sessions[session]["location"]}`. Good Luck!')

                    someone = await self.client.fetch_user(random.choice(sessions[session]["lobby"]))

                    await ctx.send(f'Started the timer.'
                                   f' {someone.mention}, you can start.')

                else:
                    await ctx.send('You need at least 3 players to start!')

                break
            else:
                await ctx.send('You have to own a lobby to use that command!')

    @commands.command()
    async def end(self, ctx):
        for session in sessions:
            if ctx.author.id == sessions[session]['owner']:
                if sessions[session]['game']:
                    sessions[session]['game'] = False
                    sessions[session]['postgame'] = False
                    await ctx.send('Ended the current game.')

                    try:
                        sweep(session)
                    except RuntimeError:
                        pass

                else:
                    await ctx.send('You haven\'t started the game yet!')

                break

        else:
            await ctx.send('You have to own a lobby to use that command!')

    @commands.command()
    async def locations(self, ctx, *, version=None):
        if not version or version == '1':
            await ctx.send(embed=locations_embed)
        elif version == '2':
            await ctx.send(embed=locations_embed_2)

    @commands.command()
    async def guess(self, ctx):
        pass

    @commands.command()
    async def switch(self, ctx):
        for session in sessions:
            if ctx.author.id == sessions[session]['owner']:
                if sessions[session]['version'] == 1:
                    sessions[session]['version'] = 2

                    await ctx.send('Switched locations to version 2.')
                elif sessions[session]['version'] == 2:
                    sessions[session]['version'] = 1

                    await ctx.send('Switched locations to version 1.')

                break

        else:
            await ctx.send('You have to own a lobby to use that command!')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and message.author != self.client.user:
            for session in sessions:
                if sessions[session]['game']:
                    if message.author.id == sessions[session]['spy']:
                        if message.content.lower().startswith('%guess'):
                            split_message = message.content.split(' ', 1)
                            guess = split_message[1]
                            if guess.lower() == sessions[session]['location'].lower():
                                await message.add_reaction('✅')

                                spy = await self.client.fetch_user(sessions[session]['spy'])
                                channel = await self.client.fetch_channel(sessions[session]['channel'])

                                correct_guess_embed = discord.Embed(title='Spy Wins!',
                                                                    description=f'{spy.name} '
                                                                                f'correctly guessed the location.',
                                                                    color=0xff0000)
                                correct_guess_embed.add_field(name='Spy', value=spy)
                                correct_guess_embed.add_field(name='Location', value=sessions[session]['location'])
                                correct_guess_embed.set_author(name=message.author.name,
                                                               icon_url=message.author.avatar_url)

                                sessions[session]['game'] = False
                                sessions[session]['postgame'] = False
                                await channel.send(embed=correct_guess_embed)

                                try:
                                    sweep(session)
                                except RuntimeError:
                                    pass

                            else:
                                await message.add_reaction('❌')

                                spy = await self.client.fetch_user(sessions[session]['spy'])
                                channel = await self.client.fetch_channel(sessions[session]['channel'])

                                incorrect_guess_embed = discord.Embed(title='Spy Loses!',
                                                                      description=f'{spy.name} '
                                                                                  f'guessed the wrong location.',
                                                                      color=0x00ff13)
                                incorrect_guess_embed.add_field(name='Spy', value=spy)
                                incorrect_guess_embed.add_field(name='Location', value=sessions[session]['location'])
                                incorrect_guess_embed.set_author(name=message.author.name,
                                                                 icon_url=message.author.avatar_url)
                                incorrect_guess_embed.add_field(name='Guess', value=guess)

                                sessions[session]['game'] = False
                                sessions[session]['postgame'] = False
                                await channel.send(embed=incorrect_guess_embed)

                                try:
                                    sweep(session)
                                except RuntimeError:
                                    pass

                        break

    @commands.command()
    async def vote(self, ctx, member: discord.Member):
        for session in sessions:
            if sessions[session]['game']:
                if ctx.author.id in sessions[session]['lobby']:
                    if member.id in sessions[session]['lobby']:
                        for message in votes:
                            if member.id in votes[message]:
                                await ctx.send(f'There is already a vote for {member.name}!')
                                break

                        else:
                            vote_embed = discord.Embed(title=f'Vote {member.name}?',
                                                       description=':white_check_mark: - Yes',
                                                       color=0xffec00)
                            vote_message = await ctx.send(embed=vote_embed)
                            await vote_message.add_reaction('✅')

                            votes[vote_message.id] = [
                                member.id,
                                session,
                                0
                            ]

                            break

                    else:
                        await ctx.send('That person is not in your lobby!')

                    break

            elif sessions[session]['postgame']:
                if ctx.author.id in sessions[session]['lobby']:
                    if member.id in sessions[session]['lobby']:
                        for message in votes:
                            if member.id in votes[message]:
                                await ctx.send(f'There is already a vote for {member.name}!')
                                break

                        else:
                            vote_embed = discord.Embed(title=f'Vote {member.name}?',
                                                       description=':white_check_mark: - Yes',
                                                       color=0xffec00)
                            vote_message = await ctx.send(embed=vote_embed)
                            await vote_message.add_reaction('✅')

                            votes[vote_message.id] = [
                                member.id,
                                session,
                                0
                            ]

                            break

                    else:
                        await ctx.send('That person is not in your lobby!')

                    break

        else:
            await ctx.send('You have to be in a game to use that command!')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id == self.client.user.id:
            if reaction.message.id in votes:
                if sessions[votes[reaction.message.id][1]]['game'] or sessions[votes[reaction.message.id][1]]['postgame']:
                    if user.id in sessions[votes[reaction.message.id][1]]['lobby']:
                        if reaction.emoji == '✅':
                            member = await self.client.fetch_user(votes[reaction.message.id][0])

                            votes[reaction.message.id][2] += 1

                            majority = round(len(sessions[votes[reaction.message.id][1]]['lobby']) / 2)

                            new_vote_embed = discord.Embed(title=f'Vote {member.name}?',
                                                           description=f':white_check_mark: - Yes '
                                                                       f'({votes[reaction.message.id][2]}/{majority}'
                                                                       f' votes)',
                                                           color=0xffec00)
                            await reaction.message.edit(embed=new_vote_embed)

                            if votes[reaction.message.id][2] >= majority:
                                channel = await self.client.fetch_channel(
                                    sessions[votes[reaction.message.id][1]]['channel'])
                                sessions[votes[reaction.message.id][1]]['game'] = False
                                sessions[votes[reaction.message.id][1]]['postgame'] = False

                                if member.id == sessions[votes[reaction.message.id][1]]['spy']:
                                    correct_vote_embed = discord.Embed(title='Spy Loses!',
                                                                       description='The spy was voted off.',
                                                                       color=0x00ff13)
                                    correct_vote_embed.add_field(name='Spy', value=member)
                                    correct_vote_embed.add_field(name='Location',
                                                                 value=sessions[votes[reaction.message.id][1]][
                                                                     'location'])
                                    correct_vote_embed.set_author(name=member.name, icon_url=member.avatar_url)

                                    await channel.send(embed=correct_vote_embed)

                                    try:
                                        sweep(votes[reaction.message.id][1])
                                    except RuntimeError:
                                        pass

                                else:
                                    spy = await self.client.fetch_user(sessions[votes[reaction.message.id][1]]['spy'])

                                    incorrect_vote_embed = discord.Embed(title='Spy Wins!',
                                                                         description='You voted off the wrong person.',
                                                                         color=0xff0000)
                                    incorrect_vote_embed.add_field(name='Spy', value=spy)
                                    incorrect_vote_embed.add_field(name='Location',
                                                                   value=sessions[votes[reaction.message.id][1]][
                                                                       'location'])
                                    incorrect_vote_embed.set_author(name=spy.name, icon_url=spy.avatar_url)

                                    await channel.send(embed=incorrect_vote_embed)

                                    try:
                                        sweep(votes[reaction.message.id][1])
                                    except RuntimeError:
                                        pass

            elif reaction.message.id in votekicks:
                if user.id in sessions[votekicks[reaction.message.id][1]]['lobby']:
                    if reaction.emoji == '✅':
                        player = await self.client.fetch_user(votekicks[reaction.message.id][0])
                        votekicks[reaction.message.id][2] += 1
                        majority = round(len(sessions[votekicks[reaction.message.id][1]]['lobby']) / 2)

                        new_votekick_embed = discord.Embed(title=f'Kick {player.name}?',
                                                           description=f':white_check_mark: - Yes '
                                                                       f'({votekicks[reaction.message.id][2]}/{majority}'
                                                                       f' votes)',
                                                           color=0xffec00)
                        await reaction.message.edit(embed=new_votekick_embed)

                        if votekicks[reaction.message.id][2] >= majority:
                            sessions[votekicks[reaction.message.id][1]]['lobby'].remove(votekicks[reaction.message.id][0])
                            channel = await self.client.fetch_channel(sessions[votekicks[reaction.message.id][1]]['channel'])

                            await channel.send(f'{player.name} was removed from the lobby.')

                            if player.id == sessions[votekicks[reaction.message.id][1]]['owner']:
                                new_owner = random.choice(sessions[votekicks[reaction.message.id][1]]['lobby'])
                                sessions[votekicks[reaction.message.id][1]]['owner'] = new_owner
                                new_owner_name = await self.client.fetch_user(new_owner)

                                await channel.send(f'{new_owner_name} is the new owner.')

                            if sessions[votekicks[reaction.message.id][1]]['game']:
                                if player.id == sessions[votekicks[reaction.message.id][1]]['spy']:
                                    sessions[votekicks[reaction.message.id][1]]['game'] = False
                                    sessions[votekicks[reaction.message.id][1]]['postgame'] = False

                                    await channel.send(f'{player.name} was the spy. Game Over!')

                                    try:
                                        sweep(votekicks[reaction.message.id][1])
                                    except RuntimeError:
                                        pass

                            del votekicks[reaction.message.id]

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if reaction.message.author.id == self.client.user.id:
            if reaction.message.id in votes:
                if sessions[votes[reaction.message.id][1]]['game']:
                    if user.id in sessions[votes[reaction.message.id][1]]['lobby']:
                        if reaction.emoji == '✅':
                            member = await self.client.fetch_user(votes[reaction.message.id][0])
                            majority = round(len(sessions[votes[reaction.message.id][1]]['lobby']) / 2)

                            votes[reaction.message.id][2] -= 1

                            new_vote_embed = discord.Embed(title=f'Vote {member.name}?',
                                                           description=f':white_check_mark: - Yes '
                                                                       f'({votes[reaction.message.id][2]}'
                                                                       f'/{majority} votes)'
                                                                       f' votes)',
                                                           color=0xffec00)
                            await reaction.message.edit(embed=new_vote_embed)

            elif reaction.message.id in votekicks:
                if user.id in sessions[votekicks[reaction.message.id][1]]['lobby']:
                    if reaction.emoji == '✅':
                        member = await self.client.fetch_user(votekicks[reaction.message.id][0])
                        majority = round(len(sessions[votekicks[reaction.message.id][1]]['lobby']) / 2)

                        votekicks[reaction.message.id][2] -= 1

                        new_votekick_embed = discord.Embed(title=f'Kick {member.name}?',
                                                           description=f':white_check_mark: - Yes '
                                                                       f'({votekicks[reaction.message.id][2]}'
                                                                       f'/{majority} votes)',
                                                           color=0xffec00)
                        await reaction.message.edit(embed=new_votekick_embed)


def setup(client):
    client.add_cog(Spyfall(client))
