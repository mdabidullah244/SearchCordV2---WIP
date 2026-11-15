from api import get_manga
from cache import anime_entries_cache
import aiohttp
import psycopg
from psycopg.types.json import Jsonb

api_cache = {}
manga_entries_reading = {}
manga_entries_will_read = {}
manga_entries_read = {}
manga_char_bias = {}
with open('psycopg_password.txt') as psycopg_password:
    psycopg_password = psycopg_password.read().strip()

async def valid_manga(session: aiohttp.ClientSession, manga_name: str):
    '''
    we need to check if the manga exists in the temp cache first
        if manga exists in temp cache then return manga info
    
    if the manga does not exist within the cache,
    it does not mean it does not exist at all
    we need to check our database for the manga info
        if manga exists in database then return manga info
        if manga does not exist in database then search manga
            if manga does not exist at all then return None
        update the database with manga info
        update the cache with manga info
        return manga info 
    '''
    if manga_name in api_cache:
        return api_cache[manga_name]

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
                SELECT manga_info
                FROM manga_api_cache
                WHERE manga_name = %s
                """,
                (manga_name,)
            )

            manga_info_db = await cursor.fetchone()

            if manga_info_db is None:

                manga_info_api = await get_manga(session, manga_name)
                if manga_info_api is None:
                    return None

                await cursor.execute(
                    """
                    INSERT INTO manga_api_cache(manga_name, manga_info)
                    VALUES (%s, %s)
                    ON CONFLICT (manga_name) DO NOTHING
                    """,
                    (manga_name, Jsonb(manga_info_api))
                )
                api_cache[manga_name] = manga_info_api
                return api_cache[manga_name]
    api_cache[manga_name] = manga_info_db[0]
    return api_cache[manga_name]

async def get_status(duID: int, status: str):
    if status == "reading":
        return manga_entries_reading.get(duID)
    if status == 'will_read':
        return manga_entries_will_read.get(duID)
    if status == 'read':
        return manga_entries_read.get(duID)

async def set_status(duID: int, manga_name, status: str):
    if status == 'reading':
        manga_entries_reading[duID] = manga_name
        return
    if status == 'will_read':
        manga_entries_will_read[duID] = manga_name
        return
    if status == 'read':
        manga_entries_read[duID] = manga_name
        return

async def remove_manga_status(duID: int, manga_name: str, status: str):
    get_status_info = await get_status(duID, status)
    
    if get_status_info is None:
        return False
    if manga_name not in get_status_info:
        return False

    get_status_info.remove(manga_name)
    return True
    

async def add_manga(session: aiohttp.client.ClientSession, duID: int, manga_name: str, status: str):
    '''
    every time the user tries to add a manga to their entry
    we need to check if that manga already exists

    we can first check the cache and then the database
        if the cache has the manga then we dont add manga, return False
    
    just because cache might not have manga does not mean database does not have manga
    so now we check the database if it has manga
        if database has manga respectve to status return False
    
    the database might not have manga respective to status
    which then we have exhuasted two assumptions: manga not in cache nor in database
    so now we can add manga to database and then to cache
        add manga to database
        add manga to cache
    '''
    get_status_info = await get_status(duID, status)
    if get_status_info is not None and manga_name in get_status_info: # CHANGE ALSO ADD ANIME
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
                """
                SELECT manga_name, status
                FROM users_manga
                WHERE user_id = %s
                """,
                (duID,)
            )

            manga_info_db = set(await cursor.fetchall())
            '''
            manga_inf_db should be tupiles,
            ('naruto', 'watched'), ('bleach', 'watching')
            where for each tupile, tupile[0] is manga name
            and tupile[1] is status
            '''
            '''
            now this looks like,
            {('naruto', 'watched), ('bleach', 'watching')}
            '''
            if (manga_name, status) in manga_info_db:
                return False

            await cursor.execute(
                """
                INSERT INTO users_manga(user_id, manga_name, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, manga_name) DO NOTHING
                """,
                (duID, manga_name, status)
            )

            if cursor.rowcount == 0:
                return False
            
    if get_status_info is None:
        get_status_list = [
            name for name, status_check in manga_info_db if status_check == status
        ]
        get_status_list.append(manga_name)
        await set_status(duID, get_status_list, status)
        return True
    get_status_info.append(manga_name)
    return True

async def get_manga_bias():
    return manga_char_bias

async def set_bias(duID: int, char_name: str, char_thumbnail: str):
    '''
    when we set a bias for a user,
    it does not matter if the cache nor the database is empty
    we simply just update their bias, nothing else
    
    however it depends if the char_name is already within the database
    we assume that the char_name is NOT within the database nor in the cache

    if char_name in manga bias cache,
        return False
    if char_name in anime bias cache,
        return False
    note that the above works because the cache is only ever
    updated AFTER checking the database
    if we were to check if the char_name was not in manga bias cache
    would be wrong because our cache resets every time our bot resets

    if char_name in database,
        return False
    update bias in database

    the updating logic for the database is going to be
    that we return what we updated
    we dont need to see if char_name is equal to what we updated
    this is because what we return after updating will always
    be the same thing as char_name

    check if char_name not in manga bias cache,
        update char_name in manga bias cache
    check if char_name not in anime bias cache,
        update char_name in anime bias cache
    '''
    anime_char_bias = await anime_entries_cache.get_anime_bias()
    if manga_char_bias.get(duID) == (char_name, char_thumbnail) or anime_char_bias.get(duID) == (char_name, char_thumbnail):
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
                """
                UPDATE users
                SET bias = %s, bias_thumbnail = %s
                WHERE user_id = %s
                """,
                (char_name, char_thumbnail, duID)
            )
    manga_char_bias[duID] = (char_name, char_thumbnail)
    anime_char_bias[duID] = (char_name, char_thumbnail)
    return True

    

async def remove_manga(duID: int, manga_name: str, status: str):
    get_status_info = await get_status(duID, status)

    '''
    just because the cache is empty does not entail
    that the database does not hold some manga x

    the bot could restart, making the cache empty
    while having some manga x within the database
    meaning that if the user were to run remove_manga(...)
    then we can't simply rely on the cache!

    removing some manga x ALWAYS requires using the database first

    make a tracker variable that tracks if something got deleted
    assume some manga x does not exists in database and cache
        if some manga x exists in database,
            remove manga x from database
            tracker = true
        if some manga x exists in cache,
            remove manga x from cache
            tracker = true
    
    return tracker
    '''

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
                DELETE FROM users_manga
                WHERE user_id = %s
                    AND manga_name = %s
                    AND status = %s
                RETURNING manga_name
                """,
                (duID, manga_name, status)
            )

            manga_info_db = await cursor.fetchone()
            
            if get_status_info is not None and manga_name in get_status_info:
                get_status_info.remove(manga_name)

            if manga_info_db is not None:
                return True
    return False