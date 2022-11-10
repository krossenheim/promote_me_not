from selenium.webdriver import Chrome
from selenium.common.exceptions import InvalidCookieDomainException
import pickle
import pathlib

__cookies_path = f"{pathlib.Path(__file__).parent.resolve()}/linked_in_cookies.pkl"


def cookies_get(br: Chrome) -> None:
    print("Saving cookies.")
    pickle.dump(br.get_cookies(), open(__cookies_path, "wb"))


def cookies_load(br: Chrome) -> bool:
    try:
        cookies = pickle.load(open(__cookies_path, "rb"))
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
