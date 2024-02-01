import subprocess
from ping3 import ping
import time
import datetime
from datetime import timedelta

from extras import pc_mac, pc_ip, phone_ip, time_ranges

## Time ranges for each day of the week to set status as "away" and wait for phone to connect to network to send WOL packet
#time_ranges = {
#    'Sunday' : [('00:00', '00:00')],
#    'Monday': [('00:00', '00:00')],
#    'Tuesday': [('00:00', '00:00')],
#    'Wednesday': [('00:00', '00:00')],
#    'Thursday': [('00:00', '00:00')]
#}

def log_prints(data):
    f = open("output.txt", "a") # Open file in append mode
    f.write(data + "\n") # Write message to file
    print(data) # Print message to console
    f.close()

# Check if the user wants to skip the next time range based on the skip.txt file
def check_if_skip():
    try:
        f = open("logs/skip.txt", "r")
    except FileNotFoundError:
        f = open("logs/skip.txt", "w")
        f.write("0")
        f.close()
        f = open("logs/skip.txt", "r")

    skip = f.read()
    f.close()
    if skip != "0":
        skip_date = datetime.datetime.strptime(skip, '%d/%m/%Y').date()  # Convert skip_date to datetime.date
        current_date = datetime.datetime.now().date()
        if skip_date >= current_date:
            print_time(f"Skipping until {skip_date.strftime('%d/%m/%Y')}...")
            log("sleeping", f"Skipping until {skip_date.strftime('%d/%m/%Y')}...")

            time_diff = (skip_date - current_date).days * 86400 - datetime.datetime.now().timestamp() % 86400
            time.sleep(time_diff)  # Sleep until skip_date
            f = open("logs/skip.txt", "w")
            f.write("0")
            f.close()
            log("sleeping", "Finished skipping")
            print_time("Finished skipping")
    return

# Run command to send Wake-on-LAN magic packet
def send_wol_packet(mac_address):
    print_time("Phone is connected.")
    subprocess.call(['wakeonlan', mac_address])
    print_time("Sent WOL packet to PC.")
    print_time("Welcome home!")
    log("wol", "Sent WOL packet to the PC. Welcome home cunt")
    log_status_true()
    return

# Check if phone is connected to the network
def is_phone_connected():
    if ping(phone_ip[0]) or ping(phone_ip[1]): # Check if phone is connected to either the 5G or the 2.4G of Raheem
        return True
    else:
        return False

def is_pc_closed():
    if ping(pc_ip):
        return False # PC is open move to sleep till next time start
    else:
        return True # PC is closed move to check if phone is connected

def next_time_start():
    # if today is thursday then get the first time range of sunday, otherwise get the first time range of the next day
    if datetime.datetime.now().strftime('%A') == 'Thursday':
        next_time = datetime.datetime.strptime(time_ranges['Sunday'][0][0],'%H:%M')
        next_datetime = (datetime.datetime.now() + timedelta(days=3)).replace(hour=next_time.hour, minute=next_time.minute, second=00, microsecond=00)
    else:
        next_time = datetime.datetime.strptime(time_ranges[(datetime.datetime.now() + timedelta(days=1)).strftime('%A')][0][0],'%H:%M')
        next_datetime = (datetime.datetime.now() + timedelta(days=1)).replace(hour=next_time.hour, minute=next_time.minute, second=00, microsecond=00)
    current_datetime = datetime.datetime.now()
    time_diff = (next_datetime - current_datetime).total_seconds()

    return time_diff

def check_if_away():
    current_day = time.strftime('%A')
    current_time = time.strftime('%H:%M')

    if current_day in time_ranges:
        for time_range in time_ranges[current_day]:
            start_time, end_time = time_range
            if start_time <= current_time <= end_time:
                return True  # Away
    else:
        print_time("Master is at home.")
        return False  # Not Away

# Check
def checking():
    time.sleep(15) # Check every 15 seconds if away
    if is_pc_closed():
        # every 30 minutes, print "Checking if phone is connected.", with out distupting the rest of the code
        if datetime.datetime.now().strftime('%M') in ['00', '30']:
            print_time("Checking if phone is connected.")
        if is_phone_connected(): # If within time range + PC not open + Phone connected, send WOL packet
            send_wol_packet(pc_mac)
            # After opening, sleep till the next time range is reached
            sleeping()
            log("wol", "Starting to look for phone again...")
    else: # If PC is already open within the time range, sleep till next time start
        log("wol", "PC is already open.")
        print_time("PC is already open.")
        sleeping()

def next():
    nexttime = next_time_start()
    next_day_start = (datetime.datetime.now() + datetime.timedelta(seconds=nexttime)).strftime('%A at %I:%M %p')
    return nexttime, next_day_start

def sleeping():
    nexttime, next_day_start = next()
    message = f"Sleeping till next time start on {next_day_start}..."
    print_time(message) # Print message to console
    log("sleeping", message) # Save message to a .txt file called "sleeping.txt"
    time.sleep(nexttime) # Sleep till next time range

    # After waking up the next day, print the date to the output.txt file to show new date log
    date = datetime.datetime.now().strftime('%d/%m/%Y')
    log_prints(f"====================={date}=====================")
    return

# Save logs to a .txt file to allow the discord bot to read on update

def log(file, message):
    try:
        f = open(f"logs/{file}.txt", "r")
    except FileNotFoundError:
        f = open(f"logs/{file}.txt", "w")
        f.write("0")
        f.close()

    current_time = time.strftime('%H:%M:%S', time.localtime())
    message = "["  + current_time + "]: " + message
    with open(f"logs/{file}.txt", "w") as f:
        f.write(message + "\n") # Write message to file
    # Close file

def log_status():
    pc = is_pc_closed()
    phone = is_phone_connected()
    try:
        f = open(f"logs/status.txt", "r", encoding="utf-8")
    except FileNotFoundError:
        f = open(f"logs/status.txt", "w", encoding="utf-8")
        f.write("0")
        f.close()

    if pc == True:
        pcstatus = "📱❌"
    else:
        pcstatus = "📱✔️"
    if phone == True:
        phonestatus = "🖥️✔️"
    else:
        phonestatus = "🖥️❌"

    current_time = time.strftime('%H:%M:%S', time.localtime())
    with open(f"logs/status.txt", "w", encoding="utf-8") as f:
        f.writelines(["["  + current_time + "]:\n" + "\tPC Status: " + pcstatus + "\n", "\tPhone Status: " + phonestatus])
    # Close file in write mode

def log_status_true(): # Only after wol is sent
    current_time = time.strftime('%H:%M:%S', time.localtime())
    with open(f"logs/status.txt", "w", encoding="utf-8") as f:
        f.writelines(["["  + current_time + "]:\n", "\tPC Status: 📱✔️", "\tPhone Status: 🖥️✔️"])
    print_time("["  + current_time + "]:\n\tPC Status: 📱✔️\n\tPhone Status: 🖥️✔️")
    # Close file in write mode

def print_time(message):
    log_prints(f"[{datetime.datetime.now().strftime('%H:%M:%S')}]: {message}")

# show that it has not been sent in the WOL Log at start
print_time("JamboWaker reporting for duty")
while(True):
    check_if_skip()
    log_status()
    time.sleep(15)
    check = check_if_away()
    if check == True:
        checking()
    else:
        sleeping() # Sleep till next time range

