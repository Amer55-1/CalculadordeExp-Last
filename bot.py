import discord
from discord.ext import commands
import itertools
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# ITEM MULTIPLIERS
# ----------------------------
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

# ----------------------------
# ASCENSION EXP (Seeds)
# ----------------------------
aufstieg_boosters = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398
}

# ----------------------------
# CALCULATE ITEM COMBO
# ----------------------------
def calculate_combo(combo, dungeon=0):
    total = 1.0
    for item in combo:
        total *= items.get(item.lower(), 1)
    
    # Cap combo between 500%-600% recommended
    capped_total = min(max(total, 5), 6)

    # Base booster multiplier (x4)
    booster_total = capped_total * 4

    # Dungeon multiplier
    dungeon_multiplier = 1 + (dungeon / 100)
    
    return {
        "base": total,
        "capped": capped_total,
        "with_booster": booster_total,
        "with_dungeon": capped_total * dungeon_multiplier,
        "with_booster_and_dungeon": booster_total * dungeon_multiplier
    }

# ----------------------------
# FIND VALID COMBOS
# ----------------------------
def find_combinations(user_items):
    all_items = list(items.keys())
    results = []
    for r in range(1, len(all_items)+1):
        for combo in itertools.combinations(all_items, r):
            # Check if all user items are included
            if all(ui.lower() in combo for ui in user_items):
                total = 1
                for i in combo:
                    total *= items[i]
                # Only combos >= 500% (cap base) recommended
                if total >= 5:
                    results.append(combo)
    return results

# ----------------------------
# COMBO COMMAND
# ----------------------------
@bot.command()
async def combo(ctx, *, args):
    user_items = [x.strip().lower() for x in args.split("+")]
    valid_combos = find_combinations(user_items)
    
    if not valid_combos:
        await ctx.send("No combinations reach the 500% EXP cap with those items.")
        return
    
    response = ""
    for combo_items in valid_combos[:10]:  # limit first 10 combos
        result = calculate_combo(combo_items)
        response += f"Combo: {', '.join(combo_items)}\n"
        response += f"Base: {result['base']:.2f}x | Capped: {result['capped']:.2f}x\n"
        response += f"With Boosters: {result['with_booster']:.2f}x | With Dungeon: {result['with_dungeon']:.2f}x\n"
        response += f"Boosters + Dungeon: {result['with_booster_and_dungeon']:.2f}x\n\n"
    
    await ctx.send(response[:2000])

# ----------------------------
# DUNGEON COMMAND
# ----------------------------
@bot.command()
async def dungeon(ctx, percent: float, *, args=""):
    user_items = [x.strip().lower() for x in args.split("+") if x]
    result = calculate_combo(user_items, dungeon=percent)
    await ctx.send(
        f"Dungeon {percent}% → EXP with items + boosters: {result['with_booster_and_dungeon']:.2f}x"
    )

# ----------------------------
# BOOSTER COMMAND
# ----------------------------
@bot.command()
async def booster(ctx, *args):
    """
    Usage:
    !booster start_level end_level -> dungeon 50% default
    !booster dungeon <percent> start_level end_level -> custom dungeon %
    """
    dungeon_percent = 50  # default
    levels = []

    # parse args
    if args[0].lower() == "dungeon":
        dungeon_percent = float(args[1])
        levels = list(map(int, args[2:]))
    else:
        levels = list(map(int, args))

    if len(levels) != 2:
        await ctx.send("Usage: !booster [dungeon <percent>] <start_level> <end_level>")
        return

    start_level, end_level = levels

    # sum total EXP needed
    total_seeds = sum(aufstieg_boosters.get(lvl, 0) for lvl in range(start_level, end_level))

    # Apply dungeon multiplier
    total_with_dungeon = total_seeds * (1 + dungeon_percent / 100)

    # Each EXP Booster gives 4x max cap (500% base)
    booster_per_seed = 5 * 4  # base 500% * booster x4
    boosters_needed = total_with_dungeon / booster_per_seed

    await ctx.send(
        f"EXP Boosters needed from Ascension {start_level} → {end_level} "
        f"with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters"
    )

# ----------------------------
# ON READY
# ----------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# ----------------------------
# RUN BOT
# ----------------------------
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
