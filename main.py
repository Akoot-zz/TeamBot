import discord
from discord.ext import commands

import util.io_util as io_util
import util.string_util as string_util

# adding intents
intents = discord.Intents().all()

# Create team_bot instance
team_bot = commands.Bot(command_prefix='!', intents=intents)

team_names = ['international', 'alaska', 'texas', 'california', 'montana', 'new mexico', 'arizona', 'nevada',
              'colorado', 'oregon', 'wyoming', 'michigan', 'minnesota', 'utah', 'idaho', 'kansas', 'nebraska']

spam_channel_name = "bot-spam"

colors = io_util.load_json("colors.json")

help_embed = discord.Embed(
    color=discord.Color.from_rgb(137, 190, 244),
    title="Bot help",
    description="Show a list of teams by typing `!listteams`\n\n"
                "To join a team, simply type `!team <team name>`\n"
                "*Example: `!team new mexico`*\n\n"
                "If for whatever reason you chose the wrong team, you can change it using the same command...\n\n"
)


def get_text_category(guild: discord.Guild):
    for category in guild.categories:
        if category.name.lower() == "text channels":
            return category
    return None


def get_spam_channel(guild: discord.Guild):
    for channel in guild.channels:
        if channel.name == spam_channel_name:
            return channel
    return None


def get_role_name(team_name: str):
    return string_util.capitalize(team_name)


def get_category_name(team_name: str):
    return "Team " + string_util.capitalize(team_name)


def get_text_channel_name(team_name: str):
    return team_name.replace(" ", "-").lower()


def get_voice_channel_name(team_name: str):
    return string_util.capitalize(team_name)


def get_role(guild: discord.Guild, team_name: str):
    role_name = get_role_name(team_name)
    for role in guild.roles:
        if role.name == role_name:
            return role
    return None


def get_category(guild: discord.Guild, team_name: str):
    category_name = get_category_name(team_name)
    for category in guild.categories:
        if category.name == category_name:
            return category
    return None


def get_text_channel(guild: discord.Guild, team_name: str):
    text_channel_name = get_text_channel_name(team_name)
    for text_channel in guild.text_channels:
        if text_channel.name == text_channel_name:
            return text_channel
    return None


def get_voice_channel(guild: discord.Guild, team_name: str):
    voice_channel_name = get_voice_channel_name(team_name)
    for voice_channel in guild.voice_channels:
        if voice_channel.name == voice_channel_name:
            return voice_channel
    return None


def get_current_team_role(member: discord.Member):
    for role in member.roles:
        if role.name.lower() in team_names:
            return role
    return None


async def create_role(guild: discord.Guild, team_name: str):
    if get_role(guild, team_name) is None:
        role_name = get_role_name(team_name)
        role = await guild.create_role(name=role_name, mentionable=True)
        print(f'created role: {role.name} <{role.id}>')


async def create_category(guild: discord.Guild, team_name: str):
    if get_category(guild, team_name) is None:
        category_name = get_category_name(team_name)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            get_role(guild, team_name): discord.PermissionOverwrite(read_messages=True)
        }
        category = await guild.create_category(name=category_name, overwrites=overwrites)
        print(f'created category: {category.name} <{category.id}>')


async def create_voice_channel(guild: discord.Guild, team_name: str):
    if get_voice_channel(guild, team_name) is None:
        category = get_category(guild, team_name)
        channel_name = get_voice_channel_name(team_name)
        channel = await guild.create_voice_channel(name=channel_name, category=category)
        print(f'created voice channel: {channel.name} <{channel.id}>')


async def create_text_channel(guild: discord.Guild, team_name: str):
    if get_text_channel(guild, team_name) is None:
        category = get_category(guild, team_name)
        channel_name = get_text_channel_name(team_name)
        channel = await guild.create_text_channel(name=channel_name, category=category)
        print(f'created text channel: {channel.name} <{channel.id}>')


# create a role and channel for a team
async def create_team(guild: discord.Guild, team_name: str):
    await create_role(guild, team_name)
    await create_category(guild, team_name)
    await create_text_channel(guild, team_name)
    await create_voice_channel(guild, team_name)


# on_ready event
@team_bot.event
async def on_ready():
    print('Logged on as', team_bot.user)


# !cleanup command
@team_bot.command()
@commands.has_permissions(manage_guild=True)
async def cleanup(ctx: commands.Context):
    guild: discord.Guild = ctx.guild

    spam_channel = get_spam_channel(guild)
    if spam_channel in guild.text_channels:
        await spam_channel.delete()

    # remove roles and channels
    for team_name in team_names:

        role = get_role(guild, team_name)
        category = get_category(guild, team_name)
        text_channel = get_text_channel(guild, team_name)
        voice_channel = get_voice_channel(guild, team_name)

        if role in guild.roles:
            print(f'Deleting role: "{role.name}" <{role.id}>')
            await role.delete()

        if category in guild.categories:
            print(f'Deleting category: "{category.name}" <{category.id}>')
            await category.delete()

        if text_channel in guild.text_channels:
            print(f'Deleting text channel: "{text_channel.name}" <{text_channel.id}>')
            await text_channel.delete()

        if voice_channel in guild.voice_channels:
            print(f'Deleting voice channel: "{voice_channel.name}" <{voice_channel.id}>')
            await voice_channel.delete()

    if ctx.channel is not spam_channel:
        await ctx.send("All clean!")


@team_bot.command(aliases=['lt', 'listteams'])
async def list_teams(ctx: commands.Context):
    await ctx.send('' + "\n".join(team_names))


@team_bot.command(name='h')
async def help_command(ctx: commands.Context):
    await ctx.channel.send(embed=help_embed)


def get_color(hex_string: str):
    return int(hex_string.lstrip('#'), 16)


@team_bot.command(aliases=['colors', 'listcolors'])
async def list_colors(ctx: commands.Context):
    await ctx.reply("(colors go here)")


@team_bot.command(aliases=['tc', 'teamcolor'])
async def team_color(ctx: commands.Context, *args):
    team_role = get_current_team_role(ctx.author)
    if team_role is not None:
        color_string = "_".join(args).lower()
        if color_string.startswith("#"):
            color_value = get_color(color_string)
        else:
            if color_string in colors:
                color_value = get_color(colors[color_string])
            else:
                await ctx.reply("That is not a valid color! *Type `!colors` for a list of colors...*")
                return
        await team_role.edit(color=discord.Color(value=color_value))

        embed = discord.Embed(
            color=color_value,
            description=f"Set role color of {team_role.name} to {color_string}"
        )
        await ctx.channel.send(embed=embed)
    else:
        await ctx.reply("You aren't part a team")


# !init command
@team_bot.command()
@commands.has_permissions(manage_guild=True)
async def init(ctx: commands.Context):
    guild: discord.Guild = ctx.guild

    spam_channel = get_spam_channel(guild)
    if spam_channel is None:
        await guild.create_text_channel(name=spam_channel_name, category=get_text_category(guild))

    for team_name in team_names:
        print(f'[{team_name}]')
        await create_team(guild, team_name)
        print()

    await ctx.reply(f"Created teams! Please use <#{get_spam_channel(guild).id}> for further commands...")

    await spam_channel.send(embed=help_embed)


# !team command
@team_bot.command(aliases=['t'])
async def team(ctx: commands.Context, *args):
    member: discord.Member = ctx.author
    guild: discord.Guild = ctx.guild

    team_name = get_role_name(" ".join(args))

    current_team_role = get_current_team_role(member)
    new_role = get_role(guild, team_name)
    if new_role is not None:
        if new_role not in member.roles:
            text_channel = get_text_channel(guild, team_name)
            if current_team_role is not None:
                await member.remove_roles(current_team_role)
                await ctx.reply(f"Switched from {current_team_role.name} to <#{text_channel.id}>!")
            else:
                await ctx.reply(f"Added to team <#{text_channel.id}>!")
            await member.add_roles(new_role)
        else:
            await ctx.reply("Already part of that team!")
    else:
        await ctx.reply("That team doesn't exist!")


# Load auth token from 'auth.json'
auth = io_util.load_json('auth.json')

# Run Ori using the auth token object
team_bot.run(auth['token'])
