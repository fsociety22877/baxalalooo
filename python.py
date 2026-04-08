import discord
from discord.ext import commands
import json
import os
import random
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN', 'YOUR_TOKEN_HERE')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_KEY')
DEEPINFRA_API_KEY = os.getenv('DEEPINFRA_API_KEY', 'YOUR_DEEPINFRA_KEY')

# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

# Data management
def load_data(file):
    if not os.path.exists('data'): 
        os.makedirs('data')
    path = f'data/{file}'
    if not os.path.exists(path): 
        return {}
    with open(path, 'r', encoding='utf-8') as f: 
        return json.load(f)

def save_data(file, data):
    if not os.path.exists('data'): 
        os.makedirs('data')
    path = f'data/{file}'
    with open(path, 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

# Bot ready event
@bot.event
async def on_ready():
    print(f'🔥 بەخە لالۆ ئامادەیە | {bot.user}')
    await bot.change_presence(
        activity=discord.Streaming(name="Baxa's Empire 🛠️", url="https://twitch.tv/baxalalo")
    )

# --- 🛡️ MODERATION COMMANDS ---

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str = "10m", *, reason=None):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not role:
        role = await ctx.guild.create_role(
            name="Muted",
            permissions=discord.Permissions(send_messages=False, speak=False)
        )
    await member.add_roles(role)
    await ctx.send(f"🔇 **{member.mention}** دەمی بەسترا بۆ {duration}")

@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role:
        await member.remove_roles(role)
        await ctx.send(f"🔊 **{member.mention}** دەمی لاب را.")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 **{member.mention}** بەیەکجاری دەرکرا.")

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"👢 **{member.mention}** بەدەرکرا.")

@bot.command(name='clear')
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 **{amount}** نامە سڕدرایەوە.", delete_after=3)

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, duration: str, *, reason=None):
    minutes = int(duration.replace('m', ''))
    timeout_duration = datetime.timedelta(minutes=minutes)
    await member.timeout(timeout_duration, reason=reason)
    await ctx.send(f"⏳ **{member.mention}** وەستاندرا بۆ {duration}")

@bot.command(name='warn')
@commands.has_permissions(manage_guild=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    warnings = load_data('warnings.json')
    user_id = str(member.id)
    if user_id not in warnings:
        warnings[user_id] = []
    
    warnings[user_id].append({
        'reason': reason or 'No reason',
        'date': datetime.datetime.now().isoformat(),
        'warned_by': str(ctx.author.id)
    })
    save_data('warnings.json', warnings)
    warn_count = len(warnings[user_id])
    await ctx.send(f"⚠️ **{member.mention}** ئاگاداریی {warn_count} بۆ: {reason}")

@bot.command(name='warnings')
async def warnings(ctx, member: discord.Member):
    warnings_data = load_data('warnings.json')
    user_id = str(member.id)
    
    if user_id not in warnings_data or not warnings_data[user_id]:
        await ctx.send(f"✅ **{member.mention}** هیچ ئاگاداریی نیە")
        return
    
    embed = discord.Embed(title=f"⚠️ ئاگاداریەکانی {member.name}", color=discord.Color.red())
    for i, warn in enumerate(warnings_data[user_id], 1):
        embed.add_field(
            name=f"ئاگاداری #{i}",
            value=f"**هۆکار:** {warn['reason']}\n**بەروار:** {warn['date']}",
            inline=False
        )
    await ctx.send(embed=embed)

# --- 🤖 AI COMMANDS ---

@bot.command(name='ask')
async def ask(ctx, *, prompt):
    async with ctx.typing():
        await ctx.reply(f"🤖 **بەخە:** تۆ پرسیار کردت: {prompt}\n(بۆ ئەم دەمە جێگر وەڵام)")

@bot.command(name='search')
async def search(ctx, *, query):
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    await ctx.send(f"🔍 بەخە بەدوای ({query}) دەگەڕێت...\n🌐 {search_url}")

@bot.command(name='canrun')
async def canrun(ctx, *, game):
    await ctx.reply(f"🎮 **پشکنینی گەیم:** {game} لەسەر مۆبایل و کۆمپیوتەری مامناوەند بە باشی ڕەن دەکات!")

# --- 💰 ECONOMY COMMANDS ---

@bot.command(name='shop')
async def shop(ctx):
    embed = discord.Embed(title="🛒 بازاڕی بەخە لالۆ", color=0x00ff00)
    embed.add_field(name="🥇 VIP", value="5000 Coins", inline=False)
    embed.add_field(name="⭐ Premium", value="3000 Coins", inline=False)
    embed.add_field(name="🎮 Gamer Role", value="1500 Coins", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='profile')
async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    economy = load_data('economy.json')
    user_id = str(member.id)
    
    if user_id not in economy:
        economy[user_id] = {'coins': 0, 'level': 1, 'xp': 0}
        save_data('economy.json', economy)
    
    user_data = economy[user_id]
    embed = discord.Embed(title=f"👤 پڕۆفایلی {member.name}", color=member.color or discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="💰 کۆین", value=f"{user_data['coins']}", inline=True)
    embed.add_field(name="⭐ ئاستی", value=f"{user_data['level']}", inline=True)
    embed.add_field(name="📈 تێبینی", value=f"{user_data['xp']}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='balance')
async def balance(ctx, member: discord.Member = None):
    member = member or ctx.author
    economy = load_data('economy.json')
    user_id = str(member.id)
    balance_amount = economy.get(user_id, {}).get('coins', 0)
    await ctx.send(f"💰 **{member.mention}** بالانسی: **{balance_amount}** کۆین")

@bot.command(name='work')
async def work(ctx):
    economy = load_data('economy.json')
    user_id = str(ctx.author.id)
    
    if user_id not in economy:
        economy[user_id] = {'coins': 0, 'level': 1, 'xp': 0}
    
    coins_earned = random.randint(100, 500)
    economy[user_id]['coins'] += coins_earned
    economy[user_id]['xp'] += random.randint(10, 50)
    save_data('economy.json', economy)
    
    await ctx.send(f"⛏️ **{ctx.author.mention}** کارکرد و **{coins_earned}** کۆین بەدەست هێنا!")

@bot.command(name='inv')
async def inv(ctx, member: discord.Member = None):
    member = member or ctx.author
    economy = load_data('economy.json')
    user_id = str(member.id)
    
    if user_id not in economy:
        await ctx.send(f"📦 **{member.mention}** سندوقی تاڵ دەکاتەوە...")
        return
    
    embed = discord.Embed(title=f"📦 سندوقی {member.name}", color=discord.Color.gold())
    embed.add_field(name="💰 کۆین", value=f"{economy[user_id]['coins']}", inline=True)
    embed.add_field(name="⭐ ئاستی", value=f"{economy[user_id]['level']}", inline=True)
    await ctx.send(embed=embed)

# --- 🎫 TICKET SYSTEM ---

@bot.command(name='ticket')
async def ticket(ctx):
    channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.name}')
    await channel.set_permissions(ctx.guild.default_role, read_messages=False)
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)
    
    embed = discord.Embed(title="🎫 تکێتی هاوکاری", description=f"سڵاو {ctx.author.mention}، چۆن یارمەتیت بدەم؟", color=discord.Color.blue())
    await channel.send(embed=embed)
    await ctx.send(f"✅ تکێتت دروست کرا: {channel.mention}")

# --- 🗣️ UTILITY COMMANDS ---

@bot.command(name='say')
@commands.has_permissions(administrator=True)
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name='botname')
@commands.is_owner()
async def botname(ctx, *, name):
    try:
        await bot.user.edit(username=name)
        await ctx.send(f"✅ ناو گۆڕدرا بۆ **{name}**")
    except Exception as e:
        await ctx.send(f"❌ هەڵە: {str(e)}")

@bot.command(name='botpfp')
@commands.is_owner()
async def botpfp(ctx):
    if not ctx.message.attachments:
        await ctx.send("❌ تکایە وێنەیەک بنێرە")
        return
    try:
        img = await ctx.message.attachments[0].read()
        await bot.user.edit(avatar=img)
        await ctx.send("✅ وێنەی بۆت گۆڕدرا")
    except Exception as e:
        await ctx.send(f"❌ هەڵە: {str(e)}")

@bot.command(name='autoresponder')
@commands.has_permissions(administrator=True)
async def autoresponder(ctx, action: str, trigger: str, *, response: str = None):
    auto = load_data('auto_responses.json')
    
    if action.lower() == 'add':
        if not response:
            await ctx.send("❌ لتکایە وەڵام دابنێ")
            return
        auto[trigger.lower()] = response
        save_data('auto_responses.json', auto)
        await ctx.send(f"✅ وەڵامی ئۆتۆ زیاد کرا بۆ: **{trigger}**")
    
    elif action.lower() == 'remove':
        if trigger.lower() in auto:
            del auto[trigger.lower()]
            save_data('auto_responses.json', auto)
            await ctx.send(f"✅ وەڵامی ئۆتۆ سڕدرا: **{trigger}**")
        else:
            await ctx.send("❌ ئەم وەڵامە نەدۆزرایەوە")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    auto = load_data('auto_responses.json')
    if message.content.lower() in auto:
        await message.channel.send(auto[message.content.lower()])
    
    await bot.process_commands(message)

# --- HELP COMMAND ---

@bot.command(name='commands')
async def commands_list(ctx):
    embed = discord.Embed(
        title="📜 لیستی فەرمانەکانی بەخە لالۆ",
        description="هەموو فەرمانەکان:",
        color=0x2b2d31
    )
    
    mod_list = (
        "🚫 **!mute** <user> [duration] [reason] - دەمبەستن\n"
        "🔊 **!unmute** <user> - لابردنی میوت\n"
        "🔨 **!ban** <user> [reason] - بە دەرکردن\n"
        "👢 **!kick** <user> [reason] - بەدەرکردن\n"
        "🧹 **!clear** <amount> - سڕینەوە\n"
        "⏳ **!timeout** <user> <duration> [reason] - وەستاندن\n"
        "⚠️ **!warn** <user> [reason] - ئاگاداری\n"
        "📋 **!warnings** <user> - دیتنی ئاگاداریەکان"
    )
    embed.add_field(name="🛡️ مۆدێرەیشن", value=mod_list, inline=False)
    
    ai_list = (
        "🤖 **!ask** <prompt> - پرسیار لە بەخە\n"
        "🔍 **!search** <query> - گەڕان\n"
        "��� **!canrun** <game> - پشکنینی گەیم"
    )
    embed.add_field(name="🧠 AI و گەڕان", value=ai_list, inline=False)
    
    eco_list = (
        "🛒 **!shop** - بازاڕ\n"
        "👤 **!profile** [user] - پڕۆفایل\n"
        "💰 **!balance** [user] - بالانس\n"
        "📦 **!inv** [user] - سندوق\n"
        "⛏️ **!work** - کار"
    )
    embed.add_field(name="💎 ئیکۆنۆمی", value=eco_list, inline=False)
    
    ticket_list = "🎫 **!ticket** - کردنەوەی تکێتی هاوکاری"
    embed.add_field(name="🎫 تکێت", value=ticket_list, inline=False)
    
    util_list = (
        "📢 **!say** <text> - قسە\n"
        "⚙️ **!botname** <name> - گۆڕینی ناوی بۆت\n"
        "🖼️ **!botpfp** - گۆڕینی وێنەی بۆت\n"
        "🤖 **!autoresponder** add/remove <trigger> [response] - ئۆتۆڕیسپۆندەر"
    )
    embed.add_field(name="🛠️ فەرمانە گشتی", value=util_list, inline=False)
    
    embed.set_footer(text="وەستا بەخە لالۆ • هەموو مافێکی پارێزراوە", icon_url=bot.user.avatar.url)
    
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)
