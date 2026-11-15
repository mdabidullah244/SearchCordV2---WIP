from cache import profile_cache
import random
import psycopg
import discord
from discord import app_commands
from discord.ext import commands

# --- Vars and helper functions ---
username_placeholders = [
    "What's your username gonna be?",
    "Enter something wimpus would love!",
    "Go on, enter your username!"
]
biography_placeholders = [
    "Anything interesting gonig on?",
    "What're you most excited for?",
    "Maybe your birthday?",
    "Something you love... or hate"
]
bias_placeholders = [
    "Who's your fav character?", 
    'Who do you look up to the most?',
    'Put someone cool!'
]
footer_text = [
    "Use '/help' if you're curious about something!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "Want to search up your favorite anime? Use '/search'⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
    "Check out someone's profile using '/view'!⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ "
]

def embed_gen(title: str, author_icon_urL: str, footer_text: str):
    embed = discord.Embed(color = discord.Color.from_str('#FFFFFF'))
    embed.set_author(name = title, icon_url = author_icon_urL)
    embed.set_footer(text = footer_text)
    return embed
# ----------------------------------

# --- EDIT MODAL ---
class editModal(discord.ui.Modal, title = 'Profile | Edit'):
    username = discord.ui.Label(
        text = 'Username',
        component = discord.ui.TextInput(placeholder=random.choice(username_placeholders), required=False)
    )
    biography = discord.ui.Label(
        text = 'Biography',
        component = discord.ui.TextInput(placeholder=random.choice(biography_placeholders), required=False)
    )
    bias = discord.ui.Label(
        text = 'Bias',
        component = discord.ui.TextInput(placeholder=random.choice(bias_placeholders), required=False)
    )

    async def on_submit(self, interaction: discord.Interaction):
        # if 'username' or the other variables are empty then it translates to an empty string ''
        # which is perfect for our helper function in 'profile_cache'
        username = self.username.component.value.strip()
        biography = self.biography.component.value.strip()
        bias = self.biography.component.value.strip()

        try:
            user_info = await profile_cache.edit_profile(interaction.user.id, username, biography, bias)
            if user_info == 'NO_INPUT':
                embed = embed_gen("Profile | Look's like you didn't make any changes!", interaction.user.avatar, random.choice(footer_text))
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            if user_info is None:
                embed = embed_gen("Profile | Look's like you don't have a profile!", interaction.user.avatar, "Use '/profile' to create your profile")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = embed_gen('Profile | Edit Successful', interaction.user.avatar, random.choice(footer_text))
            embed.set_thumbnail(url=interaction.user.avatar)
            embed.add_field(name='Username', value=user_info[0], inline=False)
            embed.add_field(name='Bias', value=user_info[2], inline=False)
            embed.add_field(name='Bio', value=user_info[1], inline=False)
            await interaction.response.send_message(embed=embed)
        except psycopg.Error as error: # ERROR
            print(f'\nEDIT PROFILE postgresql ERROR: {error}\n')
            embed = embed_gen('Profile | Edit Error', interaction.user.avatar, 'Fixing things up...')
            embed.add_field(name = 'ERROR', value = "This usually happens when you didn't setup your profile using '/profile'")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
# -------------------

# --- MAIN COMMAND ---
class editCog(commands.Cog):
    def __init__(self):
        super().__init__()

    @app_commands.command(name = 'edit', description = 'Edit your profile')
    @app_commands.checks.cooldown(1, 5.0, key = lambda interaction: (interaction.user.id))
    async def edit(self, interaction: discord.Interaction):
        await interaction.response.send_modal(editModal())

    @edit.error # ERROR
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = embed_gen('Profile | Cooldown', interaction.user.avatar, f'Retry after {int(error.retry_after)} seconds')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        print(f'\nEDIT command ERROR: {error}\n')
        embed = embed_gen('Profile | Unknown Error', interaction.user.avatar, 'Fixing things up...')
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(editCog())
# -------------------