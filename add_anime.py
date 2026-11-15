from cache import anime_entries_cache
import random
import aiohttp
import psycopg
import discord
from discord import app_commands
from discord.ext import commands

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

class pagination():
    def __init__(self, interaction: discord.Interaction, anime_info):
        self.curr_page = 0
        self.max = 12
        self.interaction = interaction
        self.anime_info = anime_info

    def add_page(self):
        self.curr_page += 1
        return
    def sub_page(self):
        self.curr_page -= 1
        return

    def get_curr_page(self):
        return self.curr_page
    
    def set_page(self, page_num: int):
         self.curr_page = page_num

    def valid_page(self, page_num: int):
        return 0 <= page_num <= self.max

    def make_page(self, page_num: int):
        anime_name = f'{(self.anime_info.get('title') or {}).get('english')} | {(self.anime_info.get('title') or {}).get('native')}'
        anime_thumbnail = (self.anime_info.get('coverImage') or {}).get('extraLarge')
        anime_chars = (self.anime_info.get('characters') or {}).get('edges') or []
        if page_num == 0:
            anime_description = self.anime_info.get('description')
            anime_banner = self.anime_info.get('bannerImage')
            anime_status = self.anime_info.get('status')
            anime_episodes = self.anime_info.get('episodes')
            anime_duration = self.anime_info.get('duration')
            anime_avgscore = self.anime_info.get('averageScore')
            anime_seasonyear = self.anime_info.get('seasonYear')
            anime_format = self.anime_info.get('format')
            
            embed = embed_gen(anime_name, self.interaction.user.avatar, f'Page: {self.curr_page + 1} | General Information, Page 2 Has More!')
            embed.description = anime_description
            embed.add_field(name = 'Status', value = anime_status)
            embed.add_field(name = 'Episodes', value = anime_episodes)
            embed.add_field(name = 'Duration', value = anime_duration)
            embed.add_field(name = 'Score', value = anime_avgscore)
            embed.add_field(name = 'Season Year', value = anime_seasonyear)
            embed.add_field(name = 'Format', value = anime_format)

            if anime_thumbnail is not None:
                embed.set_thumbnail(url = anime_thumbnail)
            if anime_banner is not None:
                embed.set_image(url = anime_banner)
            
            return embed
        
        if page_num == 1:
            anime_source = self.anime_info.get('source')
            anime_genres = self.anime_info.get('genres')
            if anime_genres is not None:
                anime_genres = ', '.join(anime_genres)
            anime_site_url = self.anime_info.get('siteUrl')
            anime_trailer_site = (self.anime_info.get('trailer') or {}).get('site')

            embed = embed_gen(anime_name, self.interaction.user.avatar, f'Page: {self.curr_page + 1} | Bit More Detailed, Page 3 Has Characters!')            
            if anime_trailer_site is not None and anime_trailer_site == 'youtube':
                anime_trailer_id = (self.anime_info.get('trailer') or {}).get('id')
                embed.add_field(name = 'Trailer', value = f"https://www.youtube.com/watch?v={anime_trailer_id}", inline = False)
            else:
                embed.add_field(name = 'Trailer', value = "Look's like we're having a hard time finding one sorry!", inline = False)
            embed.set_thumbnail(url = anime_thumbnail)
            embed.add_field(name = 'Source', value = anime_source)
            embed.add_field(name = 'Genres', value = anime_genres)
            embed.add_field(name = 'AniList Site Url', value = anime_site_url, inline = False)

            return embed

        '''
        make a method that creates the character page to not repeat code and only make pages if needed
        since char page starts at 2, maybe itll be (page_num - 2) % 10? 
        '''
        if page_num == 2:
            char_role = anime_chars[0].get('role')
            char_name_full = anime_chars[0].get('node').get('name').get('full')
            char_name_native = anime_chars[0].get('node').get('name').get('native')

            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 3:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 4:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 5:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 6:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 7:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 8:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 9:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 10:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 11:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
        if page_num == 12:
            embed = embed_gen(anime_name, self.interaction.user.avatar, f"Page: {self.curr_page + 1} | From This Point On, It's All Characters!")
            return embed
    
    def get_page(self, page_num: int):
        '''
        every single time someone goes left or right, it'll run get_page
        which means that the check at the start works
        '''
        if self.valid_page(page_num) is False:
            return False
        return self.make_page(page_num)
        
class addAnimeSelection(discord.ui.Select):
    def __init__(self, duID: int, anime_info):
        self.duID = duID
        self.anime_info = anime_info
        self.anime_name = f'{(anime_info.get('title') or {}).get('english')} | {(anime_info.get('title') or {}).get('native')}'
        self.anime_thumbnail = (self.anime_info.get('coverImage') or {}).get('extraLarge')
        self.anime_banner = anime_info.get('bannerImage')

        options = [
            discord.SelectOption(label = 'Watching', value = 'watching'),
            discord.SelectOption(label = 'Will Watch', value = 'will_watch'),
            discord.SelectOption(label = 'Watched', value = 'watched')
        ]
        super().__init__(placeholder = 'Where does this anime go?', options = options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'watching':
            try:
                add_anime_result = await anime_entries_cache.add_anime(self.duID, self.anime_name, 'watching')
                if add_anime_result is False:
                    embed = embed_gen(self.anime_name, interaction.user.avatar, f'YOU ALREADY ADDED {self.anime_name} TO WATCHING')
                    embed.description = self.anime_info.get('description')

                    if self.anime_thumbnail is not None and self.anime_thumbnail is not {}:
                        embed.set_thumbnail(url = self.anime_thumbnail)
                    if self.anime_banner is not None and self.anime_banner is not {}:
                        embed.set_image(url = self.anime_banner)

                    await interaction.response.edit_message(embed = embed)
                    return
                embed = embed_gen(self.anime_name, interaction.user.avatar, f'ADDED {self.anime_name} TO WATCHING')
                embed.description = self.anime_info.get('description')

                if self.anime_thumbnail is not None and self.anime_thumbnail is not {}:
                    embed.set_thumbnail(url = self.anime_thumbnail)
                if self.anime_banner is not None and self.anime_banner is not {}:
                    embed.set_image(url = self.anime_banner)
                
                await interaction.response.edit_message(embed = embed)
            except psycopg.Error as error:
                print(f'\nADD ANIME add to watching list ERROR: {error}')
                embed = embed_gen('Watching Error', interaction.user.avatar, random.choice(footer_text))
                embed.add_field(name = 'ERROR', value = f'Something went wrong when adding {self.anime_name}')
                embed.set_thumbnail(url = self.anime_thumbnail)
                await interaction.response.send_message(embed = embed, ephemeral = True)
        if self.values[0] == 'will_watch':
            try:
                add_anime_result = await anime_entries_cache.add_anime(self.duID, self.anime_name, 'will_watch')
                if add_anime_result is False:
                    embed = embed_gen(self.anime_name, interaction.user.avatar, f'YOU ALREADY ADDED {self.anime_name} TO WILL WATCH')
                    embed.description = self.anime_info.get('description')
                    
                    if self.anime_thumbnail is not None and self.anime_thumbnail is not {}:
                        embed.set_thumbnail(url = self.anime_thumbnail)
                    if self.anime_banner is not None and self.anime_banner is not {}:
                        embed.set_image(url = self.anime_banner)
                    
                    await interaction.response.edit_message(embed = embed)
                    return
                embed = embed_gen(self.anime_name, interaction.user.avatar, f'ADDED {self.anime_name} TO WILL WATCH')
                embed.description = self.anime_info.get('description')

                if self.anime_thumbnail is not None and self.anime_thumbnail is not {}:
                    embed.set_thumbnail(url = self.anime_thumbnail)
                if self.anime_banner is not None and self.anime_banner is not {}:
                    embed.set_image(url = self.anime_banner)
                
                await interaction.response.edit_message(embed = embed)
            except psycopg.Error as error:
                print(f'\nADD ANIME add to will watch list ERROR: {error}')
                embed = embed_gen(f'Will Watch Error', interaction.user.avatar, random.choice(footer_text))
                embed.add_field(name = 'ERROR', value = f'Something went wrong when adding {self.anime_name}')
                embed.set_thumbnail(url = self.anime_thumbnail)
                await interaction.response.send_message(embed = embed, ephemeral = True)
        if self.values[0] == 'watched':
            try:
                add_anime_result = await anime_entries_cache.add_anime(self.duID, self.anime_name, 'watched')
                if add_anime_result is False:
                    embed = embed_gen(self.anime_name, interaction.user.avatar, f'YOU ALREADY ADDED {self.anime_name} TO WATCHED')
                    embed.description = self.anime_info.get('description')

                    if self.anime_thumbnail is not None and self.anime_thumbnail is not {}:
                        embed.set_thumbnail(url = self.anime_thumbnail)
                    if self.anime_banner is not None and self.anime_banner is not {}:
                        embed.set_image(url = self.anime_banner)
                    
                    await interaction.response.edit_message(embed = embed)
                    return
                embed = embed_gen(self.anime_name, interaction.user.avatar, f'ADDED {self.anime_name} TO WATCHED')
                embed.description = self.anime_info.get('description')

                if self.anime_thumbnail is not None and self.anime_thumbnail is not {}:
                    embed.set_thumbnail(url = self.anime_thumbnail)
                if self.anime_banner is not None and self.anime_banner is not {}:
                    embed.set_image(url = self.anime_banner)
                
                await interaction.response.edit_message(embed = embed)
            except psycopg.Error as error:
                print(f'\nADD ANIME add to watched list ERROR: {error}')
                embed = embed_gen(f'Watched Error', interaction.user.avatar, random.choice(footer_text))
                embed.add_field(name = 'ERROR', value = f'Something went wrong when adding {self.anime_name}.')
                embed.set_thumbnail(url = self.anime_thumbnail)
                await interaction.response.send_message(embed = embed, ephemeral = True)
# FIX THE CHECK FOR THUMBNAIL AND IMAGE

class prevButton(discord.ui.Button):
    def __init__(self, page, option_view):
        super().__init__(
            label = '<',
            style = discord.ButtonStyle.blurple
        )
        self.page = page
        self.option_view = option_view

    async def callback(self, interaction: discord.Interaction):
        if self.page.valid_page(self.page.get_curr_page() - 1) is False:
            embed = self.page.get_page(self.page.get_curr_page())
            await interaction.response.edit_message(embed = embed, view = self.view)
            return
        self.page.sub_page()
        if self.page.get_curr_page() < 2 and self.option_view not in self.view.children:
            self.view.add_item(self.option_view)
        embed = self.page.get_page(self.page.get_curr_page())
        await interaction.response.edit_message(embed = embed, view = self.view)

class nextButton(discord.ui.Button):
    def __init__(self, page, option_view):
        super().__init__(
            label = '>',
            style = discord.ButtonStyle.blurple
        )
        self.page = page
        self.option_view = option_view

    async def callback(self, interaction: discord.Interaction):
        if self.page.valid_page(self.page.get_curr_page() + 1) is False:
            embed = self.page.get_page(self.page.get_curr_page())
            await interaction.response.edit_message(embed = embed, view = self.view)
            return
        self.page.add_page()
        if self.page.get_curr_page() >= 2 and self.option_view in self.view.children:
            self.view.remove_item(self.option_view)
        embed = self.page.get_page(self.page.get_curr_page())
        await interaction.response.edit_message(embed = embed, view = self.view)

class addAnimeContainer(discord.ui.View):
    def __init__(self, duID: int, anime_info, page):
        super().__init__()
        self.duID = duID
        self.anime_info = anime_info
        self.page = page
        self.anime_selection_view = addAnimeSelection(self.duID, anime_info)
        self.add_item(self.anime_selection_view)
        self.add_item(prevButton(self.page, self.anime_selection_view))
        self.add_item(nextButton(self.page, self.anime_selection_view))

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.duID:
            embed = embed_gen('This Is Not Your Command', interaction.user.avatar, random.choice(footer_text))
            await interaction.response.send_message(embed = embed, ephemeral = True)
            return False
        return True


class addAnimeCog(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name = 'add_anime', description = "add an anime you're watching/will watch/watched")
    @app_commands.checks.cooldown(1, 5.0, key = lambda interaction: (interaction.user.id))
    async def add_anime(self, interaction: discord.Interaction, anime_name: str):
        try:
            anime_info = await anime_entries_cache.valid_anime(self.bot.session, anime_name)
            if anime_info is None:
                embed = embed_gen('Unknown Anime', interaction.user.avatar, random.choice(footer_text))
                embed.add_field(name = 'ERROR', value = f'{anime_name} does not exist! Try again with a real anime this time')
                await interaction.response.send_message(embed = embed, ephemeral = True)
                return

            anime_status = anime_info.get('status')
            anime_format = anime_info.get('format')
            anime_episodes = anime_info.get('episodes')
            anime_duration = anime_info.get('duration')
            anime_season_year = anime_info.get('seasonYear')
            anime_avgscore = anime_info.get('averageScore')


            embed = embed_gen(f'{anime_info.get('title', {}).get('english')} | {anime_info.get('title', {}).get('native')}', interaction.user.avatar, f'Page: 1 | General Information, Page 2 Has More!')
            embed.description = anime_info.get('description')
            embed.add_field(name = 'Status', value = anime_status)
            embed.add_field(name = 'Episodes', value = anime_episodes)
            embed.add_field(name = 'Duration', value = anime_duration)
            embed.add_field(name = 'Score', value = anime_avgscore)
            embed.add_field(name = 'Season Year', value = anime_season_year)
            embed.add_field(name = 'Format', value = anime_format)

            if anime_info.get('coverImage', {}).get('extraLarge') is not None:
                embed.set_thumbnail(url = anime_info.get('coverImage', {}).get('extraLarge'))
            if anime_info.get('bannerImage') is not None:
                embed.set_image(url = anime_info.get('bannerImage'))

            page = pagination(interaction, anime_info)
            await interaction.response.send_message(embed = embed, view = addAnimeContainer(interaction.user.id, anime_info, page))
        except psycopg.Error as error:
            print(f'\nADD ANIME anime_entries_cache\valid_anime ERROR: {error}')
            embed = embed_gen('Unknown Error', interaction.user.avatar, random.choice(footer_text))
            await interaction.response.send_message(embed = embed)

    @add_anime.error
    async def on_add_anime_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message("command on cooldown")

async def setup(bot):
    await bot.add_cog(addAnimeCog(bot))