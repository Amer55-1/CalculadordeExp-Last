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

# Seeds required per Ascension level (base 500% + dungeon 50%)
aufstieg_boosters = [3985, 7970, 11955, 19128, 95639, 159398]

# Calculate total EXP for a combo, including dungeon
def calculate_combo(combo, dungeon=0):
    total = 1.0
    for item in combo:
        total *= items.get(item.lower(), 1)
    # Limit recommendations between 500% and 600%
    capped_total = min(max(total, 5), 6)
    booster_total = capped_total * 4  # EXP Booster x4
    dungeon_multiplier = 1 + (dungeon / 100)
    return {
        "base": total,
        "capped": capped_total,
        "with_booster": booster_total,
        "with_dungeon": capped_total * dungeon_multiplier,
        "with_booster_and_dungeon": booster_total * dungeon_multiplier
    }

# Find valid combinations including user items that reach at least 500%
def find_combinations(user_items):
    all_items = list(items.keys())
    results = []
    for r in range(1, len(all_items)+1):
        for combo in itertools.combinations(all_items, r):
            if all(ui.lower() in combo for ui in user_items):
                total = 1
                for i in combo:
                    total *= items[i]
                if total >= 5:  # only combos reaching 500%
                    results.append(combo)
    return results

# Combo command
@bot.command()
async def combo(ctx, *, args):
    user_items = [x.strip().lower() for x in args.split("+")]
    valid_combos = find_combinations(user_items)
    
    if not valid_combos:
        await ctx.send("No combinations reach 500% EXP with those items.")
        return
    
    response = ""
    for combo_items in valid_combos[:10]:  # limit to first 10 combos
        result = calculate_combo(combo_items)
        response += f"Combo: {', '.join(combo_items)}\n"
        response += f"Total without cap: {result['base']:.2f}x | Recommendation cap: {result['capped']:.2f}x\n"
        response += f"With boosters: {result['with_booster']:.2f}x | With dungeon: {result['with_dungeon']:.2f}x\n"
        response += f"With boosters + dungeon: {result['with_booster_and_dungeon']:.2f}x\n\n"
    
    await ctx.send(response[:2000])

# Dungeon command
@bot.command()
async def dungeon(ctx, percent: float, *, args=""):
    user_items = [x.strip().lower() for x in args.split("+") if x]
    result = calculate_combo(user_items, dungeon=percent)
    await ctx.send(f"Dungeon {percent}% → EXP with items + boosters: {result['with_booster_and_dungeon']:.2f}x")

# Booster command with optional dungeon
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

    # Sum seeds for selected range
    total_seeds = sum(aufstieg_boosters[start_level-1:end_level-1])

    # Total gain per booster with dungeon %
    total_multiplier = 7.5 / 5 * (5 + dungeon_percent / 100)  # Adjusted to scale relative to base 750% (500% items + 50% dungeon)
    booster_multiplier = total_multiplier * 4  # x4 EXP Booster

    boosters_needed = total_seeds / booster_multiplier

    await ctx.send(
        f"EXP Boosters needed from Ascension {start_level} → {end_level} "
        f"with dungeon {dungeon_percent}%: {boosters_needed:.2f} Boosters"
    )

# Ready event
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# Run bot
TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)
