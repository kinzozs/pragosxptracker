import discord
from discord.ext import commands
import json

# Bot token
BOT_TOKEN = " " # YOU NEED TO GENERATE YOUR OWN DISCORD TOKEN

# Players data file
DATA_FILE = "players.json"

# GMs. ADD THE DISCORD ID FROM USERS WHO CAN MODIFY THE EXPERIENCE
GM_USER_IDS = [ ]

# ENTER THE ID FROM THE CHANNEL WHERE THE BOT WILL SEND MESSAGES
REPORTS_CHANNEL_ID = 

# Prefixes
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# --- PLAYER DATA ---
def load_players_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        initial_data = {
            "lestat": {"xp": 0, "level": 1, "discord_id": ""},
            "torin": {"xp": 0, "level": 1, "discord_id": ""},
            "liftrasa": {"xp": 0, "level": 1, "discord_id": ""},
            "asterion": {"xp": 0, "level": 1, "discord_id": ""}
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(initial_data, f, indent=4)
        return initial_data

def save_players_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- Bot Events ---
@bot.event
async def on_ready():
    print(f'Logeado rey {bot.user}!')
    print('EL BOT ESTA ONLINE PAPURRI')

# --- Bot Commands ---
@bot.command()
async def xp_list(ctx):
    """Print de xp_list."""
    players_data = load_players_data()
    embed = discord.Embed(title="Pragos XP Tracker", color=0x3498db)
    
    # Pjs y emote ID
    player_emojis = {
        "player1": "", #YOU CAN ADD EMOTES
        "player2": "", #FOR EACH PLAYER CLASS
        "player3": "", #USE EMOTE IDS
        "player4": ""
    }
    
    for player_name, data in players_data.items():
        emote = player_emojis.get(player_name, "")
        
        embed.add_field(
            name=f"{emote} {player_name.title()}",
            value=f"**Nivel:** {data['level']}\n**XP:** {data['xp']}/100",
            inline=False
        )

    target_channel = bot.get_channel(REPORTS_CHANNEL_ID)
    if target_channel:
        await target_channel.send(embed=embed)
    else:
        # Fallback de error
        await ctx.send("Could not find the designated reporting channel.")


@bot.command()
async def add_xp(ctx, player_name: str, amount: int):
    """Comando de GM para agregar XP."""
    # Checkeo si el ID es GM
    if ctx.author.id not in GM_USER_IDS:
        await ctx.send("Que tocas mostro.")
        return

    players_data = load_players_data()
    player_name = player_name.lower() 

    if player_name not in players_data:
        await ctx.send(f"Escribiste mal, gaga.")
        return

    players_data[player_name]['xp'] += amount
    
    target_channel = bot.get_channel(REPORTS_CHANNEL_ID)

    # Checkeo de XP para subir de level
    while players_data[player_name]['xp'] >= 100:
        players_data[player_name]['xp'] -= 100
        players_data[player_name]['level'] += 1

        # Toma player ID de Discord
        player_discord_id = players_data[player_name].get('discord_id')
        
        # Target de channel
        target_channel = bot.get_channel(REPORTS_CHANNEL_ID)
        
        # Ping de level up
        if player_discord_id and target_channel:
            await target_channel.send(f"Felicitaciones, <@{player_discord_id}>! {player_name.title()} subió a nivel {players_data[player_name]['level']}!")
        elif target_channel:
            await target_channel.send(f"Felicitaciones! {player_name.title()} subió a nivel {players_data[player_name]['level']}!")
        else:
            # Fallback de error
            await ctx.send("Level up, but could not find the designated reporting channel.")

    save_players_data(players_data)
    
    # Mensaje de confirmacion XP
    await target_channel.send(f"Se añadió {amount} XP a {player_name.title()}. Ahora tiene {players_data[player_name]['xp']} XP en nivel {players_data[player_name]['level']}.")

@bot.command()
async def add_xp_all(ctx, amount: int):
    """Comando de GM para agregar XP a toda la party."""
    if ctx.author.id not in GM_USER_IDS:
        await ctx.send("Que tocas mostro.")
        return

    players_data = load_players_data()
    target_channel = bot.get_channel(REPORTS_CHANNEL_ID)

    if not target_channel:
        await ctx.send("Could not find reporting channel.")
        return

    for p_name in players_data:
        players_data[p_name]['xp'] += amount
        
        while players_data[p_name]['xp'] >= 100:
            players_data[p_name]['xp'] -= 100
            players_data[p_name]['level'] += 1
            p_id = players_data[p_name].get('discord_id')
            
            if p_id:
                await target_channel.send(f"Felicitaciones, <@{p_id}>! {p_name.title()} subió a nivel {players_data[p_name]['level']}!")
            else:
                await target_channel.send(f"Felicitaciones! {p_name.title()} subió a nivel {players_data[p_name]['level']}!")

    save_players_data(players_data)
    await target_channel.send(f"⚔️ **Party Update:** Se añadieron {amount} XP a todos.")

@bot.command()
async def remove_xp(ctx, player_name: str, amount: int):
    """Comando de GM para restar XP."""
    # Checkeo si el ID es GM
    if ctx.author.id not in GM_USER_IDS:
        await ctx.send("Que tocas mostro.")
        return

    players_data = load_players_data()
    player_name = player_name.lower() 

    if player_name not in players_data:
        await ctx.send(f"Escribiste mal de nuevo gaga.")
        return

    # Restar XP primero
    players_data[player_name]['xp'] -= amount
    
    # Checkeo de XP para bajar de level
    while players_data[player_name]['xp'] < 0:
        if players_data[player_name]['level'] > 1:
            players_data[player_name]['level'] -= 1
            players_data[player_name]['xp'] += 100
            await ctx.send(f"JIJOOOOO {player_name.title()} ha bajado a nivel {players_data[player_name]['level']}.")
        else:
            players_data[player_name]['xp'] = 0
            break

    save_players_data(players_data)

    target_channel = bot.get_channel(REPORTS_CHANNEL_ID)
    if target_channel:
        await target_channel.send(f"Se eliminaron {amount} XP a {player_name.title()} por peton. Ahora tiene {players_data[player_name]['xp']} XP en nivel {players_data[player_name]['level']}.")
    else:
        await ctx.send("Could not find the designated reporting channel.")

bot.run(BOT_TOKEN)