import os
import discord
import json
import time

from discord import Intents
#Discord Bot

Intents.message_content = True
client = discord.Client(intents = Intents.all())
token = os.environ["token"]

#Misc
global prefix
prefix = "!"
Admins = ["604817657169969182","440181498344374302","717161731805413470"]
disconnected = True

#channels id
global channel_todo
global channel_war
global channel_map
channel_todo = 1016076988756271135
channel_war = 1016075320857723051
channel_map = 1015326293715333170


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

#Starting and disconnect

@client.event
async def on_ready():
  print("User: {} ".format(client.user))

#Factions

def load_factions():
  with open("factions.json", "r") as file:
    global Factions
    Factions = json.loads(file.read())
    return Factions

def save_factions(Factions,faction_name,manpower,permissions):
  for Faction in Factions["Factions"]:
    name_json = Faction["faction"]
    if name_json == faction_name:
      Faction["manpower"] = manpower
      Faction["permissions"] = permissions
      with open("factions.json","w") as file:
        json.dump(Factions,file,indent = 4)

def search_faction(Factions,Roles):
    for Faction in Factions["Factions"]:
      faction_name = Faction["faction"]
      for Role in Roles:
        if faction_name == str(Role):
          return Faction
    return "No faction found"

def faction_id(user_faction,Factions):
  count = 0
  while Factions["faction"] != user_faction:
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

def is_neighbour(Regions,Faction,id):
  for Region_selected in Regions["Regions"]:
    owner = Region_selected["owner"] #each owned region by occupier
    if owner == Faction:
      for i in range(len(Region_selected["neighbours"])):
        neighbour = Region_selected["neighbours"][i]
        if int(id) == int(neighbour):
          return True
  return False

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
    
    commands = ["region","map","close","test","ping","manpower","factions"] #first word
    region_commands = ["occupy","info"] #region definer words

    
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

      #Checking Faction
      
      Faction = search_faction(Factions,roles) 
      if Faction == "No faction found":
        await message.channel.send("{} You aren't part of a faction.".format(message.author.mention))
      else: 
        #Faction
        faction_name = Faction["faction"]
        manpower = Faction["manpower"]
        permissions = Faction["permissions"]
        
        #Checking for letters
        ABC = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y","Z"]
        abc = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        
        letters = False                          #i gave up and made two lists
        if content_id in ABC or content_id in abc:
            letters = True
        if letters == True:   #checking if letters in id
          await message.channel.send("{} Second word contains letters. Must be a number as it's identfication for the region.".format(message.author.mention))
        
        elif len(content) >= 3: # is a command. [command + id + definer] ##START COMMANDS HERE## ↓
          content_id = content[1]
          definer_word = content[2]
          
          region_id = find_region_id(Regions,content_id)
          region = search_region(Regions,region_id)
          if region_id == content_id:
            #Regions
            owner = region["owner"]
            neighbours = region["neighbours"]
            building = region["building"]
            price = float(region["price"])
            water = region["water"]
            cost = float(0)
            
            #occupy
            if content_word == "region" and definer_word == "occupy": 
                load_regions()
                if is_neighbour(Regions,faction_name,region_id): 
                  if owner != "None" and owner != faction_name: #region currently controled
                    if building == "Fort": #adding to cost is Fort is present
                      cost = 2
                    cost = cost + price
                    if cost <=  manpower: #checking manpower
                      channel =  client.get_channel(channel_war)
                      #changing manpower
                      
                      new_manpower = manpower - cost
                      manpower = new_manpower
                      
                      #Sending Messages
                      await message.channel.send("{} You have started a war with {}. Using {} Manpower with {} left.".format(message.author.mention,owner,cost,new_manpower))
                      await channel.send("""
__**{} is being attacked by {}**__

{} has 3 days to respond or the node will be taken.

**Region {} info**
                                
Region Owner: `{}`
Neighbours: `{}`
Building: `{}`
Port availability: `{}`
Manpower required to seize: `{}` """.format(owner,faction_name,owner,region_id,owner,neighbours,building,water,price))  
                      #Saving
                      save_factions(Factions,faction_name,manpower,permissions)
                      
                    else:await message.channel.send("{} You have don't have enough manpower.".format(message.author.mention))
                  #Nont currently controled
                  elif owner == "None":
                    if building == "Fort": #adding to cost is Fort is present
                      cost = 2
                    cost = cost + (price / 2)
                    if cost <= manpower: #checking manpower:
                      channel =  client.get_channel(channel_todo)

                      #setting manpower
                      new_manpower = manpower - cost
                      manpower = new_manpower
                      #Sending
                      await message.channel.send("{} You have occupied region {}, using {} Manpower & {} Left.".format(message.author.mention,region_id,cost,new_manpower))
                      await channel.send("**__Region {}__** has been taken by {}".format(region_id,faction_name))
                      #Saving
                      save_factions(Factions,faction_name,manpower,permissions)
                      save_regions(Regions,region_id,faction_name,building)#Region not owned 
                    else: await message.channel.send("{} You have don't have enough manpower.".format(message.author.mention))
                  else:await message.channel.send("{} You already own this region.".format(message.author.mention))
                else:
                  await message.channel.send("{} You aren't neighbouring this region.".format(message.author.mention))
            elif content_word == "region" and definer_word not in region_commands:
              await message.channel.send("{} `{}` is not regonised as a command; commands for `!region`  are `{}` .".format(message.author.mention,definer_word,region_commands))
       
        ##COMMANDS THAT HAVE A LENGTH OF UNDER 3##
        #Region Info
        if content_word == "region" and definer_word == "info":
          if owner == "None":
             price = price / 2
          await message.channel.send("""
{}

__**Region {} info**__
                                
Region Owner: `{}`
Neighbours: `{}`
Building: `{}`
Port availability: `{}`
Manpower required to seize: `{}`
                
          """.format(message.author.mention,region_id,owner,neighbours,building,water,price))
        #Map outside of regions
        if content_word == "map":
            map_link = "https://cdn.discordapp.com/attachments/1015326293715333170/1026529209465712640/Faction_Map_PND.png"
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
          await message.channel.send("{} Your Manpower is `{}`.".format(message.author.mention,manpower))
          #Factions
        if content_word == "factions":
          load_factions()
          main = ""
          factiontitle = """
**__ FACTIONS __**"""
          for Faction in Factions["Factions"]:
            faction_name = Faction["faction"]
            manpower = Faction["manpower"]
            main = main + (
"""

Faction: **{}**
Manpower: **{}**"""
            .format(faction_name,manpower))
          embed = discord.Embed(title=factiontitle,description=main,color=discord.Colour.blue())
          await message.channel.send(embed=embed)
  
  print("on_message over")

load_factions()
load_regions()
client.run(token)
while disconnected == True:
  reconnect(disconnected,token)