Got bored one day and decided to make a program that automatically opens my PC whenever I get home from university simply by just checking if phone has connected to the WiFi network and sending a WoL Magic Packet.  
- Sends a message though a discord bot notifying the user of the wakeup.  
- Keeps logs of current status and last wakeup timestamp
Pretty simple code. Currently requires seperate device (Using a Linux server) to run the code continuously.

## Customizable Variables
### WakerBot.py
Create your bot from [Discord's Developers Portal](https://discord.com/developers/applications/)
```
token = "Discord bot token ID"   # Bot token for connection
serverID = "Discord Server ID"   # What server you want the bot to be connected to
channelID = "Discord Channel ID" # What log channel you want the bot to be connected to
```
### PCWaker.py
```
pc_mac = "MAC Address of the PC to wake up"   # MAC address of your personal computer
pc_ip = 'IP Address of the PC to wake up'     # IP Address of your personal computer
phone_ip = ['IP Address of Phone #1', IP Address of Phone #2 '] # The IP Addresses' to check for, listed in an array (For example listing both 5G, 2.4G)
```

Time ranges for each day of the week to set status as "away" and wait for phone to connect to network to send WOL packet
```
time_ranges = {
    'Sunday' : [('00:00', '00:00')],
    'Monday': [('00:00', '00:00')],
    'Tuesday': [('00:00', '00:00')],
    'Wednesday': [('00:00', '00:00')],
    'Thursday': [('00:00', '00:00')]
}
```
Note that this was built assuming that Friday and Saturday are weekdays instead of Saturday and Sunday, so changing 
```Weekends = ['Thursday', 'Sunday']```
to 
```Weekends = ['Friday', 'Monday']```
should allow the code to sleep correctly over weekends.  

Rule of thumb it that it's ["Day before the start of weekend", "Day after the end of weekend"])

## Running
Just run WakerBot.py and Waker.py should open automatically alongside it. 
_Should_ work on Windows although have not tested the restart commmand.
Built for Linux.
