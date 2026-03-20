# bot.py
import discord
from discord.ext import commands
import itertools
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ================================
# ITEM MULTIPLIERS
# ================================
items = {
    "lucky blessed iris": 2,
    "blessed iris": 2,
    "iris bless": 2,
    "platinum blessed iris": 3,
    "legendary iris": 5,
    "experience potion 1-day": 1.3,
    "experience potion 3-days": 1.3,
    "experience potion 7-days": 1.3,
    "experience elixir 1-hour": 1.3,
    "experience elixir 3-hour": 1.3,
    "experience elixir 7-hour": 1.3,
    "experience scroll": 1.5,
    "blessed bottle": 1.2,
    "experience potion": 1.5,
    "sacred jar": 1.3,
    "cake": 1.3,
    "large cake": 1.3,
    "snowman": 2,
    "big snowman": 2,
    "chicken noodle soup": 1.2,
    "watermelon": 1.5,
    "water melon slice": 1.2,
    "blue april fools candy": 1.5,
    "stripes": 1.5,
}

MAX_CAP = 5.0  # 500% cap
MIN_TARGET = 5.0  # minimum recommended total multiplier

# ================================
# ASCENSION DATA
# ================================
ascension_exp = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398,
}

# ================================
# COMMAND: !combo
# ================================
@bot.command()
async def combo(ctx):
    output = []

    # Legendary Iris always alone
    output.append(
        f"Combo: legendary iris\nTotal: 5.00x\nRecommendation: Use EXP Booster + Random Booster"
    )

    # Generate other combos (2–3 items) for reaching near 500%
    other_items = [i for i in items.keys() if i != "legendary iris"]
    for r in range(1, 4):
        for combo in itertools.combinations(other_items, r):
            total = 1.0
            for item in combo:
                total *= items[item]

            if total >= 4.0 and total <= MAX_CAP:
                # close to 500% cap
                rec = "Use Epic 500% EXP Spell + EXP Booster + Random Booster"
                output.append(
                    f"Combo: {', '.join(combo)}\nTotal: {min(total, MAX_CAP):.2f}x\nRecommendation: {rec}"
                )

    # Send messages in chunks to avoid Discord limit
    for i in range(0, len(output), 5):
        await ctx.send("\n\n".join(output[i:i+5]))

# ================================
# COMMAND: !booster
# Usage: !booster 1 7 OR !booster dunge 180 1 7
# ================================
@bot.command()
async def booster(ctx, *args):
    try:
        dungeon_percent = 50.0
        start, end = 1, 7

        if args[0] == "dunge":
            dungeon_percent = float(args[1])
            start = int(args[2])
            end = int(args[3])
        else:
            start = int(args[0])
            end = int(args[1])

        # Base: Legendary Iris 500% + dungeon multiplier
        base_multiplier = 5.0 * (1 + dungeon_percent / 100)
        boosters_needed = 0.0

        for lvl in range(start, end):
            exp_needed = ascension_exp.get(lvl, 0)
            boosters_needed += exp_needed / (base_multiplier * 4)  # each EXP Booster x4

        await ctx.send(
            f"EXP Boosters needed from Ascension {start} → {end} with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters"
        )
    except Exception as e:
        await ctx.send(f"Error: {e}")

# ================================
# RUN BOT
# ================================
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # load token from env for safety
bot.run(TOKEN)
