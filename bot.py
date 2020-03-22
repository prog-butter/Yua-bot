import os
from dotenv import load_dotenv
import json
import random
from colour import Color
import time
import asyncio
from json.decoder import JSONDecodeError

import discord
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='y!')

#global vars
TIMEOUT_EMOJI = ':alarm_clock:'
CORRECT_ANSWER = ':o:'
SKIPPED_QUESTION = ':fast_forward:'

names = ['Yua', 'ゆあ', '結愛']

curr_quiz_data = {}
available_quizzes = ["poke_g1", "poke_g2", "poke_g3", "poke_g4", "poke_g5", "poke_g6", "poke_g7", "poke_g8"]
quiz_should_run = True

DEF_TIMEOUT_TIME = 15.0
DEF_TIME_AFTER_ANSWER = 1.0 #how much more time to give after one player answers correctly

#helper functions
def load_quiz_json(filename):
	with open(filename) as f:
		global curr_quiz_data
		curr_quiz_data = json.load(f)

def darkenColor(hex):
	c = Color('#'+hex)
	c.luminance -= 0.2
	return c

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
		desc = ''
		for q in available_quizzes:
			desc += '{} '.format(q)
		embed_info = discord.Embed(title="**Yua's quizzes**", color=0x9b1c31)
		embed_info.add_field(name=":flag_jp:", value=desc, inline=False)
		await ctx.send(embed=embed_info)
	elif args[0] in available_quizzes:
		#gen1 quiz
		participants = {} #keep track of player score
		already_answered = {} #to prevent from answering multiple times
		global quiz_should_run
		quiz_should_run = True
		num_q_to_ask = 10
		if len(args) > 1:
			num_q_to_ask = int(args[1])
		total_q_asked = 0
		load_quiz_json(args[0]+'.json')
		info_msg = 'Starting Pokemon Generation {} Quiz\nFirst to {} points wins\n{}'.format(args[0][-1], num_q_to_ask, curr_quiz_data['description'])
		print('Starting Pokemon Generation {} Quiz'.format(args[0][-1]))
		await ctx.send(info_msg)
		deck = curr_quiz_data['deck']
		while quiz_should_run:
			#stuff
			already_answered = {}
			#generate qestion
			total_q = len(curr_quiz_data['deck'])
			index = random.randint(0, total_q-1)
			embed_q = discord.Embed(title='**' + deck[index]['id'] + '**', color=discord.Colour(int(darkenColor(deck[index]['type']).hex[1:], 16)))
			#embed_q.add_field(name=deck[index]['answers'][0], value=deck[index]['answers'][1])
			embed_q.set_thumbnail(url=deck[index]['question'])
			await ctx.send(embed=embed_q)
			total_q_asked += 1

			#wait for answer
			q_answered = False
			time_left = DEF_TIMEOUT_TIME
			while time_left > 0:
				q_start_time = time.monotonic()
				try:
					ans = await bot.wait_for('message', timeout=time_left)
				except asyncio.TimeoutError:
					#add to review list

					#show timeout message
					time_left = 0
					if q_answered == False and quiz_should_run:
						embed_to = discord.Embed(title=TIMEOUT_EMOJI+' **Timed out**', color=discord.Colour.red())
						embed_to.add_field(name=deck[index]['answers'][0], value=deck[index]['answers'][1])
						await ctx.send(embed=embed_to)
				else:
					#received a message
					if ans.content.lower() == 'stop!': #stop the quiz
						time_left = 0
						quiz_should_run = False
						continue
					if ans.content.lower() == '..': #skip this question
						time_left = 0.1
						embed_skip = discord.Embed(title=SKIPPED_QUESTION+' **Skipped**', color=discord.Colour.dark_blue())
						embed_skip.add_field(name=deck[index]['answers'][0], value=deck[index]['answers'][1])
						await ctx.send(embed=embed_skip)
					#received an answer
					for answer in deck[index]['answers']:
						if ans.content.lower() == answer.lower(): #change to lowercase before check
							#correct answer - give points
							print('Gave a point to {}'.format(ans.author))
							author_name = str(ans.author)
							if author_name not in already_answered:
								already_answered[author_name] = 1 #answered this question
								if author_name not in participants:
									participants[author_name] = 1 #add it
								else:
									participants[author_name] += 1 #update score
								q_answered = True
							time_left = DEF_TIME_AFTER_ANSWER
					if q_answered == False:
							#received answer was wrong
							new_time = time.monotonic()
							elapsed = new_time - q_start_time
							time_left -= elapsed

			#correct answer
			if q_answered:
				embed_ca = discord.Embed(title=CORRECT_ANSWER+' **Correct**', color=discord.Colour.dark_green())
				embed_ca.add_field(name=deck[index]['answers'][0], value=deck[index]['answers'][1], inline=False)
				temp_val = ''
				for part in participants:
					temp_val += ('**{}** {}p '.format(part[:part.index('#')], participants[part]))
				embed_ca.add_field(name='Scorers - {} to {}'.format(args[0], num_q_to_ask), value=temp_val)
				await ctx.send(embed=embed_ca)

			#check if quiz is over or not
			if len(participants) > 0:
				max_points = max(participants, key=participants.get)
				if participants[max_points] >= num_q_to_ask:
					quiz_should_run = False

		#final results of current quiz
		embed_res = discord.Embed(title='Final Scoreboard: {}'.format(args[0]), description='-------------------------------', color=0x0)
		player_str = ''
		for part in participants:
			player_str += ('**{}** {}p\n'.format(part[:part.index('#')], participants[part]))
		if player_str == '':
			player_str = 'No participants'
		embed_res.add_field(name='Participants (Questions asked: {})'.format(total_q_asked), value=player_str)
		await ctx.send(embed=embed_res)
		#update and display leaderboards
		lb = {}
		#create lb file if doesn't exist
		if (os.path.exists(args[0]+'_lb.json')) is False:
			with open(args[0]+'_lb.json', 'w') as f:
				pass

		with open(args[0]+'_lb.json', 'r') as f:
			try:
				lb = json.load(f)
			except JSONDecodeError:
				pass
			for part in participants:
				if part not in lb: #player scored for the first time in this quiz
					lb[part] = participants[part]
				else:
					lb[part] += participants[part]
		with open(args[0]+'_lb.json', 'w') as f:
			json.dump(lb, f)

		embed_lb = discord.Embed(title='Leaderboard for {}'.format(args[0]), color=0xffdf00)
		top_ten = []
		orig_lb = lb.copy()
		for player in lb:
			keyToDel = max(lb, key=lb.get)
			top_ten.append(keyToDel)
			lb[keyToDel] = 0
		for i in range(min(len(top_ten), 10)):
			if (i+1) % 4 != 0:
				embed_lb.add_field(name='{}. {}'.format(i+1, top_ten[i]), value=orig_lb[top_ten[i]], inline=True)
			else:
				embed_lb.add_field(name='{}. {}'.format(i+1, top_ten[i]), value=orig_lb[top_ten[i]], inline=False)
		await ctx.send(embed=embed_lb)

	else:
		await ctx.send('No no {.author.mention}, you need to choose one from the available quizzes!'.format(ctx.message))

bot.run(TOKEN)