import psycopg

profile_cache = {}
with open('psycopg_password.txt') as psycopg_password:
    psycopg_password = psycopg_password.read().strip()

# --- VALID PROFILE ---
# we need a function that simply determines if a profile exists
# this will be used in accordacne to other functions.
async def valid_profile(duID: int):
    # check if the users discord user id is in the profile cache
    if duID in profile_cache:
        return True

    # check if the user exisits within the database itself
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
                SELECT 1
                FROM users
                WHERE discord_user_id = %s
                """,
                (duID,)
            )

            # notice this literly just returns if 'user_info' (which would be 'user_info = cursor.fetchone()') != None
            # so if we wrote 'return await cursor.fetchone() is None' then it would check if user_info
            # is equal to None and if it is then it returns True
            # esseitnaly it checks given the condition and if the condition is satesified then return True
            # other wise return False
            return await cursor.fetchone() is not None
# --- VALID PROFILE END --- 

# --- GET PROFILE ---
# this function here will get the profile of a user depending on their discord user id
# check if the discord user id (unique key) exsists within the profile_cache dict

# if duID does then return that information (value coresponding to the key)
# if duID not in profile_cache then check if duID in database
#   if duID in database then insert duID and user info into the profile_cache dict
# if duID not in database
# return None 

async def get_profile(duID: int):
    if duID in profile_cache:
        return profile_cache[duID]

    # when we use 'with' we later on say what we use that 'as'
    # also this is simliar to how we did 'connection = psycopg.connect(...)'
    # instead, since this is asynchronous and we want to define our 'connectin' variable 
    # we use 'with' to essentially define 'psycopg.AsyncConnection.connect(...)
    # and set it equal to our 'connection' by doing 'as connection'

    # think of it like this 'LEFTVAR  = RIGHTVAR'
    # when asynchronous, 'async with {optional: await} RIGHTVAR as LEFTVAR'

    # since we WANT TO do something, we have to use 'await'
    # here, we WANT TO connect to psycopg as an asynchronous connection,
    # we do 'await psycopg.AsyncConnection.connect(...)
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
                SELECT username, biography, bias
                FROM users
                WHERE discord_user_id = %s
                """,
                (duID,)
            )
            user_info = await cursor.fetchone()

    # we put this 'if' statement OUTSIDE of the asynchronous commands
    # we can put inside the asynchronous command block, but keeping it outside
    # is better since the database connection as soon as the 'query' finishes

    # since these are just normal python commands, there's no need to have them run there
    # also it would be irrelavnet to have this 'if' statment within the asynchronous command
    # since those manipluate the database

    # here we are just simply checking if the user (discord user id) exists within the database
    if user_info is not None:
        profile_cache[duID] = user_info
    return user_info
# also note here we didn't have to close the 'cursor' or 'connection' 
# because it closes automatically as soon as the 'query' finishes
# --- GET PROFILE END ---

# --- CREATE PROFILE ---

# NOTE when the user enters their info and it is not an empty string, BEFORE we use the 'create_profile(...)' function
# we need to check if the conjoined string is not empty and if it isnt then that means they inputed something
# which then we store those info into variables
# we dont need a hasmap here because if the username is None then it defaults to being their discord username
# if the bio is None then it defaults to "Nothing to see here yet!"
# and if the bias is None then it defaults to "Nope, nothing here either"
# we can sepeartly check each one of them after storing the userinput info onto variables
# even if we did have a hasmap we would still need to check the hasmaps info so it would be the same thing
# then with the stored info within the variables, we make the profile this is only for the first time creation of a profile
# since only after that will they 'edit' their profile and only then do we need to make sure if they edit something we edit only that info
# we need to strip each info, check if the string they inputed is offensive or not and most likely conjoin/append these information to maybe a string or tupile 

# we don't need to check if the discord user id is in profile cache
# because we ONLY use this function when the user does not exist within the database itself
async def create_profile(duID: int, username: str, bio: str, bias: str):
    # we need information about their username, bio, and bias
    # we don't need to check if the username, bio, and bias are empty or not as discord will handel this.
    # however now that i think about it, im thinking of making it so to check if there are any offensive words within the inputs
    # NOTE make sure to make an "check_offensive_words" function, we check that information before we use this function
    # but for now we assume that there are no offensive words

    # LOGIC
    # we create the profile for the user, given info
    # we then insert their discord user id as key and 'username', 'bio', 'bias' as value into profile cache
    # so that when the same user uses 'profile', they're able to see their info without having to check the database itself

    # theres no reason to do 'try:' and 'except:' here, we will TRY to use the function outside
    # and if it doesn't work then the EXCEPT outside of the function will catch it anyways. if we do try here
    # and another try outside it would just be redundent

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
                INSERT INTO users (discord_user_id, username, biography, bias)
                VALUES (%s, %s, %s, %s)
                RETURNING username, biography, bias
                """,
                (duID, username, bio, bias)
            )
            userinfo = await cursor.fetchone()

    # NOTICE how we have 'RETURNING". a plain 'INSERT INTO' does NOT createa row for 'fetchone()' to read.
    # that row itself must already have been created, meaning ONLY AFTER THIS insert, can we use 'fetchone()'
    # for example, after this (if we didnt have to return any information), the user can just use 'profile' in order
    # to see their profile because since the profile ONLY now exists after insertion, we can only now read it with 'fetchone()'
    # which is what the 'profile' command would do if you arleady have a profile

    # so for here we need to add 'RETURNING' and the coresponding values we wnat to return

    # we cache their values ONLY after the database retrives the information, or else it'll look like the database worked when it didn't
    profile_cache[duID] = userinfo
    return True
# --- CREATE PROFILE END ---

# --- EDIT PROFILE ---
async def edit_profile(duID: int, username: str, bio: str, bias: str):
    # for now we need all of the information but when we send the modal
    # the entire thing will all be optional

    # instead of making one string variable that conjoins everything and never using it again
    # we can make a hashmap that stores everything in order
    # BUT THEN AGAIN if we make a hashmap storing everything that's just an empty string that's just doing more work?
    # we can conjoin each input by doing ''.join([username, bio, bias]) and see if its an empty string, if so return ''
    # this allows us to save some resources right?
    # username: userinput username
    # bio: userinput bio
    # bias: userinput bias
    # we can then check if each entry is ''.strip(), which means its an empty string and if it is then return '', an empty string
    # if at least one of these entries are valid (not empty strings)
    # take that valid string and conjoin it with 'update_colums' variable
    # everything will be in order so there's no need to worry about which comes first
    # then we return that 'update_colums' variable
    # this will be the string that is passed within the """UPDATE users SET ..."""  

    if ''.join([username, bio, bias]) == '':
        return 'NO_INPUT'

    info_map = {
        'username': username,
        'biography': bio,
        'bias': bias
    }

    # this form of iteration has the general rule,
    # 'WHAT DO WE WANT? WHAT DO WE ITERATE through to get what we want? WHATS THE CONDITION for what we want?'
    changes = {key: value for key, value in info_map.items() if value != ''}

    # so say they input only biography then the changes dict would look like
    # changes = {
    # biography: 'hello! theres are the changes id like to make'
    # }

    set_clause = ', '.join(f'{key} = %s' for key in changes)

    # so using our previous example for the changes dict,
    # this would be 'biography = %s'
    # notice that because it is ONLY one element, it does not add the ', ' connector


    async with await psycopg.AsyncConnection.connect(
        dbname = 'searchcord',
        user = 'postgres',
        password = psycopg_password,
        host = 'localhost',
        port = 5432
    ) as connection:
        async with connection.cursor() as cursor:
            await cursor.execute(
                f"""
                UPDATE users
                SET {set_clause}
                WHERE discord_user_id = %s
                RETURNING username, biography, bias
                """,
                (*changes.values(), duID) 
                # remember that 'duID' is just a variable storing information
                # doing '*changes.values()' doesnt itself 'return' something
                # instead, each value is being UNPACKED. usually you would get all of them PACKED
                # together. but that little '*' lets you UNPACK them and turn them into seperate elements
                # essentially like this 'value1', 'value2', 'value3', etc
            )
            updated_user_info = await cursor.fetchone()
    # if the user does not exist in our database
    # then the 'UPDATE ... WHERE discord_user_id = %s' executes successfully
    # but updates 0 rows
    # so there is no error to report!
    # meaning we need a way to distinguish when a user does not exist
    # within the databsae when they try to edit
    # also notice how we are 'RETURNING username, biography, bias'
    # if the user does not exist within the databsae, there is nothing to return!
    # hence it returns none
    if updated_user_info == None:
        return None

    profile_cache[duID] = updated_user_info
    return profile_cache[duID]
# --- EDIT PROFILE END ---

# --- DELETE PROFILE ---
async def delete_profile(duID: int):
    async with await psycopg.AsyncConnection.connect(
        dbname = 'searchcord',
        user = 'postgres',
        password = psycopg_password,
        host = 'localhost', 
        port = 5432
    ) as connection:
        async with connection.cursor() as cursor:
            # delete the discord user id from the table
            # deleting works the same way as 'UPDATE'
            # if there is a user that exists and deletes their profile
            # then it returns their id that was just deleted (so does NOT return 'None')
            # however if a user does not exist and tries to run this command
            # then it deletes from a row where the user id does not exist
            # meaning it deletes nothing and hence would return 'None' since the user did not
            # exist to begin with
            await cursor.execute(
                """
                DELETE FROM users
                WHERE discord_user_id = %s
                RETURNING discord_user_id
                """,
                (duID,)
            )
            # here we don't need to check what the 'cursor.fetchone()' info would contain
            # the logic is pretty simple
            # if it returns 'None' then that means a user that does not have a profile
            # tried running the command
            # if it returns 'discord_user_id' then it means that we successfully deleted the user's profile
            # meaning we can just check if its equal to 'None' 

            # we need to keep 'user_info' within our 'cursor' block beacuse
            # 'async with ... as ...' automates the opening and closing of the asynchronous connection
            user_info = await cursor.fetchone()
    if duID in profile_cache:
        del profile_cache[duID]
    return user_info
# --- DELETE PROFILE END ---