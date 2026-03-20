# bot.py
import discord
from discord.ext import commands
import itertools

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

# ================================
# ASCENSION DATA (base "Samen" per level)
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
# COMBO FUNCTION
# ================================
def calculate_combos():
    max_cap = 5.0  # 500%
    combos_output = []
    all_items = list(items.keys())

    # Legendary Iris stands alone
    combos_output.append({
        "combo": ["legendary iris"],
        "total": items["legendary iris"],
        "recommendation": "Use EXP Booster + Random Booster"
    })

    # For all other combinations (2–4 items to reach 500%)
    for r in range(1, 4):
        for combo in itertools.combinations(all_items, r):
            if "legendary iris" in combo:
                continue  # skip combos with legendary iris
            total = 1.0
            for item in combo:
                total *= items[item]
            if total < max_cap:
                # Only consider combos that reach near 500%
                if total >= 4.0:  # 400%+
                    combos_output.append({
                        "combo": list(combo),
                        "total": total,
                        "recommendation": "Use Epic 500% EXP Spell + EXP Booster + Random Booster"
                    })
            elif total >= max_cap:
                total = max_cap
                combos_output.append({
                    "combo": list(combo),
                    "total": total,
                    "recommendation": "Use EXP Booster + Random Booster"
                })
    return combos_output

# ================================
# COMMAND: !combo
# ================================
@bot.command()
async def combo(ctx):
    combos = calculate_combos()
    msg_lines = []
    for c in combos:
        line = f"Combo: {', '.join(c['combo'])}\nTotal without cap: {c['total']:.2f}x | Capped at 500%: {min(c['total'],5.0):.2f}x\nRecommendation: {c['recommendation']}"
        msg_lines.append(line)
    # Split long messages if needed
    for i in range(0, len(msg_lines), 5):
        await ctx.send("\n\n".join(msg_lines[i:i+5]))

# ================================
# COMMAND: !booster [dungeon%] [start] [end]
# ================================
@bot.command()
async def booster(ctx, *args):
    # parse args
    dungeon_percent = 50.0
    start = 1
    end = 7

    if args[0] == "dunge":
        dungeon_percent = float(args[1])
        start = int(args[2])
        end = int(args[3])
    else:
        start = int(args[0])
        end = int(args[1])

    # Base dungeon bonus 50% as multiplier
    base_multiplier = 5.0 * (1 + dungeon_percent / 100)  # Legendary Iris base 500% x dungeon%
    boosters_needed = 0.0

    for lvl in range(start, end):
        base_exp = ascension_exp.get(lvl, 0)
        # Each EXP Booster x4
        total_per_booster = base_multiplier * 4  # multiplier applied
        boosters_needed += base_exp / total_per_booster

    await ctx.send(f"EXP Boosters needed from Ascension {start} → {end} with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters")

# ================================
# RUN BOT
# ================================
# Place your token here or load from environment variable
TOKEN = "YOUR_DISCORD_BOT_TOKEN"
bot.run(TOKEN)
