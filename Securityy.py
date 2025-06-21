import os
import discord
from discord.ext import commands
from flask import Flask
import threading

# Whitelist
WHITELIST_ROLE_ID = 1384171852087169052 # Ersetze durch Admin-Rolle
WHITELIST_USER_ID = 843180408152784936 # Deine Discord-ID

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Flask-Teil für UptimeRobot ---
app = Flask("")

@app.route("/")
def home():
    return "Bot läuft!", 200

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# --- Discord Bot Teil ---
@bot.event
async def on_ready():
    print(f"✅ Bot gestartet als {bot.user}")

@bot.event
async def on_guild_role_delete(role):
    async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
        if entry.user and not entry.user.bot:
            if WHITELIST_ROLE_ID in [r.id for r in entry.user.roles] or entry.user.id == WHITELIST_USER_ID:
                return
            try:
                await role.guild.timeout(entry.user, duration=3600, reason="Rolle gelöscht ohne Berechtigung")
                print(f"⛔ {entry.user} wurde für 1 Stunde getimeoutet (Rolle gelöscht)")
            except Exception as e:
                print(f"Fehler beim Timeout (Rolle): {e}")

@bot.event
async def on_guild_channel_delete(channel):
    async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        if entry.user and not entry.user.bot:
            if WHITELIST_ROLE_ID in [r.id for r in entry.user.roles] or entry.user.id == WHITELIST_USER_ID:
                return
            try:
                await channel.guild.timeout(entry.user, duration=3600, reason="Kanal gelöscht ohne Berechtigung")
                print(f"⛔ {entry.user} wurde für 1 Stunde getimeoutet (Kanal gelöscht)")
            except Exception as e:
                print(f"Fehler beim Timeout (Kanal): {e}")

@bot.event
async def on_message(message):
    return  # Ignoriere alle Nachrichten

# --- Start Bot + Flask ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    TOKEN = os.getenv("TOKEN")  # Sicherer Zugriff aus Render (nicht im Code)
    bot.run(TOKEN)
