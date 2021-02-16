import discord
from discord.ext import commands

import util.io_util as io_util

# adding intents
intents = discord.Intents().all()

# Create team_bot instance
team_bot = commands.Bot(command_prefix='!', intents=intents)

team_names = ['international', 'alaska', 'texas', 'california', 'montana', 'new mexico', 'arizona', 'nevada',
              'colorado', 'oregon', 'wyoming', 'michigan', 'minnesota', 'utah', 'idaho', 'kansas', 'nebraska']


# capitalize a team name
def capitalize(name):
    new_name = ""
    for word in name.split():
        new_name += word[0:1].upper() + word[1:] + " "
    return new_name[:-1]


def create_team(guild: discord.Guild, team_name: str):
    if team_name not in guild.roles:
        guild.create_role(name=team_name, mentionable=True)
        guild.create_text_channel(team_name)


# on_ready event
@team_bot.event
async def on_ready():
    print('Logged on as', team_bot.user)


@team_bot.command()
@commands.has_permissions(manage_messages=True)
async def init(ctx: commands.Context):
    for team_name in team_names:
        create_team(ctx.guild, capitalize(team_name))
    await ctx.send("Created teams!")


@team_bot.command(aliases=['t'])
async def team(ctx: commands.Context, **args):
    member: discord.Member = ctx.author
    role_name = "".join(args).lower()
    if role_name in team_names:
        if ctx.guild.has_role(role_name):
            await member.add_roles(role_name)
            await member.send("You have been added to team " + ctx.guild.get)
    else:
        await member.send("You are already in that team!")


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
team_bot.run(auth['token'])
