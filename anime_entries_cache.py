from api import get_anime
from cache import manga_entries_cache
import aiohttp
import psycopg
from psycopg.types.json import Jsonb

api_cache = {}
anime_entries_watching = {}
anime_entries_will_watch = {}
anime_entries_watched = {}
anime_char_bias = {}
with open('psycopg_password.txt') as psycopg_password:
    psycopg_password = psycopg_password.read().strip()

# if the anime is found within the databases then simply return
# if it is not found, then we need to make sure we are adding them to the appropate database
# --- VALID ANIME ---
async def valid_anime(session: aiohttp.ClientSession, anime_name: str):
    # first check if the anime already exists in the temp cache
    if anime_name in api_cache:
        return api_cache[anime_name]

    # second check if the anime exists within the database
    async with await psycopg.AsyncConnection.connect(
        dbname = 'searchcord',
        user = 'postgres',
        password = psycopg_password,
        host = 'localhost',
        port = 5432
    ) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                """
                SELECT anime_info
                FROM anime_api_cache
                WHERE anime_name = %s
                """,
                (anime_name,)
            )

            result = await cursor.fetchone()

            # if the restul returns nothing then that means that the anime is not within the database
            if result is None:
                # meaning now we need to search up with the anime using 'get_anime()' from the 'api' folder
                anime_info = await get_anime.get_anime(session, anime_name)

                # however notice the anime could still be 'None' meaning it does not exist at all!
                if anime_info is None:
                    return None

                # if the anime was found then store it in the pyscopg database
                await cursor.execute(
                    """
                    INSERT INTO anime_api_cache (anime_name, anime_info)
                    VALUES (%s, %s)
                    ON CONFLICT (anime_name) DO NOTHING
                    """,
                    (anime_name, Jsonb(anime_info))
                )
            else:
                anime_info = result[0]

    # Store the anime info from either the database or API in memory.
    api_cache[anime_name] = anime_info
    return anime_info
# --- VALID ANIME END ---


# --- ADD ANIME | Help Function: Gets temp cache based on status of the anime ---
async def get_profile_cache(duID: int, status: str):
    if status == 'watching':
        return anime_entries_watching.get(duID)
    if status == 'will_watch':
        return anime_entries_will_watch.get(duID)
    if status == 'watched':
        return anime_entries_watched.get(duID)
# --- ADD ANIME | Help Function: Gets temp cache based on status of the anime END ---

# --- ADD ANIME | Help Function: Sets temp cache based on status of the anime ---
async def set_profile_cache(duID: int, result, status: str):
    if status == 'watching':
        anime_entries_watching[duID] = result
        return
    if status == 'will_watch':
        anime_entries_will_watch[duID] = result
        return
    if status == 'watched':
        anime_entries_watched[duID] = result
        return 
# --- ADD ANIME | Help Function: Sets temp cache based on status of the anime END ---    

# --- ADD ANIME ---
async def add_anime(duID: int, anime_name: str, status: str):
    # first check if the anime profile cache has the information of all the anime's in the temp cache
    get_status_info = await get_profile_cache(duID, status)
    if get_status_info is not None and anime_name in get_status_info:
        return False
        # but what about now if anime_name is not in cached_anime?
        # well if it is not in cached_anime it means we have to add it!
        # so we keep going with the program

    # if 'cached_anime' is 'None' then the temp cache stores no info
    # hence we continue with the program

    # check if 'valid_anime', if so return, if not then continue

    # at this point all saftey checks have been done, we can now safely proceed
    # with adding the anime to the user's anime entries
    async with await psycopg.AsyncConnection.connect(
        dbname = 'searchcord',
        user = 'postgres',
        password = psycopg_password,
        host = 'localhost',
        port = 5432
    ) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                """
                SELECT anime_name, status
                FROM users_anime
                WHERE user_id = %s
                """,
                (duID,)
            )

            anime_info_db = set(await cursor.fetchall())
            if (anime_name, status) in anime_info_db:
                return False

            await cursor.execute(
                """
                INSERT INTO users_anime(user_id, anime_name, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, anime_name, status) DO NOTHING
                """,
                (duID, anime_name, status)
            )

            if cursor.rowcount == 0:
                return False
            
    if get_status_info is None:
        get_status_list = [
            name for name, status_check in anime_info_db if status_check == status
        ]
        get_status_list.append(anime_name)
        await set_profile_cache(duID, get_status_list, status)
        return True
    get_status_info.append(anime_name)
    return True
# --- ADD ANIME END ---

async def get_anime_bias():
    return anime_char_bias

# --- ADD BIAS ---
async def set_bias(duID: int, char_name: str, char_thumbnail: str) -> bool:
    manga_char_bias = await manga_entries_cache.get_manga_bias()
    if anime_char_bias.get(duID) == (char_name, char_thumbnail) or manga_char_bias.get(duID) == (char_name, char_thumbnail):
        return False

    async with await psycopg.AsyncConnection.connect(
        dbname = 'searchcord',
        user = 'postgres',
        password = psycopg_password,
        host = 'localhost',
        port = 5432
    ) as connection:
        async with connection.cursor() as cursor:

            await cursor.execute(
                '''
                UPDATE users
                SET bias = %s, bias_thumbnail = %s
                WHERE user_id = %s
                ''',
                (char_name, char_thumbnail, duID)
            )

    anime_char_bias[duID] = (char_name, char_thumbnail)
    manga_char_bias[duID] = (char_name, char_thumbnail)
    return True

# --- ADD BIAS END ---

# --- REMOVE ANIME | HELPER FUNCTION --- 
# this is going to be useful later on when we're dealing with deleting a users anime entries cache entirely
# but other then that we need to just remove the anime inside of the cache as of right now
# meaning
'''
say for example, the user wants to remove an anime from the 'watching' status
their dict would
{
    123 : ['naruto', 'bleach']
}

and say they want to remove 'bleach' then it would look like

    123: ['naruto', 'bleach']
'''
async def remove_all_profile_cache(duID: int, status: str):
    if status == 'watching':
        anime_entries_watching.pop(duID, None)
    if status == 'will_watch':
        anime_entries_will_watch.pop(duID, None)
    if status == 'watched':
        anime_entries_watched.pop(duID, None)

async def remove_anime_status(duID: int, anime_name: str, status: str):
    user_entries = get_profile_cache(duID, status)

    if user_entries is None:
        return False
    if anime_name not in user_entries:
        return False

    user_entries.remove(anime_name)
    return True

# --- REMOVE ANIME ---
async def remove_anime(duID: int, anime_name: str, status: str):
    if status not in ('watching', 'will_watch', 'watched'):
        return False
    # first check if the anime is already removed from the user's database
    # then check if its been removed from the user's temp cache
    # if both of them have been removed only then return 'True'

    cached_anime = await get_profile_cache(duID, status)

    async with await psycopg.AsyncConnection.connect(
        dbname = 'searchcord',
        user = 'postgres',
        password = psycopg_password,
        host  = 'localhost',
        port = 5432
    ) as connection:
        async with connection.cursor() as cursor:

            # before we can even check if the anime is already removed
            # we need to check if there is any data to remove in the first place
            await cursor.execute(
                """
                SELECT anime_name
                FROM users_anime
                WHERE user_id = %s
                    AND anime_name = %s
                    AND status = %s
                """,
                (duID, anime_name, status)
            )
            result = await cursor.fetchone()

            # if both of these are 'None' then there is nothnig to remove!
            # also note that 'cached_anime' only checks if theres anything to remove
            # it does not check for the case if the anime the user wants to remove
            # is actually inside of the cache itself
            if result is None and cached_anime is None:
                return False

            # but what if 'result' is 'None' and the temp is not None?
            # and what if result is not None and temp is None?
            # then the data is in at least one of the two

            # assume that the result is not None so check for the case where the result is None
            if result is None and cached_anime is not None:
                # since there exsists no information in the main database,
                # we can completely remove the info from the temp cache
                # this works becuase if they do have information stored within the temp cache
                # and its not an anime that they actually have within their respective status dict
                # then we can't remove it!
                return await remove_anime_status(duID, anime_name, status)

            # we now continue the program with the assumption that 'result' is not 'None'
            # since result is not None then we would be solving
            # 'if result is not None and cache_info is None'
            # since we already considered the case where result is None and cache_info is None

            # now we need to remove the data from the databse
            # meaning remove the anime_name and the status from the database

            # so we're deleting the anime_name respective to it's status ('watching', 'will_watch', or 'watched')
            await cursor.execute(
                """
                DELETE FROM users_anime
                WHERE user_id = %s
                    AND anime_name = %s
                    AND status = %s
                """,
                (duID, anime_name, status)
            )

    await remove_anime_status(duID, anime_name, status)
    return True   
    
# --- REMOVE ANIME END ---