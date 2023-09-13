from backend import token

def getUserFromCookies(cookies):
    try:
        access_token = cookies.get("access_token")
        user = token.verify_token(access_token)
        return user
    except:
        print("Error in getUserFromCookies function")
        return None


