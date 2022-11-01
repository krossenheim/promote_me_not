from selenium.webdriver import Chrome
from selenium.common.exceptions import InvalidCookieDomainException
import pickle
import os


def cookies_get(br: Chrome, cookies_path="../cookies/linked_in_cookies.pkl") -> None:
    print("Saving cookies.")
    pickle.dump(br.get_cookies(), open(cookies_path, "wb"))


def cookies_set(br: Chrome, cookies_path="../cookies/linked_in_cookies.pkl") -> bool:
    try:
        cookies = pickle.load(open(cookies_path, "rb"))
        print("Loaded cookies.")
    except (EOFError, FileNotFoundError):
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
