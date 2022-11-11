from selenium.webdriver import Chrome
from selenium.common.exceptions import InvalidCookieDomainException
import pickle


def cookies_get(br: Chrome, file_path: str) -> None:
    print("Saving cookies.")
    pickle.dump(br.get_cookies(), open(file_path, "wb"))


def cookies_load(br: Chrome, file_path: str) -> bool:
    try:
        cookies = pickle.load(open(file_path, "rb"))
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
