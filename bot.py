import discord
from discord.ext import commands
import itertools
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ======================
# Item multipliers
# ======================
items = {
    "legendary iris": 5.0,
    "platinum iris": 3.0,
    "blessed iris": 2.0,
    "experience scroll": 1.5,
    "blessed bottle": 1.2,
    "cake": 1.3,
    "experience elixir": 1.3,
    "snowman": 2.0,
    "double exp event": 2.0
}

# ======================
# EXP Boosters needed per Ascension level (Seeds)
# ======================
aufstieg_boosters = {1: 3985, 2: 7970, 3: 11955, 4: 19128, 5: 95639, 6: 159398}

# ======================
# Calculate base combo (without dungeon)
# ======================
def calculate_combo_base(combo):
    total = 1.0
    for item in combo:
        total *= items.get(item.lower(), 1)
    capped_total = min(total, 5.0)  # Cap at 500%
    return capped_total

# ======================
# Recommend items / boosters
# ======================
def recommend_combo(user_items):
    current_total = calculate_combo_base(user_items)
    
    # Single item giving 500%
    if len(user_items) == 1 and current_total >= 5.0:
        return "Recommendation: Use EXP Booster + Random Booster"
    
    # Combo reaches 500%
    if current_total >= 5.0:
        return "Recommendation: Use Epic 500% EXP Spell"
    
    # Suggest additional items to reach 500% if possible
    possible_additions = []
    for name, multiplier in items.items():
        if name.lower() in [i.lower() for i in user_items]:
            continue
        new_total = calculate_combo_base(user_items + [name])
        if 5.0 <= new_total <= 6.0 or (current_total < 5.0 <= new_total):
            possible_additions.append(name)
    
    if possible_additions:
        return f"Recommendation: Add {' + '.join(possible_additions)} and use Epic 500% EXP Spell"
    
    # Default
    return "Recommendation: Use EXP Booster + Random Booster"

# ======================
# Combo command
# ======================
@bot.command()
async def combo(ctx, *, args):
    user_items = [x.strip().lower() for x in args.split("+") if x]
    if not user_items:
        await ctx.send("Please provide at least one item.")
        return
    
    capped_total = calculate_combo_base(user_items)
    recommendation = recommend_combo(user_items)

    response = f"Combo: {', '.join(user_items)}\n"
    response += f"Total without cap: {capped_total:.2f}x | Capped at 500-600%: {capped_total:.2f}x\n"
    response += recommendation

    await ctx.send(response[:2000])

# ======================
# Dungeon command
# ======================
def calculate_combo_dungeon(combo, dungeon_percent=50.0):
    base = calculate_combo_base(combo)
    dungeon_multiplier = 1 + dungeon_percent / 100
    return base * dungeon_multiplier

@bot.command()
async def dungeon(ctx, percent: float, *, args=""):
    user_items = [x.strip().lower() for x in args.split("+") if x]
    result = calculate_combo_dungeon(user_items, dungeon_percent=percent)
    await ctx.send(f"Dungeon {percent}% → EXP with items: {result:.2f}x")

# ======================
# Booster command (Ascension)
# ======================
def calculate_boosters(start_level, end_level, dungeon_percent=50.0):
    base_boosters_needed = sum(aufstieg_boosters.get(lvl, 0) for lvl in range(start_level, end_level))
    
    # Base EXP with dungeon
    base_exp_percent = 5.0  # 500% EXP base
    dungeon_multiplier = 1 + dungeon_percent / 100  # e.g., 50% → 1.5
    total_exp_per_booster = base_exp_percent * dungeon_multiplier * 4  # 4x per EXP Booster
    
    boosters_needed = base_boosters_needed / total_exp_per_booster
    return boosters_needed

@bot.command()
async def booster(ctx, *args):
    """
    Usage:
    !booster 1 7           → default dungeon 50%
    !booster dunge 180 1 7 → dungeon 180%
    """
    args = [str(a) for a in args]
    if args[0].lower() == "dunge" and len(args) == 4:
        dungeon_percent = float(args[1])
        start_level = int(args[2])
        end_level = int(args[3])
    elif len(args) == 2:
        dungeon_percent = 50.0
        start_level = int(args[0])
        end_level = int(args[1])
    else:
        await ctx.send("Usage: !booster [start_level end_level] or !booster dunge [percent start_level end_level]")
        return

    boosters_needed = calculate_boosters(start_level, end_level, dungeon_percent=dungeon_percent)
    await ctx.send(f"EXP Boosters needed from Ascension {start_level} → {end_level} with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters")

# ======================
# Bot ready
# ======================
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# ======================
# Run bot
# ======================
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
