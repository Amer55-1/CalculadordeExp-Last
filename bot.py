import discord
from discord.ext import commands
import itertools
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Item multipliers
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

# EXP boosters needed per Ascension level (in Seeds)
aufstieg_boosters = {1: 3985, 2: 7970, 3: 11955, 4: 19128, 5: 95639, 6: 159398}

# ======================
# EXP Combo Calculations
# ======================
def calculate_combo(combo, dungeon=0):
    total = 1.0
    for item in combo:
        total *= items.get(item.lower(), 1)
    
    # Cap items at 500% (5.0x)
    capped_total = min(total, 5.0)

    # Dungeon multiplier applies on top of capped total
    dungeon_multiplier = 1 + (dungeon / 100)
    total_with_dungeon = capped_total * dungeon_multiplier

    # EXP Booster applies after dungeon
    total_with_booster = total_with_dungeon * 4  # x4 for boosters

    # Recommendation logic
    if len(combo) == 1 and capped_total == 5.0:
        recommendation = "Recommendation: Use EXP Booster + Random Booster"
    elif capped_total == 5.0:
        recommendation = "Recommendation: Use Epic 500% EXP Spell"
    else:
        recommendation = f"Current combo gives {capped_total*100:.0f}%, can add more items to reach 500%"

    return {
        "base": total,
        "capped": capped_total,
        "with_dungeon": total_with_dungeon,
        "with_booster_and_dungeon": total_with_booster,
        "recommendation": recommendation
    }

@bot.command()
async def combo(ctx, *, args):
    user_items = [x.strip().lower() for x in args.split("+")]
    
    result = calculate_combo(user_items)
    
    response = f"Combo: {', '.join(user_items)}\n"
    response += f"Total without cap: {result['base']:.2f}x | Capped at 500%: {result['capped']:.2f}x\n"
    response += f"With dungeon: {result['with_dungeon']:.2f}x | With boosters + dungeon: {result['with_booster_and_dungeon']:.2f}x\n"
    response += result['recommendation']

    await ctx.send(response[:2000])

# ======================
# Dungeon Command
# ======================
@bot.command()
async def dungeon(ctx, percent: float, *, args=""):
    user_items = [x.strip().lower() for x in args.split("+") if x]
    result = calculate_combo(user_items, dungeon=percent)
    await ctx.send(f"Dungeon {percent}% → EXP with items + boosters: {result['with_booster_and_dungeon']:.2f}x")

# ======================
# Booster Calculation for Ascension
# ======================
def calculate_boosters_needed(start_level, end_level, dungeon_percent=50):
    total_seeds = sum(aufstieg_boosters.get(lvl, 0) for lvl in range(start_level, end_level))
    
    # Base EXP multiplier: 500% exp + dungeon percent
    base_exp = 5.0  # 500% exp
    dungeon_multiplier = 1 + (dungeon_percent / 100)
    exp_per_booster = base_exp * dungeon_multiplier * 4  # Booster multiplier
    
    # Calculate boosters needed
    boosters_needed = total_seeds / exp_per_booster
    return boosters_needed

@bot.command()
async def booster(ctx, *args):
    # Example usage:
    # !booster 1 7 (default dungeon 50%)
    # !booster dungeon 180 1 7
    if args[0].lower() == "dungeon":
        dungeon_percent = float(args[1])
        start_level = int(args[2])
        end_level = int(args[3])
    else:
        dungeon_percent = 50.0
        start_level = int(args[0])
        end_level = int(args[1])
    
    boosters_needed = calculate_boosters_needed(start_level, end_level, dungeon_percent)
    await ctx.send(f"EXP Boosters needed from Ascension {start_level} → {end_level} with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters")

# ======================
# Bot Ready Event
# ======================
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# ======================
# Run the Bot
# ======================
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
