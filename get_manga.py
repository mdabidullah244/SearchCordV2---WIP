import aiohttp
anilist_api = 'https://graphql.anilist.co'

async def get_manga(session: aiohttp.ClientSession, manga_name: str):
    query = """
        query ($search: String!) {
        Page(perPage: 1) {
                    media(search: $search, type: MANGA) {
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
                        


                        averageScore

                        favourites
                        genres

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
    variables = {'search': manga_name}

    async with session.post(
        anilist_api,
        json = {
            'query' : query,
            'variables' : variables
        }
    ) as response:
        response.raise_for_status()
        result = response.json()

        if 'errors' in result:
            raise RuntimeError(f'ANI LIST API MANGA ERROR f{result['errors']}')

        result = result['data']['page']['media']
        if not result:
            return None
        return result[0]       
        