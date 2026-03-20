import os
import discord
from discord.ext import commands
import itertools

# ----------------------------
# Intents & Bot Setup
# ----------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------------
# Item multipliers
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

# EXP boosters needed per level
aufstieg_boosters = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398
}

# ----------------------------
# Functions
# ----------------------------
def calculate_combo(combo, dungeon=0):
    """Calcula el multiplicador de EXP de un combo con opcional dungeon."""
    total = 1.0
    for item in combo:
        total *= items.get(item.lower(), 1)

    capped_total = min(total, 5)           # Limite máximo 500%
    booster_total = capped_total * 4       # Considerando booster 4x
    dungeon_multiplier = 1 + (dungeon / 100)

    return {
        "base": total,
        "capped": capped_total,
        "with_booster": booster_total,
        "with_dungeon": capped_total * dungeon_multiplier,
        "with_booster_and_dungeon": booster_total * dungeon_multiplier
    }

def find_combinations(user_items):
    """Encuentra todas las combinaciones que incluyen los items del usuario y alcanzan el cap."""
    all_items = list(items.keys())
    results = []

    for r in range(1, len(all_items) + 1):
        for combo in itertools.combinations(all_items, r):
            if all(ui.lower() in combo for ui in user_items):
                total = 1
                for i in combo:
                    total *= items[i]
                if total >= 5:  # Solo combos que alcanzan el cap
                    results.append(combo)
    return results

# ----------------------------
# Commands
# ----------------------------
@bot.command()
async def combo(ctx, *, args):
    """Muestra combos de EXP con los items ingresados por el usuario."""
    user_items = [x.strip().lower() for x in args.split("+")]
    valid_combos = find_combinations(user_items)

    if not valid_combos:
        await ctx.send("No combinations reach 500% EXP with those items.")
        return

    response = ""
    for combo_items in valid_combos[:10]:  # Limitar a los primeros 10 combos
        result = calculate_combo(combo_items)
        response += (
            f"**Combo:** {', '.join(combo_items)}\n"
            f"Total without cap: {result['base']:.2f}x | Capped at 500%: {result['capped']:.2f}x\n"
            f"With boosters: {result['with_booster']:.2f}x | With dungeon: {result['with_dungeon']:.2f}x\n"
            f"With boosters + dungeon: {result['with_booster_and_dungeon']:.2f}x\n\n"
        )

    await ctx.send(response[:2000])

@bot.command()
async def dungeon(ctx, percent: float, *, args=""):
    """Aplica multiplicador de dungeon sobre los items ingresados."""
    user_items = [x.strip().lower() for x in args.split("+") if x]
    result = calculate_combo(user_items, dungeon=percent)
    await ctx.send(f"Dungeon {percent}% → EXP with items + boosters: {result['with_booster_and_dungeon']:.2f}x")

@bot.command()
async def booster(ctx, start_level: int, end_level: int):
    """Calcula la cantidad de boosters necesarios entre niveles de ascensión."""
    total = sum(aufstieg_boosters.get(lvl, 0) for lvl in range(start_level, end_level))
    await ctx.send(f"EXP Boosters needed from Asc {start_level} → {end_level}: {total} Seeds")

# ----------------------------
# Events
# ----------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# ----------------------------
# Run Bot
# ----------------------------
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("No DISCORD_TOKEN found in environment variables!")

bot.run(TOKEN)
