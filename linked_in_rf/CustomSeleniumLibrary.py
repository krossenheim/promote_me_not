from robot.libraries.BuiltIn import BuiltIn


def get_webdriver_instance():
    se2lib = BuiltIn().get_library_instance('SeleniumLibrary')
    return se2lib.driver
