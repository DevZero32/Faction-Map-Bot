import os
import discord
import json
import time

from discord import Intents
from replit import db

#Discord Bot

Intents.message_content = True
client = discord.Client(intents = Intents.all())
token = os.environ["token"]

#Misc
global prefix
prefix = "!"
Admins = ["604817657169969182","440181498344374302","717161731805413470"]
disconnected = True

def reconnect(disconnected,token):
  print("Bot Disconnected")
  if disconnected == True:
    import discord
    from discord import Intents
    
    Intents.message_content = True
    client = discord.Client(intents = Intents.all())
   
    disconnected = False
    print("Bot connected")
    client.run(token)
    disconnected = True
    time.sleep(60)

#Manpower

def save_manpower(Manpower):
  db[str(os.environ['manpower'])] = Manpower
  print("Manpower Saved: {}".format(Manpower))
  

def set_manpower(condition):
  if condition == True:
    Manpower = [5,5,5,5,5,5,5,5,5,5,5,5]
  else: Manpower = []
  return Manpower

global Manpower
Manpower = set_manpower(False)
manpower_key = str(os.environ['manpower'])
#db[manpower_key] = Manpower
#Starting and disconnect

@client.event
async def on_ready():
  global Manpower
  Manpower = db[manpower_key]
  print("Manpower Loaded: {} | User: {} ".format(Manpower,client.user))

@client.event
async def on_disconnect():
  db[manpower_key] = Manpower
  print("Manpower Saved: {}".format(Manpower))

#Roles and Factions

Factions = [
"State Of Sparta",
"One Man Army Apex",
"Banana's Empire",
"Kingdom Of Pagasia",
"Glowing Phoenix",
"Kingdom Of Thespians",
"Byzantium",
"S.P.Q.R | Senātus Populusque Rōmānus",
"Carthage",
"Shadow Dynasty",
"Romania",
"Romanus",
"Greek City State Of Phocis"
]

def find_faction(roles,Factions):
  user_faction = "None"
  for i in range(len(roles)):
    role = roles[i]
    if str(role) in Factions:
          user_faction = role
  return user_faction

def faction_id(user_faction,Factions):
  count = 0
  while Factions[count] != user_faction:
    count = count + 1
  return count

def find_role(id,Admins):
  found = True
  for i in Admins:
        if id == i:
          user_role = "Staff"
          found = False
        elif found == True:
          user_role = "Member"
        if id == "412740786963087370":
          user_role = "Femboy"
  return user_role
  
#Region Functions

def is_neighbour(Regions,Faction,id):
  for Region_selected in Regions["Regions"]:
    owner = Region_selected["owner"] #each owned region by occupier
    if owner == Faction:
      for i in range(len(Region_selected["neighbours"])):
        neighbour = Region_selected["neighbours"][i]
        if int(id) == int(neighbour):
          return True
  return False
      

def load_regions():
  with open("regions.json", "r") as file:
    global Regions
    Regions = json.loads(file.read())
    return Regions

def save_regions(Regions,id,owner,building):
  for Region in Regions["Regions"]:
    if int(Region["id"]) == int(id):
      Region["owner"] = owner
      Region["building"] = building
      with open("regions.json","w") as file:
        json.dump(Regions,file,indent = 4)
      
def search_region(Regions,id):
    for Region in Regions["Regions"]:
      if int(Region["id"]) == int(id):
        return Region

def find_region_id(Regions,id):
  found = False
  for Region in Regions["Regions"]:
    if int(Region["id"]) == int(id):
      region_id = id
      found = True
      return region_id
    elif found == False: region_id = "no region_id"
  return region_id

#Bot things
def split(message):
  content = message.content.split()
  return content

@client.event
async def on_message(message):
  if message.author.bot or message.attachments:
    return #exit function
  else:
    ##Commands##
    
    commands = ["declare","region","map","close","test","ping","manpower"] #first word
    
    content = split(message)
    content_word = content[0] #Getting first word
    content_prefix = content_word[0] #Getting prefix / very first letter
    content_word = content_word[1:] #letters after prefix
    content_id = "no content_id"
    
    if len(content) > 1:
      content_id = content[1]
  if content_word not in commands and content_prefix == prefix : await message.channel.send("{} Command not recognised.".format(message.author.mention)) #Checking if it is inside commands
  elif content_prefix == prefix: #prefix recognised & command recognised
      
      roles = message.author.roles
      user_faction = str(find_faction(roles,Factions))
      if user_faction == "None":
        await message.channel.send("{} You aren't apart of a faction.".format(message.author.mention))
      else: 
        faction_index = faction_id(user_faction,Factions)
        
        #Checking for letters
        ABC = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y","Z"]
        abc = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        
        letters = False                          #i gave up and made two lists
        if content_id in ABC or content_id in abc:
            letters = True
        if letters == True:   #checking if letters in id
          await message.channel.send("{} Second word contains letters. Must be a number as it is identfication of the region.".format(message.author.mention))
        elif len(content) >= 3: # is a command. [command + id + definer] ##START COMMANDS HERE## ↓
          content_id = content[1]
          
          region_id = find_region_id(Regions,content_id)
          region = search_region(Regions,region_id)
          if region_id == content_id:

            owner = region["owner"]
            neighbours = region["neighbours"]
            building = region["building"]
            price = float(region["price"])
            water = region["water"]
            
            
            Faction = Factions[faction_index]
            
            definer_word = content[2]
            
            #occupy
            if content_word == "region" and definer_word == "occupy":
              if is_neighbour(Regions,Faction,region_id):
                if owner == "None" and building == "Fort":
                  cost = float(price * 0.5) + 2
                elif owner == "None": 
                  cost = float(price * 0.5)
                  if cost > float(Manpower[faction_index]):
                    await message.channel.send("{} You have dont have enough manpower.".format(message.author.mention))
                  else:
                    new_manpower = Manpower[faction_index]
                    new_manpower = new_manpower - cost
                    Manpower[faction_index] = new_manpower
                    await message.channel.send("{} You have occupied region {}, using {} Manpower & {} Left.".format(message.author.mention,region_id,cost,new_manpower))
                    save_manpower(Manpower)
                    save_regions(Regions,region_id,Faction,building)
              else:
                await message.channel.send("{} You arent neighbouring this region.".format(message.author.mention))
            elif content_word == "declare" and definer_word != "occupy":
              await message.channel.send("{} `{}` is not regonised as a command; commands for `!region`: `occupy`.".format(message.author.mention,definer_word))
        ##COMMANDS THAT HAVE A LENGTH OF UNDER 3##
        #Region Info
        if content_word == "region" and definer_word == "info":
          if owner == "None":
             price = price / 2
          await message.channel.send("""
{}

__**Region {} info**__
                                
Faction: `{}`
Neighbours: `{}`
Building: `{}`
Port availability: `{}`
Manpower required to seize: `{}`
                
          """.format(message.author.mention,region_id,owner,neighbours,building,water,price))
        #Map outside of regions
        if content_word == "map":
            map_link = "https://cdn.discordapp.com/attachments/1015326293715333170/1026203525333663784/Faction_Map_PNG.png"
            await message.channel.send("{} {}.".format(message.author.mention,map_link))
          #close
        if content_word == "close" and str(message.author.id) in Admins:
           await message.channel.send("{} Bot closing.".format(message.author.mention))
           await client.close()
        elif content_word == "close" and str(message.author.id) not in Admins: 
          await message.channel.send("{} You do not meet the requirements to run this command.".format(message.author.mention))
        #test
        if content_word == "test": await message.channel.send("{} SHUT THE FUCK UP!".format(message.author.mention))
        #ping
        if content_word == "ping": await message.channel.send("{} PONG!  `{}ms`.".format(message.author.mention,round(client.latency* 1000)))
        #manpower
        if content_word == "manpower": 
          faction_manpower = Manpower[faction_index]
          await message.channel.send("{} Your Manpower is `{}`.".format(message.author.mention,faction_manpower))

load_regions()
client.run(token)
while disconnected == True:
  reconnect(disconnected,token)

  # I am testing ()()()