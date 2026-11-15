from cache import profile_cache
import psycopg
import random
import discord
from discord import app_commands
from discord.ext import commands

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

class deleteModal(discord.ui.Modal, title = 'Profle | Deletion'):
    auth = discord.ui.Label(
        text = 'Authorization',
        component = discord.ui.TextInput(placeholder="Enter 'DELETE' to delete your account", required=True)
    )

    async def on_submit(self, interaction: discord.Interaction):
        auth = self.auth.component.value.strip() if self.auth.component.value.strip() == 'DELETE' else ''
        if auth == '':
            embed = embed_gen('Profile | Deletion Canceled', interaction.user.avatar, random.choice(footer_text))
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            user_info = await profile_cache.delete_profile(interaction.user.id)
            if user_info == None:
                embed = embed_gen("Profile | Look's like you don't have a profile!", interaction.user.avatar, "Use '/profile' to create your profile")
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            embed = embed_gen('Profile | Deletion Successful', interaction.user.avatar, "If you want to make a profile again use '/profile'")
            await interaction.response.send_message(embed=embed)
        except psycopg.Error as error: # ERROR
            print(f'\nDELETE PROFILE postgresql ERROR: {error}\n')
            embed = embed_gen('Profile | Deletion Error', interaction.user.avatar, 'Fixing things up...')
            embed.add_field(name = 'ERROR', value = 'Something went wrong when we tried to delete your profile')
            await interaction.response.send_message(embed=embed, ephemeral=True)

class deleteCog(commands.Cog):
    def __init__(self):
        super().__init__()

    @app_commands.command(name = 'delete', description = "Delete's your profile")
    @app_commands.checks.cooldown(1, 5.0, key = lambda interaction: (interaction.user.id))
    async def delete(self, interaction: discord.Interaction):
        await interaction.response.send_modal(deleteModal())

    @delete.error # ERROR
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            embed = embed_gen('Profile | Cooldown', interaction.user.avatar, f'Retry after {int(error.retry_after)} seconds')
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        print(f'\nDELETE command ERROR: {error}\n')
        embed = embed_gen('Profile | Unknown Error', interaction.user.avatar, 'Fixing things up...')
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(deleteCog())