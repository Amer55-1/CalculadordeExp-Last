import discord
from discord.ext import commands
import os

# ============================================================
# CONFIGURACIÓN DEL BOT
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# ============================================================
# BOOSTERS NECESARIOS CON DUNGEON 50%
# ============================================================
#
# Estos son los valores BASE.
#
# Dungeon 50%:
#
# Ascension 1 → 2 = 3.985
# Ascension 2 → 3 = 7.970
# Ascension 3 → 4 = 11.955
# Ascension 4 → 5 = 19.128
# Ascension 5 → 6 = 95.639
# Ascension 6 → 7 = 159.398
#
# ============================================================

boosters_50 = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398
}


# ============================================================
# CALCULAR BOOSTERS SEGÚN DUNGEON
# ============================================================

def calculate_boosters(base_boosters, dungeon_percent):

    # Los valores base corresponden a Dungeon 50%
    base_dungeon_multiplier = 1 + (50 / 100)

    # Multiplicador del nuevo Dungeon
    new_dungeon_multiplier = 1 + (dungeon_percent / 100)

    # Fórmula:
    #
    # Boosters nuevos =
    # Boosters base × multiplicador Dungeon 50%
    # / multiplicador Dungeon nuevo
    #
    result = (
        base_boosters
        * base_dungeon_multiplier
        / new_dungeon_multiplier
    )

    return result


# ============================================================
# COMANDO DUNGEON
# ============================================================
#
# USO:
#
# !dungeon 130
#
# Muestra todas las ascensiones con Dungeon 130%
#
# ------------------------------------------------------------
#
# !dungeon 130 5
#
# Muestra solamente 5 → 6
#
# ------------------------------------------------------------
#
# !dungeon 130 5 6
#
# También muestra solamente 5 → 6
#
# ============================================================

@bot.command(name="dungeon")
async def dungeon(ctx, dungeon_percent: float, start_level: int = None, end_level: int = None):

    # ========================================================
    # VALIDAR DUNGEON
    # ========================================================

    if dungeon_percent < 0:
        await ctx.send(
            "❌ El porcentaje de Dungeon no puede ser negativo."
        )
        return


    # ========================================================
    # SI NO SE INDICA ASCENSIÓN
    # MOSTRAR TODAS
    # ========================================================

    if start_level is None:

        response = (
            f"🏰 **Cálculo de Dungeon {dungeon_percent:.0f}%**\n\n"
            f"📌 Valores calculados tomando como referencia "
            f"**Dungeon 50%**.\n\n"
        )

        for level, base_value in boosters_50.items():

            result = calculate_boosters(
                base_value,
                dungeon_percent
            )

            response += (
                f"🔹 Ascension **{level} → {level + 1}**\n"
                f"   Dungeon 50%: **{base_value:,}**\n"
                f"   Dungeon {dungeon_percent:.0f}%: "
                f"**{result:,.2f} Boosters**\n\n"
            )

        await ctx.send(response)
        return


    # ========================================================
    # SI SOLO SE INDICA START_LEVEL
    # ========================================================

    if start_level is not None and end_level is None:

        end_level = start_level + 1


    # ========================================================
    # VALIDAR RANGO
    # ========================================================

    if start_level >= end_level:

        await ctx.send(
            "❌ El nivel inicial debe ser menor que el nivel final.\n\n"
            "Ejemplo:\n"
            "`!dungeon 130 5 6`"
        )
        return


    # ========================================================
    # VALIDAR QUE EXISTAN LOS NIVELES
    # ========================================================

    missing_levels = []

    for level in range(start_level, end_level):

        if level not in boosters_50:

            missing_levels.append(level)


    if missing_levels:

        await ctx.send(
            "❌ No tengo datos para las siguientes ascensiones: "
            + ", ".join(
                f"{x} → {x + 1}"
                for x in missing_levels
            )
        )

        return


    # ========================================================
    # CALCULAR ASCENSIONES
    # ========================================================

    response = (
        f"🏰 **Cálculo de Dungeon {dungeon_percent:.0f}%**\n\n"
    )

    total_base = 0
    total_result = 0

    for level in range(start_level, end_level):

        base_value = boosters_50[level]

        result = calculate_boosters(
            base_value,
            dungeon_percent
        )

        total_base += base_value
        total_result += result

        response += (
            f"🔹 Ascension **{level} → {level + 1}**\n"
            f"📦 Dungeon 50%: **{base_value:,} Boosters**\n"
            f"🔥 Dungeon {dungeon_percent:.0f}%: "
            f"**{result:,.2f} Boosters**\n\n"
        )


    # ========================================================
    # SI HAY MÁS DE UNA ASCENSIÓN
    # MOSTRAR TOTAL
    # ========================================================

    if end_level - start_level > 1:

        total_calculated = calculate_boosters(
            total_base,
            dungeon_percent
        )

        response += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **TOTAL**\n"
            f"📦 Dungeon 50%: **{total_base:,} Boosters**\n"
            f"🔥 Dungeon {dungeon_percent:.0f}%: "
            f"**{total_calculated:,.2f} Boosters**"
        )


    await ctx.send(response)


# ============================================================
# COMANDO BOOSTER
# ============================================================
#
# Este comando está desactivado.
# Si alguien intenta usarlo, se le indica el comando correcto.
#
# ============================================================

@bot.command(name="booster")
async def booster_disabled(ctx, *args):

    await ctx.send(
        "❌ El comando `!booster` ya no se utiliza.\n\n"
        "Usa el comando:\n"
        "`!dungeon <Dungeon%>`\n\n"
        "Ejemplo:\n"
        "`!dungeon 130`\n\n"
        "Para una ascensión específica:\n"
        "`!dungeon 130 5 6`"
    )


# ============================================================
# HELP
# ============================================================

@bot.command(name="help")
async def custom_help(ctx):

    await ctx.send(
        "📖 **LastChaos EXP Calculator**\n\n"
        "🏰 **Calcular todas las ascensiones:**\n"
        "`!dungeon 130`\n\n"
        "🏰 **Calcular una ascensión:**\n"
        "`!dungeon 130 5 6`\n\n"
        "🏰 **También puedes usar:**\n"
        "`!dungeon 130 5`\n\n"
        "💡 Puedes usar cualquier Dungeon:\n"
        "`50` · `100` · `130` · `200` · `250`..."
    )


# ============================================================
# ON READY
# ============================================================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"BOT CONECTADO: {bot.user}")
    print("=" * 50)
    print("Sistema de cálculo Dungeon activo.")
    print("Ejemplo: !dungeon 130 5 6")


# ============================================================
# INICIAR BOT
# ============================================================

TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:

    print("❌ ERROR: No se encontró DISCORD_TOKEN")

else:

    bot.run(TOKEN)
