import nextcord
from nextcord.ext import commands
import requests
import os

# === CONFIG ===
TOKEN = os.getenv("TOKEN")
API_ADD = "https://doj-backend-ac2o.onrender.com/api/add_schedule"
API_JSON = "https://doj-backend-ac2o.onrender.com/schedule.json"
# =====================

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents)


# -------------------------
# EVENT: BOT READY
# -------------------------
@bot.event
async def on_ready():
    print(f"Slash DOJ bot online jako {bot.user}")
    try:
        synced = await bot.sync_all_application_commands()
        print("Slash commands zsynchronizowane.")
    except Exception as e:
        print(f"Błąd sync: {e}")


# -------------------------
# /rozprawa
# -------------------------
@bot.slash_command(
    name="rozprawa",
    description="Dodaje nową rozprawę DOJ"
)
async def rozprawa(
    inter: nextcord.Interaction,
    sedzia: str,
    prokurator: str,
    sala: str,
    oskarzony: str,
    adwokat: str,
    data: str,
    godzina: str,
    opis: str
):

    await inter.response.defer()

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
        r = requests.post(API_ADD, json=payload)

        if r.status_code == 200:
            await inter.followup.send("✔ Rozprawa dodana do DOJ.")
        else:
            await inter.followup.send(f"❌ Błąd API: {r.status_code}")

    except Exception as e:
        await inter.followup.send(f"❌ Problem z połączeniem: {e}")


# -------------------------
# /usun_rozprawe
# -------------------------
@bot.slash_command(
    name="usun_rozprawe",
    description="Usuwa rozprawę po ID"
)
async def usun_rozprawe(inter: nextcord.Interaction, id: int):

    await inter.response.defer()

    try:
        # Pobieramy json
        data = requests.get(API_JSON).json()

        # Szukamy rekordu
        new_data = [item for item in data if item["id"] != id]

        if len(new_data) == len(data):
            await inter.followup.send("❌ Nie znaleziono rozprawy o takim ID.")
            return

        # Nadpisujemy plik — back-end musi mieć endpoint DELETE lub update!
        requests.post(
            "https://doj-backend-ac2o.onrender.com/api/overwrite",
            json=new_data
        )

        await inter.followup.send(f"🗑 Rozprawa {id} została usunięta.")

    except Exception as e:
        await inter.followup.send(f"❌ Błąd: {e}")


bot.run(TOKEN)

