import discord
from discord.ext import commands
import requests
import os

# === CONFIG ===
TOKEN = os.getenv("TOKEN")
API_URL = "https://doj-backend-ac2o.onrender.com/api/add_schedule"
# =====================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot DOJ zalogowany jako {bot.user}")


@bot.command()
async def rozprawa(
    ctx,
    sedzia,
    prokurator,
    sala,
    oskarzony,
    adwokat,
    data,
    godzina,
    *,
    opis
):
    payload = {
        "name": f"{oskarzony} - {adwokat}",
        "judge": sedzia,
        "prosecutor": prokurator,
        "defendant": oskarzony,
        "lawyer": adwokat,
        "witnesses": "",
        "room": sala,
        "date": data,
        "time": godzina,
        "parties": f"SA vs {oskarzony}",
        "description": opis
    }

    try:
        r = requests.post(API_URL, json=payload)

        if r.status_code == 200:
            await ctx.reply("✔ Rozprawa została dodana do DOJ (Render).")
        else:
            await ctx.reply(f"❌ Błąd API: {r.status_code}")

    except Exception as e:
        await ctx.reply(f"❌ Problem z połączeniem do API Render: {e}")


bot.run(TOKEN)

