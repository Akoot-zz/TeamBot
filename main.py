import asyncio

import discord
from discord.ext import commands

import util.io_util as io_util

# adding intents
intents = discord.Intents().all()

# Create team_bot instance
team_bot = commands.Bot(command_prefix='!', intents=intents)

teams_category_name = "State Teams"

team_names = ['international', 'alaska', 'texas', 'california', 'montana', 'new mexico', 'arizona', 'nevada',
              'colorado', 'oregon', 'wyoming', 'michigan', 'minnesota', 'utah', 'idaho', 'kansas', 'nebraska']

role_map = {}
channel_map = {}
category_map = {}


def sync_maps(guild: discord.Guild):
    role_map.clear()
    for role in guild.roles:
        role_map[role.name] = role.id
    for channel in guild.text_channels:
        channel_map[channel.name] = channel.id
    for category in guild.categories:
        category_map[category.name] = category.id


def get_channel_name(name):
    return name.replace(" ", "-")


# capitalize a team name
def get_role_name(name):
    new_name = ""
    for word in name.split():
        new_name += word[0:1].upper() + word[1:] + " "
    return new_name[:-1]


async def create_role(guild: discord.Guild, team_name: str):
    role_name = get_role_name(team_name)
    if role_name not in role_map:
        role = await guild.create_role(name=role_name, mentionable=True)
        role_map[role.name] = role.id
        print(f'created role: {role.name} <{role.id}>')


async def create_channel(guild: discord.Guild, team_name: str):
    channel_name = get_channel_name(team_name)
    teams_category = category_map[teams_category_name]
    if channel_name not in channel_map:
        channel = await guild.create_text_channel(name=channel_name, category=guild.get_channel(teams_category))
        channel_map[channel.name] = channel.id
        print('created channel: ', channel)


# create a role and channel for a team
async def create_team(guild: discord.Guild, team_name: str):
    await create_role(guild, team_name)
    await create_channel(guild, team_name)


# on_ready event
@team_bot.event
async def on_ready():
    print('Logged on as', team_bot.user)


# !cleanup command
@team_bot.command()
async def cleanup(ctx: commands.Context):
    guild: discord.Guild = ctx.guild

    sync_maps(guild)

    # remove roles and channels
    for team_name in team_names:
        role_name = get_role_name(team_name)
        channel_name = get_channel_name(team_name)

        # remove role
        if role_name in role_map:
            await guild.get_role(role_map[role_name]).delete()
            print('deleted role:', role_name)

        # remove channel
        if channel_name in channel_map:
            await guild.get_channel(channel_map[channel_name]).delete()
            print('deleted channel:', channel_name)

    # remove category
    for category in guild.categories:
        if category.name == teams_category_name:
            await category.delete()

    await ctx.send("All clean!")


@team_bot.command(aliases=['lt', 'listteams'])
async def list_teams(ctx: commands.Context):
    await ctx.send('' + "\n".join(team_names))


# !init command
@team_bot.command()
@commands.has_permissions(manage_messages=True)
async def init(ctx: commands.Context):
    guild: discord.Guild = ctx.guild

    has_teams_category = False
    for category in guild.categories:
        if category.name == teams_category_name:
            has_teams_category = True
            break

    if not has_teams_category:
        await guild.create_category(teams_category_name)

    sync_maps(guild)

    tasks = []
    for team_name in team_names:
        tasks.append(asyncio.create_task(create_team(guild, team_name)))
    await asyncio.wait(tasks)

    await ctx.send("Created teams!")


# !team command
@team_bot.command(aliases=['t'])
async def team(ctx: commands.Context, *args):
    member: discord.Member = ctx.author
    guild: discord.Guild = ctx.guild

    sync_maps(guild)

    role_name = get_role_name("".join(args).lower())
    if role_name in role_map:
        role = guild.get_role(role_map[role_name])
        if role not in member.roles:
            await member.add_roles(role)
            await ctx.send("You have been added to team " + role.name + "!")
        else:
            await ctx.send("You are already part of that team!")
    else:
        await ctx.send("That team doesn't exist!")


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
team_bot.run(auth['token'])
