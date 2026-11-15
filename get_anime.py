import aiohttp
anilist_api = 'https://graphql.anilist.co'

# we split functions into different folders so that we dont have one big file where we do everything
# and for organizing purposes
async def get_anime(session: aiohttp.ClientSession, anime_name: str):
    # we define the 'query', inside of it we must pass our 'anime_name'
    # however we can't just use an f string in order to directly plce the 'anime_name'
    # instead we store it inside of 'variables'
    # hence why we pass both 'query' and 'variables'\
    query = """
    query ($search: String!) {
        Page(perPage: 1) {
            media(search: $search, type: ANIME) {
                title {
                    english
                    native
                }
                description
                bannerImage
                coverImage {
                    extraLarge
                }
                
                studios(isMain: true) {
                  nodes {
                    name
                  }
                }
                status
                source
                format
                
                episodes
                duration

                seasonYear
                averageScore

                favourites
                genres

                trailer {
                    id
                    site
                    thumbnail
                }
                siteUrl
                isAdult

                characters(perPage: 10, sort: [ROLE, FAVOURITES_DESC]) {
                  edges {
                    role
                    
                    node {
                      name {
                        full
                        native
                      }
                      image {
                        medium
                      }
                    }

                    voiceActors(language: JAPANESE) {
                      name {
                        full
                        native
                      }
                      image {
                        medium
                      }
                    }
                  }
                }
            }
        }
    }
    """
    variables = {"search" : anime_name}

    # if we imported 'requests' into this file then we would have something like
    '''
    response = requests.post(
        anilist_api,
        json={
            'query' : query,
            'variables' : variables
        }
    )
    data = response.json()
    '''
    # but notice here how similar using 'aiohttp' is
    # since we want the 'response' we do 'async with ... as response'
    # instead of 'requsts', here we have our session! hence why we do 'session.post(...)'
    # and then inside of 'session.post()' is just the same thing as our 'request.post(...)'
    
    # we add more of a safety check here by checking the status of our 'response'
    # by doing, 'response.raise_for_status()'
    # then we get the 'result' by doing 'await response.json()' 
    # which is the same thing as 'data = response.json()'

    # since now we have our actual 'response' we can check if any 'errors' popped up
    # from the http request we made (hence why we did 'response.raise_for_status())'
    # this is because we made sure to check the status for our 'response'
    # if there are 'errors' in 'result' then we handel them

    # also notice how we do 'session', this means we need to pass an actual 'session' into our function
    # we can create a one time 'session' during our startup for our bot and use that until our bot shuts down
    # meaning that we would need to pass 'session' into all the functions that need it
    # which would be the anime_cog -> add_anime -> get_anime
    
    # remember the 'setup_hook(...)' function in our 'main.py' file
    # we can initalize the 'session' inside of that 'main.py' file
    # also remember at the end of every cog command we have a 'async def setup(bot)'
    # we do 'bot.add_cog(cog_name())', usually we woudn't need to pass our 'bot'
    # but now for our 'add_anime' cog (and every function that would need our 'bot' instance)
    # we would pass our 'bot' into 'bot.add_cog(cog_name(bot))' so we can access the 'session'!
    async with session.post(
        anilist_api,
        json={
            "query": query,
            "variables": variables
        }
    ) as response:
        response.raise_for_status()
        result = await response.json()

        if 'errors' in result:
            raise RuntimeError(f"ANI LIST API ANIME ERROR: {result['errors']}")
    
    result = result['data']['Page']['media']
    if not result:
        return None    
    return result[0]

#note to self: the first page will be the anime/manga info and then the second page will be the trailer
#starting from the third page and beyond, it will be characters and their voice actors
#since the third page and beyond will include characters, the users will be able to choose which one of those
#characters they want as their bias 