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
    description="Dodaj rozprawę do wokandy DOJ."
)
async def rozprawa(
    interaction: Interaction,
    sedzia: str = SlashOption(description="Imię i nazwisko sędziego"),
    prokurator: str = SlashOption(description="Imię i nazwisko prokuratora"),
    sala: str = SlashOption(description="Numer sali sądowej"),
    oskarzony: str = SlashOption(description="Oskarżony / pozwany"),
    adwokat: str = SlashOption(description="Adwokat"),
    data: str = SlashOption(description="Data rozprawy (np. 28.11.2025)"),
    godzina: str = SlashOption(description="Godzina rozprawy (np. 14:30)"),
    strony: str = SlashOption(description="Strony sprawy, np. SA vs Kowalski"),
    swiadkowie: str = SlashOption(
        description="Świadkowie (oddzieleni przecinkami, np.: Jan Kowalski, Adam Nowak)",
        required=False
    ),
    opis: str = SlashOption(description="Krótki opis sprawy")
):

    await interaction.response.defer(ephemeral=True)

    # Zamiana pustego testimony na "" zamiast None
    swiadkowie = swiadkowie or ""

    payload = {
        "name": f"{oskarzony} - {adwokat}",
        "judge": sedzia,
        "prosecutor": prokurator,
        "defendant": oskarzony,
        "lawyer": adwokat,
        "witnesses": swiadkowie,
        "room": sala,
        "date": data,
        "time": godzina,
        "parties": strony,
        "description": opis
    }

    try:
        r = requests.post(API_URL, json=payload)
        if r.status_code == 200:
            await interaction.followup.send(
                f"✔ **Dodano rozprawę:**\n"
                f"**{strony}** o {godzina} w sali {sala}\n"
                f"Sędzia: {sedzia}\n"
                f"Świadkowie: {swiadkowie or 'brak'}"
            )
        else:
            await interaction.followup.send(f"❌ Błąd API: {r.status_code}")
    except Exception as e:
        await interaction.followup.send(f"❌ Błąd połączenia z API: {e}")


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


