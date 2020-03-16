import os
from dotenv import load_dotenv
import json
import random

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='y!')

names = ['Yua', 'ゆあ', '結愛']
curr_data = {}

#helper functions
def load_json(filename):
	with open(filename+'.json') as f:
		curr_data = json.load(f)

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
	if len(args) == 0:
		desc = "poke_g1, poke_g2, poke_g3, poke_g4, poke_g5"
		embed = discord.Embed(title="**Yua's quizzes**", color=0x9b1c31)
		embed.add_field(name=":flag_jp:", value=desc, inline=False)
		await ctx.send(embed=embed)
	elif args[0] == "poke_g1":
		#gen1 quiz
		num_q = 15
		load_json('poke_g1')
		info_msg = 'Starting Pokemon Generation 1 Quiz\nFirst to {} points wins\n{}'.format(num_q, str(curr_data["description"]))
		await ctx.send(info_msg)
		deck = curr_data["deck"]
		for i in range(5):
			index = randint(0, 150)
			embed = discord.Embed(title='**' + deck[index]["comment"] + '**', color=0x0)
			embed.add_field(name=deck[index]["answer"][0], value=deck[index]["answer"][1])
			embed.set_thumbnail(url=deck[index]["question"])
			await ctx.send(embed=embed)

	else:
		await ctx.send('No no {.author.mention}, you need to choose one from the available quizzes!'.format(ctx.message))

bot.run(TOKEN)