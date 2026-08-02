import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

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
# CALCULATE EXP
# ----------------------------
def calculate_combo(combo, dungeon=0):
    total = 1.0

    for item in combo:
        total *= items.get(item.lower(), 1)

    # Cap máximo recomendado: 500% - 600%
    capped_total = min(max(total, 5), 6)

    # Multiplicador x4 de los boosters
    booster_total = capped_total * 4

    # Dungeon
    dungeon_multiplier = 1 + (dungeon / 100)

    return {
        "base": total,
        "capped": capped_total,
        "with_booster": booster_total,
        "with_dungeon": capped_total * dungeon_multiplier,
        "with_booster_and_dungeon": booster_total * dungeon_multiplier
    }


# ----------------------------
# DUNGEON COMMAND
# ----------------------------
@bot.command()
async def dungeon(ctx, percent: float, *, args=""):

    # Separar los items usando "+"
    user_items = [
        x.strip().lower()
        for x in args.split("+")
        if x.strip()
    ]

    # Calcular
    result = calculate_combo(
        user_items,
        dungeon=percent
    )

    # Respuesta
    await ctx.send(
        f"🏰 **Dungeon {percent}%**\n"
        f"📦 Items: {', '.join(user_items) if user_items else 'Ninguno'}\n\n"
        f"🔹 EXP base: **{result['base']:.2f}x**\n"
        f"🔹 EXP cap: **{result['capped']:.2f}x**\n"
        f"🔹 Con Booster x4: **{result['with_booster']:.2f}x**\n"
        f"🔹 Con Dungeon: **{result['with_dungeon']:.2f}x**\n"
        f"🔥 **Booster + Dungeon: {result['with_booster_and_dungeon']:.2f}x**"
    )


# ----------------------------
# ON READY
# ----------------------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    print("Comando disponible: !dungeon")


# ----------------------------
# RUN BOT
# ----------------------------
TOKEN = os.environ.get("DISCORD_TOKEN")

bot.run(TOKEN)
