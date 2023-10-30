import os
import discord
import typing
import asyncio
import datetime
import random
import json
import random
import urllib
import ssl
from urllib import parse
from discord.ext import commands
from discord.interactions import Interaction
from IdList import IdList
from UserDataList import UserDataList
from datetime import datetime, timedelta, time
from discord import ui, Interaction, SelectOption, Message, ButtonStyle
from BigSong import BigSong
from BigMTGCard import BigMTGCard
from BigCoin import BigCoin
from discord.utils import get


#swap from normal running to test mode
IS_TESTING = False

#a schedule which detemines what type of day we are performing
#0 for a regular fact and vid day, 1 for a quiz day, and 2 for a post quiz day 
WEEKLY_SCHEDULE = [0, 0, 0, 0, 0, 1, 2]

#same as rgular schedule but for testing mode
WEEKLY_TEST_SCHEDULE = [0, 0, 1, 3, 3, 3, 2]

# Your Discord bot token
TOKEN = 'MTA1MzI1NDQ4NzQ3ODkxMTAyNg.G-y-w0.3Bh_Zux_EjCw7cjUs1tNu7T2xNH6IkozQnzAIE'
TENOR_KEY = 'AIzaSyDazK_T__grZUtsaO6K13K9iXz2sFvWWsI'

# Your Discord bot client
#client = discord.Client(command_prefix = "!", intents=discord.Intents.all())
client = commands.Bot(command_prefix = "!", intents=discord.Intents.all())

#Guild
MAIN_SERVER = 1046477059523874957 #GOOBERS
TEST_SERVER = 1087993781317537832 #BOF Test Server
SERVER = None #Server to be updated based on if we are in testing mode

#leaderboard channels
LEADERBOARD_CHANNEL_MAIN = 1089128661434781816 #GOOBERS
LEADERBOARD_CHANNEL_TEST = 1087994033000939600 #BOF Test Server
LEADERBOARD_CHANNEL = None #channel to be updated based on if we are in testing mode

LEADERBOARD_MESSAGE_MAIN = 1089142709819822175 #GOOBERS
LEADERBOARD_MESSAGE_TEST = 1089010733582393365 #BOF Test Server
LEADERBOARD_MESSAGE = None #message id to be updated based on if we are in testing mode

#post channels
BOF_MAIN_CHANNEL = 1081553625358290965 #GOOBERS
BOF_TEST_CHANNEL = 1087993904743333940 #BOF Test Server
BOF_CHANNEL = None #channel to be updated based on if we are in testing mode

MAIN_BIG_ROLE = 1089128958563467334 #GOOBERS
TEST_BIG_ROLE = 1088193796837212211 #BOF Test Server
BIG_ROLE = None #role to be updated based on if we are in testing mode

# Path to the text file containing the facts
FACTS_FILE = 'facts.txt'
VIDEOS_FILE = 'videos.txt'
QUIZZES_FILE = 'quizzes.txt'
FOODS_FILE = 'foods.txt'
BIG_FILE = 'big.txt'

#role for winning the quiz
SPECIAL_ROLE_NAME = "Big King"

winner_list = None
stats_list = None

#dictates what periods of time someone can vote on quizes
can_vote = False

amog_mode = False
ssl_contex = None

#data that holds the integer id of the current quiz message
quiz_message_id = None
correct_answer = None
winner_id = None

food_list = None
big_list = None


#/////////////////////////////////////////////////////////////////////////////////////////////////////////
#/////////////////////////////////////////////////////////////////////////////////////////////////////////
#large method for detemining day and then running the corect action for that day looping untill turned off
async def run_days():
    await client.wait_until_ready()
    weekday = 0
    temp = False
    print(can_vote)
    while True:
        
        
        await update_scoreboard()
        #if not testing waits untill 8 am
        if not IS_TESTING:
            if temp:
                await asyncio.sleep(time_until('08:00:00'))
            else:
                temp = True
        else:
            await asyncio.sleep(10) #if testing waits 10 seconds
        
        #if not testing sets the weekday
        if not IS_TESTING:
            now = datetime.now()
            weekday = now.weekday()
            print(weekday)
        else:
            weekday = weekday + 1 #if testing increments weekday

        #seting they day type of this day to detirmine if its a fact, quiz, or post-quiz day
        day_type = -1
        if not IS_TESTING:
            day_type = WEEKLY_SCHEDULE[weekday]
        else:
            day_type = WEEKLY_TEST_SCHEDULE[weekday - 1] #test version

        #checking daytype and running the related method
        if day_type == 0:
            #run fact
            await fact_day()
        elif day_type == 1:
            #run quiz
            await quiz_day()
        elif day_type == 2:
            #run post quiz
            await post_quiz_day()
        elif day_type == 3:
            await postq_quizday()

        if IS_TESTING and weekday >= 7:
            weekday = 0

async def fact_day():

    #picking out a random fact
    facts = read_facts()
    fact = random.choice(facts)
    while(fact == ''):
        fact = random.choice(facts)

    #picking out a random video
    videos = read_videos()
    video = random.choice(videos)
    while(video == ''):
        video = random.choice(videos)
        
    #sending fact and video to channel
    await BOF_CHANNEL.send(':small_blue_diamond:**Big One Fact of the Day**:small_blue_diamond:**:** ' + fact)
    await BOF_CHANNEL.send(':small_blue_diamond:**Big One Video of the Day**:small_blue_diamond:**:** ' + video)


    #if not testing fact/video are removed so they are not picked again
    if not IS_TESTING:
        facts.remove(fact)
        write_facts(facts)
        videos.remove(video)
        write_videos(videos)

async def quiz_day():
    global quiz_message_id, correct_answer, can_vote

    await BOF_CHANNEL.send(':green_circle: **Big One Quiz at 3pm** :green_circle: Check Leaderboard for more information.')

    #sleeping till 2:59pm unless testing
    if not IS_TESTING:
        await asyncio.sleep(time_until('14:59:00'))
    else:
        await asyncio.sleep(3)
    
    await BOF_CHANNEL.send(':yellow_circle: **Big One Quiz in 1 Minute!** :yellow_circle:')

    #sleeping till 3:00pm unless testing
    if not IS_TESTING:
        await asyncio.sleep(time_until('15:00:00'))
    else:
        await asyncio.sleep(1)

    #picking a random quiz from the quiz txt and then spliting it around the '|' charector
    #EX: Example Quiz|Answer A|Answer B|Answer C|Answer D|B
    quizzes = read_quizzes()
    rando_quiz = random.choice(quizzes)
    quiz = rando_quiz.strip()
    question, answer_a, answer_b, answer_c, answer_d, correct = quiz.split('|')

    if not IS_TESTING:
        quizzes.remove(rando_quiz)
        write_quizzes(quizzes)

    #sends fact and saves its id to the global quiz_message_id variable
    quiz_message_id = (await BOF_CHANNEL.send(f":red_circle: **Big One Quiz!** :red_circle:\n{question}\n\nA: {answer_a}\nB: {answer_b}\nC: {answer_c}\nD: {answer_d}")).id
    correct_answer = correct

    #saving data in case program is stopped early
    save_extra_quiz_data('quiz_message_id', quiz_message_id)
    save_extra_quiz_data('correct_answer', correct_answer)    

    #fetchs the quiz message from the id and adds the emojis people will use to answer with
    quiz_message = await BOF_CHANNEL.fetch_message(quiz_message_id)
    for emoji in ('🇦', '🇧', '🇨', '🇩'):
        await quiz_message.add_reaction(emoji)

    can_vote = True
    save_extra_quiz_data('can_vote', can_vote)

async def post_quiz_day():
    global winner_list, stats_list, winner_id, can_vote

    can_vote = False
    save_extra_quiz_data('can_vote', can_vote)

    await remove_winner_role()

    await BOF_CHANNEL.send(f":red_circle: **Quiz Results** :red_circle:\nThe correct answer is: {correct_answer}")
    
    if winner_list.get_size() > 0:
        #grabs the first id from winner_list gets the user corresponding to it and retrives their username
        winner_id = winner_list.get_first()
        save_extra_quiz_data('winner_id', winner_id)
        
        #checking if winner has a nickname if not it uses their regular name
        member = SERVER.get_member(winner_id)
        name = None
        if member.nick is None:
            name = member.display_name
        else:
            name = member.nick

        await BOF_CHANNEL.send(f"The first person who is still picking the correct answer is: {name}")
        #gets rid of the first winner
        winner_list.remove_id(winner_list.get_first())

        #gives the speedy winner their role
        await assign_winner_role()
    else:
        await BOF_CHANNEL.send("There were no winners you sussy bakas.")

    #checking to see if there are other winners
    if winner_list.get_size() > 0:
        await BOF_CHANNEL.send(f"Other winners:")
    
        #removing remaining winners from the list
        while winner_list.get_size() > 0:
            #checking if winner has a nickname if not it uses their regular name
            member = SERVER.get_member(winner_list.get_first())
            name = None
            if member.nick is None:
                name = member.display_name
            else:
                name = member.nick

            await BOF_CHANNEL.send(f" {name}")
            winner_list.remove_id(winner_list.get_first())

    emojis = ['🇦', '🇧', '🇨', '🇩']

    #a conversion guide so the weird emoji is converted into a regular charector
    emoji_to_letter = {
        '🇦': 'A',
        '🇧': 'B',
        '🇨': 'C',
        '🇩': 'D',
    }

    quiz_message = await BOF_CHANNEL.fetch_message(quiz_message_id)
    #checking for only the allowed reactions
    for reaction in quiz_message.reactions:
        if reaction.emoji in emojis:
            #grabbing all the users who reacted to this emoji who is not the bot and putting them in a list
            users = [user async for user in reaction.users() if user != client.user]
            #comparing if the answer is correct
            if emoji_to_letter[str(reaction.emoji)] == correct_answer:
                #if correct it edits the users stats to have 1 more win coin and play. If they are not on the list they get added
                for user in users:
                    if stats_list.find_user(user.id) == None:
                        stats_list.add_user(user.id)

                    current_user = stats_list.find_user(user.id)
                    stats_list.update_user(user.id, wins=current_user["wins"] + 1, coins=current_user["coins"] + 1, plays=current_user["plays"] + 1)
            else:
                #if incorect answer it only adds to the plays
                for user in users:
                    if stats_list.find_user(user.id) == None:
                        stats_list.add_user(user.id)

                    current_user = stats_list.find_user(user.id)
                    stats_list.update_user(user.id, plays=current_user["plays"] + 1)

    await update_scoreboard()
    await fact_day()

async def postq_quizday():
    await post_quiz_day()
    await quiz_day()

async def update_scoreboard():
    
    sorted_users = sorted(stats_list.data["users"], key=lambda user: user['wins'], reverse=True)
    user_strings = []
    for i, user in enumerate(sorted_users, start=1):
        
        member = SERVER.get_member(user['id'])
        name = None
        if member.nick is None:
            name = member.display_name
        else:
            name = member.nick
        user_strings.append(f"{i}. {name} - {user['wins']} wins, {user['coins']} coins, {user['plays']} plays")
    leaderboard = "\n".join(user_strings)

    leaderboard_text = "**Quiz Explanation**\n"
    leaderboard_text += "Every Saturday, a quiz will be held at 3pm. Participants can react to the quiz message with their answer. The first person to answer correctly and is still picking said answer when the quiz ends will be awarded the Big King role. All other correct answers will award participants one win and one BigCoin. The correct answer will be revealed every Sunday. NOTE: The bot will remove extra answers, so don't quickly change between answers or yours might not be counted\n\n"
    leaderboard_text += "**Big King Role**\n"
    leaderboard_text += "The Big King role is a special role awarded to the first person who is still curently picking the correct answer. The role is held for one week, until the next quiz winner is determined.\n\n"
    leaderboard_text += "**BigCoin**\n"
    leaderboard_text += "BigCoin is a currency which can be currently traded for 1 of 3 things.\n1. 1 BigCoin can be traded for 1 USD.\n2. 5 BigCoin can be traded for a custom MTG Big One card.\n3. 10 BigCoin Can be traded for a Big One music video on the song of your choice.\n"
    leaderboard_text += "To puchase these items use the command *\"/request <choice>\"*\nBigCoin can also be traded between players with the command *\"/pay <member_mention> <amount>\"*\n\n"
    leaderboard_text += "**Leaderboard**\n"
    leaderboard_text += "The leaderboard displays the number of quiz wins and coins for each participant. It is sorted by the number of wins and then by the number of coins.\n\n"
    leaderboard_text += "```"
    leaderboard_text += leaderboard
    leaderboard_text += "```"

    leaderboard_message = await LEADERBOARD_CHANNEL.fetch_message(LEADERBOARD_MESSAGE)
    await leaderboard_message.edit(content=leaderboard_text)       

async def assign_winner_role():
    role = discord.utils.get(SERVER.roles, name=SPECIAL_ROLE_NAME)

    member = SERVER.get_member(winner_id)
    print(member)
    if member is not None:
        await member.add_roles(role)

async def remove_winner_role():
    role = discord.utils.get(SERVER.roles, name=SPECIAL_ROLE_NAME)
    if role is not None:
        print('role is not none')
        print(winner_id)
        member = SERVER.get_member(winner_id)
        if member is not None:
            print('member is not none')
            if member.get_role(BIG_ROLE) is not None: #big king role id
                print('member having role is not none')
                await member.remove_roles(role)

#method that saves extra quiz data (currently 'quiz_message_id', 'winner_id, 'correct_answer', 'and can_vote') to the quizData json
def save_extra_quiz_data(key, value):
    try:
        with open('quizData.json', 'r') as f:
            data = json.load(f)

        data[key] = value

        #print(f"Data before writing to file: {data}")  # Debugging print

        with open('quizData.json', 'w') as f:
            json.dump(data, f)

        #print(f"Data after writing to file: {data}")  # Debugging print

    except Exception as e:
        print(f"An error occurred: {e}")

#method that loads extra quiz data (currently 'quiz_message_id', 'winner_id, 'correct_answer', and 'can_vote') from the quizData json
def load_extra_quiz_data(key):
    with open('quizData.json', 'r') as f:
        data = json.load(f)

    value = data.get(key)
    #print(value)
    return value

# Function to read foods from a text file
def read_foods():
    with open(FOODS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]
    
# Function to read big synoms from a text file
def read_big():
    with open(BIG_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Function to read facts from a text file
def read_facts():
    with open(FACTS_FILE, 'r') as f:
        return f.readlines()

# Function to write facts to a text file
def write_facts(facts):
    with open(FACTS_FILE, 'w') as f:
        for fact in facts:
            f.write(fact)  

# Function to read videos from a text file
def read_videos():
    with open(VIDEOS_FILE, 'r') as f:
        return f.readlines()

# Function to write videos to a text file
def write_videos(videos):
    with open(VIDEOS_FILE, 'w') as f:
        for video in videos:
            f.write(video)

# Function to read quizzes from a text file
def read_quizzes():
    with open(QUIZZES_FILE, 'r') as f:
        return f.readlines()
    
def write_quizzes(quizzes):
    with open(QUIZZES_FILE, 'w') as f:
        for quiz in quizzes:
            f.write(quiz)
#method that  takes a specified time as a string in the format 'HH:MM:SS' and calculates the time remaining until that time in seconds:
def time_until(target_time_str):
    target_time = datetime.strptime(target_time_str, '%H:%M:%S').time()
    now = datetime.now().time()

    target_datetime = datetime.combine(datetime.now().date(), target_time)
    now_datetime = datetime.combine(datetime.now().date(), now)

    if target_datetime <= now_datetime:
        target_datetime += timedelta(days=1)

    time_remaining = target_datetime - now_datetime
    return time_remaining.total_seconds()

#function that checks if the discord member in question ans a nickname and will return the nick, if not it will return their name
def returnNickOrName(member):
    if member.nick is None:
        return member.display_name
    else:
        return member.nick

@client.slash_command(description = "Trade BigCoin With Others!")
async def pay(ctx: discord.ApplicationContext, name : discord.Member, amount : int):

    if amount <= 0:
        await ctx.send_response("You cannot enter a amount that is less than or equal to 0.")
        return

    if stats_list.find_user(ctx.author.id) == None:
        stats_list.add_user(ctx.author.id)
    if stats_list.find_user(name.id) == None:
        stats_list.add_user(name.id)

    sender = stats_list.find_user(ctx.author.id)
    recipient = stats_list.find_user(name.id)

    if sender["coins"] < amount:
        await ctx.send_response(f"{returnNickOrName(ctx.author)} does not have enough coins!")
    else:
        stats_list.update_user(ctx.author.id, coins=sender["coins"] - amount)
        stats_list.update_user(name.id, coins=recipient["coins"] + amount)
        await ctx.send_response(f"{returnNickOrName(ctx.author)} payed {returnNickOrName(name)} {amount} coins!")

@pay.error
async def pay_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Not all of the parameters were in the command. Please use the format: !pay member amount")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member was unable to be found. Make sure members with spaces in their names are replaced with underscores. EX: Big_Jig.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Something besides a whole number was used when paying, the command does not work with formats such as: one, or 1.3")
    else:
       await ctx.send("unknown error") 

@client.slash_command(description = "Spend your Big Coins for prizes!")
async def request(ctx: discord.ApplicationContext, choice: discord.Option(str, "Pick your item", choices = ['Money', 'Custom Big One mtg card', 'Custom Big One music video'])):
        
        if stats_list.find_user(ctx.author.id) == None:
            stats_list.add_user(ctx.author.id)

        requester = stats_list.find_user(ctx.author.id)

        if choice == 'Custom Big One music video':
            if requester["coins"] < 10:
                await ctx.send_response("You have less than the ten coins needed for this option.")
                return
            Song = BigSong(client, title="Custom Big One Music Vid")
            await ctx.send_modal(Song)
            await Song.wait()

            if Song.iscallback == True:
                stats_list.update_user(ctx.author.id, coins=requester["coins"] - 10)
        elif choice == 'Custom Big One mtg card':
            if requester["coins"] < 5:
                await ctx.send_response("You have less than the five coins needed for this option.")
                return
            Card = BigMTGCard(client, title="Custom Big One MTG Card")
            await ctx.send_modal(Card)
            await Card.wait()

            if Card.iscallback == True:
                stats_list.update_user(ctx.author.id, coins=requester["coins"] - 5)
        elif choice == 'Money':
            Coin = BigCoin(client, requester["coins"], title="Trade BigCoin for USD")
            await ctx.send_modal(Coin)
            await Coin.wait()

            final_amount = int(Coin.amount)
            stats_list.update_user(ctx.author.id, coins=requester["coins"] - final_amount)
        await update_scoreboard()
            

#@request.error
async def request_error(ctx, error):
    print("e")

@client.slash_command(description = "Turns on amog mode!")
async def amog(ctx: discord.ApplicationContext):
    global amog_mode
    if not amog_mode:
        amog_mode = True
        await ctx.send_response("Amog mode activated")
        await get_gif(ctx)
    else:
        amog_mode = False
        await ctx.send_response("Amog mode deactivated")


async def get_gif(ctx: discord.ApplicationContext):
    url = "http://api.giphy.com/v1/gifs/random"

    params = parse.urlencode({
    "api_key": "Fm1HcQ5pO4zIrtTli7OyWsEq9LwoTsGC",
    "q": "among us",
     "rating": "g"
    })

    print("".join((url, "?", params)))
    with urllib.request.urlopen("https://api.giphy.com/v1/gifs/random?api_key=Fm1HcQ5pO4zIrtTli7OyWsEq9LwoTsGC&tag=among+us&rating=g", context=ssl_contex) as response:
        data = json.loads(response.read().decode('utf-8'))
    print(json.dumps(data, sort_keys=True, indent=4))
    gif_url = data['data']['embed_url']
    await ctx.send(gif_url)

@client.slash_command()
async def help(ctx: discord.ApplicationContext):

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name = 'Help')
    embed.add_field(name = '/pay', value ='Gives a specified amout of BigCoin to target user.', inline=False)
    embed.add_field(name = '/request', value ='Request for one of the BOF prizes described on the leaderboard. The correct amount of BigCoin is required for each option.', inline=False)
    embed.add_field(name = '/amog', value ='Turns on amog mode. Amog mode has a 1 in 10 chance to post a random among us gif when someone sends a message.', inline=False)
    embed.add_field(name = 'Extra info', value ='For any aditional info check the leaderboard channel.', inline=False)

    await ctx.send_response(embeds=[embed])
    

@client.event
async def on_message(message):
    
    if message.author != client.user:
        content = message.content

        if amog_mode:
            rand = random.randint(1, 10)
            if rand == 1:
                await get_gif(message.channel)

        for word in big_list:
            if word.lower() in content.lower():
                channel = message.channel
                await channel.send('Not as ' + word.lower() + ' as me!')
                break

        for word in food_list:
            if word.lower() in content.lower():
                print(word)
                emog = client.get_emoji(1128051289587204207)
                await message.add_reaction(emog)
                break
        print('done')

@client.event
async def on_reaction_add(reaction, user):
    global winner_list

    #a conversion guide so the weird emoji is converted into a regular charector
    emoji_to_letter = {
        '🇦': 'A',
        '🇧': 'B',
        '🇨': 'C',
        '🇩': 'D',
    }

    #checking if the react was on the right message, was not the bot, is one of the 4 emojis, and that it is voting time
    if reaction.message.id == quiz_message_id and user != client.user and str(reaction.emoji) in emoji_to_letter.keys() and can_vote:
            
        answer = emoji_to_letter[str(reaction.emoji)]

        #removing other answers that were chosen previously
        if not (answer == 'A'):
            await reaction.message.remove_reaction('🇦', user)
        if not (answer == 'B'):
            await reaction.message.remove_reaction('🇧', user)
        if not (answer == 'C'):
            await reaction.message.remove_reaction('🇨', user)
        if not (answer == 'D'):
            await reaction.message.remove_reaction('🇩', user)
        
        if answer == correct_answer:
            winner_list.add_id(user.id)
        else:
            winner_list.remove_id(user.id)
            
       

#runs on startup of bot
@client.event
async def on_ready():
    global SERVER, LEADERBOARD_CHANNEL, LEADERBOARD_MESSAGE, BOF_CHANNEL, BIG_ROLE, winner_list, stats_list, quiz_message_id, correct_answer, winner_id, food_list, big_list, can_vote, ssl_contex
    
    if not IS_TESTING:
        SERVER = client.get_guild(MAIN_SERVER)
        LEADERBOARD_CHANNEL = client.get_channel(LEADERBOARD_CHANNEL_MAIN)
        LEADERBOARD_MESSAGE = LEADERBOARD_MESSAGE_MAIN
        BOF_CHANNEL = client.get_channel(BOF_MAIN_CHANNEL)
        BIG_ROLE = MAIN_BIG_ROLE
    else:
        SERVER = client.get_guild(TEST_SERVER)
        LEADERBOARD_CHANNEL = client.get_channel(LEADERBOARD_CHANNEL_TEST)
        LEADERBOARD_MESSAGE = LEADERBOARD_MESSAGE_TEST
        BOF_CHANNEL = client.get_channel(BOF_TEST_CHANNEL)
        BIG_ROLE = TEST_BIG_ROLE

    food_list = read_foods()
    big_list = read_big()

    for word in food_list:
        print(word)

    winner_list = IdList('quizData.json')
    print(winner_list)
    stats_list = UserDataList('quizData.json')

    quiz_message_id = load_extra_quiz_data('quiz_message_id')
    correct_answer = load_extra_quiz_data('correct_answer')
    winner_id = load_extra_quiz_data('winner_id')
    can_vote = load_extra_quiz_data('can_vote')
    print(winner_id)
    print(quiz_message_id)

    #making sure bot only sets the canvote if its the right time
    weekday = 0
    #if not testing sets the weekday
    if not IS_TESTING:
        now = datetime.now()
        weekday = now.weekday()

        day_type = -1

        day_type = WEEKLY_SCHEDULE[weekday]

        target_time = datetime.strptime('08:00:00', '%H:%M:%S').time()
        now = datetime.now().time()

        target_datetime = datetime.combine(datetime.now().date(), target_time)
        now_datetime = datetime.combine(datetime.now().date(), now)

        print(can_vote)
        #checking the day and times setting false if its not a quizday or is a post quiz day before 8am
        #if day_type != 1 and day_type != 3:
        #    print('day not fact')
        #    if day_type == 2:
        #        print('day type is 2')
        #        if target_datetime <= now_datetime:
        #            print('after 8am')
        #            can_vote = False
            #else: can_vote = False
    else:
        can_vote = False

    ssl_contex = ssl._create_unverified_context()

    await client.sync_commands()
        
    print('Logged in as {0.user}'.format(client))
    await run_days()
    
client.run(TOKEN)