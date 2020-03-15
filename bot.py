import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='y!')

names = ['Yua', 'ゆあ', '結愛']

#events
@bot.event
async def on_ready():
	print(f'{bot.user.name} woke up!')

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return

	#respond to being called
	for name in names:
		if name.lower() in message.content.lower():
			await message.channel.send('Did you call me {.author.mention}?'.format(message))

	await bot.process_commands(message)

#commands
@bot.command(name='jiko', help='Introduces herself')
async def jikoshoukai(ctx):
	await ctx.send('I am {}\nNice to meet you!'.format(bot.user.name))

@bot.command(name='quiz', help='To play those sweet quizzes!')
async def quiz(ctx, *args):
	desc = "poke_g1, poke_g2, poke_g3, poke_g4, poke_g5"
	embed = discord.Embed(title="**Yua's quizzes**", color=0x9b1c31)
	embed.add_field(name=":flag_jp:", value=desc, inline=False)
	await ctx.send(embed=embed)

bot.run(TOKEN)