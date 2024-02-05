import discord
from discord.ext import commands
import time
import datetime
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tracemalloc
import os
import sys

from extras import token, serverID, channelID, pc_mac

tracemalloc.start()

# token = 'discord bot token'
# serverID = 'Server to log to'
# channelID = 'channel to log to'
# pc_mac = 'MAC address of the PC'

botlog = "enter name of log channel here"

def log_prints(data):
    f = open("output.txt", "a") # Open file in append mode
    f.write(data + "\n") # Write message to file
    print(data) # Print message to console
    f.close() # Close file in append mode

log_prints(f"====================={datetime.datetime.now().strftime('%d/%m/%Y')}=====================")

# Discord client initialization
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
prefix = "PCWaker!"
bot = commands.Bot(intents=intents, activity=discord.Activity(type=discord.ActivityType.watching, name="if you're back home or not to open the pc for you, you lazy fuck"), status=discord.Status.idle, command_prefix = prefix)
ran = 0

@bot.event # Event that runs when the bot connects to Discord
async def on_ready():
    print_time('Bot connected to Discord as {0.user}'.format(bot))
    await logConnection(True)
    global ran

    if ran == 0:
        try:
            command = ['python3', 'PCWaker.py']
            subprocess.Popen(command)
            print_time("Ran PCWaker.py successfully")
            ran = 1
        except Exception as e:
            print_time("Failed to run PCWaker.py")
            print_time(e)
    try:
        synced = await bot.tree.sync()
        print_time(f"Synced {len(synced)} channels")
    except Exception as e:
        print_time(e)

# Log Channel Connection for sending messages
async def logConnection(startup):
    # Log channel ID
    server = bot.get_guild(serverID)
    if server is None:
        print_time("Server not found")
        return
    if startup:
        print_time("Server found at {} with ID {}".format(str(server.name), str(server.id)))

    # Get the log channel
    logChannel = discord.utils.get(server.text_channels, name=botlog)
    if logChannel is None:
        print_time("Log channel not found")
        return
    if startup:
        print_time("Log channel found at {} with ID {}".format(str(logChannel.name), str(logChannel.id)))

        # Send a message to the log channel
        await logChannel.send("[{0}]: Bot connected to Discord as {1.user}".format(time.strftime('%H:%M:%S', time.localtime()), bot))

    return logChannel

async def say(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(message, ephemeral=True)

# Command to restart the python program within discord
@bot.tree.command(name="restart", description="Restarts the bot")
async def jrestart(self):
    await say(self, "Restarting...")
    print_time("Restarting...")
    restart_program()

def restart_program():
    #find and kill PCWaker.py using "ps -ef | grep PCWaker.py | grep -v grep | awk '{print $2}' | xargs -r kill -9"
    psef = subprocess.Popen(["ps", "-ef"], stdout=subprocess.PIPE)
    grepwaker = subprocess.Popen(["grep", "PCWaker.py"], stdin=psef.stdout, stdout=subprocess.PIPE)
    grepv = subprocess.Popen(["grep", "-v", "grep"], stdin=grepwaker.stdout, stdout=subprocess.PIPE)
    awk = subprocess.Popen(["awk", "{print $2}"], stdin=grepv.stdout, stdout=subprocess.PIPE)
    xargs = subprocess.Popen(["xargs", "-r", "kill", "-9"], stdin=awk.stdout, stdout=subprocess.PIPE)
    psef.stdout.close()
    grepwaker.stdout.close()
    grepv.stdout.close()
    awk.stdout.close()
    xargs.stdout.close()

    #restart PCWaker.py
    python = sys.executable
    os.execl(python, python, *sys.argv)

# Shows the contents of the skip.txt file
@bot.tree.command(name="skip", description="Shows the contents of the skip.txt file")
async def skip(self):
    f = open("logs/skip.txt", "r")
    skip = f.read()
    f.close()
    await say(self, skip)

# Command that allows the user to skip the next n amount of days to wake the pc on, writes the number to a file called "skip.txt"
@bot.tree.command(name="skipset", description="Adds n amount of days to skip")
async def skipadd(self, days: int):
    try:
        if days < 0:
            await say(self, "Days cannot be less than 0")
            return

        f = open("logs/skip.txt", "w")
        counter = 0
        end_date = datetime.datetime.now()
        while counter < days:
            end_date += datetime.timedelta(days=1)
            if end_date.weekday() < 5:  # 0-4 denotes Monday to Friday
                counter += 1

        f.write(end_date.strftime('%d/%m/%Y'))
        f.close()
        weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
        today = datetime.datetime.now().strftime('%A')
        try:
            # find what index today is in weekdays
            today_index = weekdays.index(today)
        except:
            # if error then today is friday or saturday, so start the index from 0
            today_index = 0
        # print the next n days to skip including today
        skipdays = ""
        for i in range(today_index, today_index + days):#
            skipdays += weekdays[i % 5] + ", "
        # remove the final comma and space from the string
        skipdays = skipdays[:-2]
        await say(self, f"[{time.strftime('%H:%M:%S', time.localtime())}]: Skipping the next {days} days: {skipdays}")
        print_time(f"Skipping the next {days} days: {skipdays}")
    # if not an integer
    except Exception as e:
        await say(self, e)

async def sendMessage(message):
    timelog = f"[{time.strftime('%H:%M:%S', time.localtime())}]: "
    log_channel = await logConnection(False)  # Wait for logConnection coroutine to complete
    await log_channel.send(f"{timelog}{message}")


##################################### Getting and sending log files based on commands #####################################

@bot.tree.command(name = "wake", description="Manually sends a WOL packet to the pc to wake it up if PC is closed.")
async def wake_pc(interaction: discord.Interaction):
    subprocess.call(['wakeonlan', pc_mac])
    await say(interaction, "Waking up the PC...")
    print_time("Manually Waking up the PC...")

@bot.tree.command(name = "sleeping", description="Checks the sleeping status of the bot")
async def get_sleeping(interaction: discord.Interaction):
    f = open("logs/sleeping.txt", "r")
    sleeping = f.read()
    f.close()
    await say(interaction, sleeping)

@bot.tree.command(name = "status", description="Checks the pc/phone status of the bot")
async def get_status(interaction: discord.Interaction):
    f = open("logs/status.txt", "r", encoding="utf-8")
    status = f.read()
    f.close()
    await say(interaction, status)

@bot.tree.command(name = "wol", description="Checks the WOL status of the bot")
async def get_wol(interaction: discord.Interaction):
    f = open("logs/wol.txt", "r")
    wol = f.read()
    f.close()
    await say(interaction, wol)

class FileChangeHandler(FileSystemEventHandler):
    wol_sent = False
    sleeping_sent = False

    def __init__(self, bot):
        self.bot = bot

    def on_modified(self, event):
        channel = self.bot.get_channel(channelID)
        if channel is None:
            print_time("Channel not found.")
            return
        # if wol.txt changed
        if not event.is_directory and event.src_path.endswith('wol.txt') and not self.wol_sent:
            with open(event.src_path, 'r') as file:
                contents = file.read()
            print_time("wol.txt has been modified")
            self.bot.loop.create_task(channel.send(contents))

            self.wol_sent = True
        else:
            self.wol_sent = False

        #if sleeping.txt changed
        if not event.is_directory and event.src_path.endswith('sleeping.txt') and not self.sleeping_sent:
            with open(event.src_path, 'r') as file:
                contents = file.read()
            print_time("sleeping.txt has been modified")
            self.bot.loop.create_task(channel.send(contents))

            self.sleeping_sent = True
        else:
            self.sleeping_sent = False

def start_observer(bot):
    path = os.path.join(".", "logs")
    observer = Observer()
    event_handler = FileChangeHandler(bot)
    observer.schedule(event_handler, path, recursive=False)
    try:
        observer.start()
        print_time(path + " is being watched")
    except Exception as e:
        print_time("Error started observer: " + e)
        pass

def print_time(message):
    log_prints(f"[{datetime.datetime.now().strftime('%H:%M:%S')}]: {message}")

start_observer(bot)
bot.run(token)
