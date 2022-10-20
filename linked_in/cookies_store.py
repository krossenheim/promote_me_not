from selenium.webdriver import Chrome
from selenium.common.exceptions import InvalidCookieDomainException
import pickle

__cookies_path = "../cookies/linked_in_cookies.pkl"


def cookies_get(br: Chrome):
    pickle.dump(br.get_cookies(), open(__cookies_path, "wb"))


def cookies_load(br: Chrome) -> bool:
    try:
        cookies = pickle.load(open(__cookies_path, "rb"))
    except EOFError:
        print("No cookies saved, file is empty.")
        return False
    for cookie in cookies:
        try:
            br.add_cookie(cookie)
        except InvalidCookieDomainException:
            print("Failed to load cookie")
    return True


if __name__ == "__main__":
    pass
