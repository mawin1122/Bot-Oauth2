import nextcord
from nextcord.ext import commands
from datetime import datetime
import json

bot = commands.Bot(
    command_prefix='!',
    help_command=None,
    intents=nextcord.Intents.all(),
    strip_after_prefix=True,
    case_insensitive=True
)

class Verification(nextcord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(nextcord.ui.Button(
            label='Verification',
            url='http://localhost:5000/',  # URL ที่คุณต้องการให้เป็นลิงก์
            style=nextcord.ButtonStyle.link,  # เลือกสไตล์เป็น link
        ))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(
    name='verification_set',
    description='verification_set'
)
async def set_verify(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:  # ตรวจสอบว่าผู้ใช้มีสิทธิ์เป็นเอดมินหรือไม่
        return await interaction.response.send_message(content='[ERROR] No Permission For Use This Command.', ephemeral=True)
    verificationmber = nextcord.Embed()
    verificationmber.description = f'''
```
Start Bot verification
```
'''
    verificationmber.color = nextcord.Color.green()

    embed = nextcord.Embed()
    embed.description = f'''
```
กดปุ่มเพื่อนำทางคุณไปยังเว็บไซยืนยันตัวตน
```
'''
    embed.color = nextcord.Color.green()
    await interaction.response.send_message(embed=verificationmber, ephemeral=True)
    await interaction.channel.send(embed=embed, view=Verification())


@bot.slash_command(
    name='verification_stats',
    description='Check verification statistics'
)
async def check_verification_stats(interaction: nextcord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(content='[ERROR] No Permission For Use This Command.', ephemeral=True)
    
    # Load user data from JSON
    with open('./data/user_data.json', 'r') as f:
        data = json.load(f)

    # Count total users
    total_users = len(data.get('users', {}))

    # Prepare a list of embed fields for each user
    user_fields = []
    for username, user_data in data.get('users', {}).items():
        timestamp = user_data.get('timestamp', 'N/A')
        user_fields.append(f"```Username: {username}\nTimestamp: {timestamp}```")

    # Create an embed to display the information
    embed = nextcord.Embed(
        title="Verification Statistics",
        description=f"```Total Users: {total_users}```",
        color=nextcord.Color.green()
    )

    # Add fields for each user
    for field in user_fields:
        embed.add_field(name="User Information", value=field, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)



bot.run("bot_token")  # Replace with your bot token
