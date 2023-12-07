from backend import token, database

def getUserFromCookies(cookies):
    try:
        access_token = cookies.get("access_token")
        user = token.verify_token(access_token)
        return user
    except:
        print("Error in getUserFromCookies function")
        return None


def getRoute(mission):
    route = []
    for (lon, lat, alt) in mission:
        route.append([lon, lat])
    return route


async def gps_event_generator(drone_name):
    while True:
        lat, lon = database.getDroneStatusByDroneName(drone_name)
        yield f"data: {json.dumps(gps_data)}\n\n"
        await asyncio.sleep(1)