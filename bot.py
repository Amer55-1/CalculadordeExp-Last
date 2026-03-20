import discord
from discord.ext import commands
import itertools
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# EXP items and multipliers
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
    "blue april fools' day candy": 1.5,
    "stripes": 1.5,
    "elizabeth's enhancement": 2,
    "holy bless": 1.1,  # average between 1.05-1.2
    "heroic ignition": 2.5,
    "guardian's blessing": 1.75,  # average 1.5-2
    "sun of happiness": 1.5,
    "recommended sever exp": 1.5,
}

# Ascension seeds per level
aufstieg_boosters = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398
}

# Calculate total EXP for a combo capped at 500%
def calculate_combo(combo):
    total = 1.0
    for item in combo:
        total *= items.get(item.lower(), 1)
    capped_total = min(total, 5)  # cap at 500%
    return {
        "base": total,
        "capped": capped_total
    }

# Find combinations to reach 500% without exceeding 600%
def suggest_combinations(user_items):
    all_items = list(items.keys())
    results = []

    # Single item 500%
    for ui in user_items:
        if items.get(ui.lower(), 0) >= 5:
            results.append({
                "combo": [ui],
                "capped": 5,
                "recommendation": "Use EXP Booster + Random Booster"
            })
            return results

    # If current combo < 500%, generate extra combos
    current_total = 1
    for ui in user_items:
        current_total *= items.get(ui.lower(), 1)

    # Generate additional combinations
    potential_additions = [i for i in all_items if i.lower() not in [x.lower() for x in user_items]]
    valid_combos = []

    for r in range(0, 4):  # up to 3 extra items
        for extra in itertools.combinations(potential_additions, r):
            combo = user_items + list(extra)
            total = 1
            for i in combo:
                total *= items.get(i.lower(), 1)
            if total >= 5:  # reached 500%
                valid_combos.append((combo, min(total,5)))

    # Prepare results
    for combo, capped in valid_combos[:10]:  # limit first 10
        results.append({
            "combo": combo,
            "capped": capped,
            "recommendation": "Use Epic 500% EXP Spell"
        })

    # If nothing reaches 500%, just show current
    if not results:
        results.append({
            "combo": user_items,
            "capped": min(current_total,5),
            "recommendation": "Current combo gives {:.0%}, can add more items to reach 500%".format(min(current_total,5)/5)
        })

    return results

# Combo command
@bot.command()
async def combo(ctx, *, args):
    user_items = [x.strip().lower() for x in args.split("+")]
    combos = suggest_combinations(user_items)
    response = ""
    for c in combos:
        response += f"Combo: {', '.join(c['combo'])}\n"
        response += f"Total without cap: {calculate_combo(c['combo'])['base']:.2f}x | Capped at 500%: {c['capped']:.2f}x\n"
        response += f"Recommendation: {c['recommendation']}\n\n"
    await ctx.send(response[:2000])

# Booster command for Ascension
@bot.command()
async def booster(ctx, *args):
    dungeon_percent = 50  # default
    if args[0].lower() == "dunge":
        dungeon_percent = float(args[1])
        start_level = int(args[2])
        end_level = int(args[3])
    else:
        start_level = int(args[0])
        end_level = int(args[1])

    total_seeds = sum(aufstieg_boosters.get(lvl,0) for lvl in range(start_level, end_level))
    # Base gain: 500% + dungeon %
    base_percent = 5  # 500% cap
    total_multiplier = base_percent * (1 + dungeon_percent/100) * 4  # x4 for boosters
    boosters_needed = total_seeds / total_multiplier
    await ctx.send(f"EXP Boosters needed from Ascension {start_level} → {end_level} with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters")

# Ready event
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# Run bot
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
