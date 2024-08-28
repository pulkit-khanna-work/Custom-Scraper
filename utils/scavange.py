from datetime import datetime
from operator import itemgetter
from pathlib import Path
import json
import os
import pytz
import shutil
import signal
import subprocess
import sys
import time
import re
from glob import glob
import itertools
import traceback

import pandas as pd
from utils import gui


COOKIES = {
    "fr": {
        "fnac": "#onetrust-accept-btn-handler",
        "darty": "#onetrust-accept-btn-handler",
    },
    "us": {"t-mobile": None},
}


class Scavange:
    def __init__(self, region, retailer, data=None, use_gui=False):
        match sys.platform:
            case "win32":
                home = os.getenv("USERPROFILE")
            case _:
                home = os.getenv("HOME")

        if home is not None:
            self.HOME = home
        else:
            raise Exception("HOME cannot be None")
        self.PLATFORM = sys.platform
        self.port = 0000
        self.use_gui = use_gui
        self.region = region.upper()
        self.lregion = self.region.lower()
        self.retailer = retailer
        self.lretailer = self.retailer.lower()
        self.data = data
        self.should_fetch_links = True if self.data is None else False
        self.should_fetch_name = (
            False if self.data is not None and isinstance(self.data, dict) else True
        )
        self.file_name = self.__get_file_name()
        self.file_number = self.__get_file_number()
        self.no_of_files = self.__get_no_of_files()
        self.min = 0
        self.max = None
        self.index = self.min
        self.parent_path = ""

        # Set Date
        tz = pytz.timezone("Asia/Kolkata")
        format = "".join(["%Y", "%m", "%d"])
        self.date = datetime.now(tz).date().strftime(format)
        self.wait_file = self.create_filename(["wait"], "txt")

        if self.should_fetch_links:
            self.links_file = self.create_filename(["links"], "csv")

        self.errors_file = self.create_filename(
            ["errors", "" if self.file_number == 0 else str(self.file_number)], "csv"
        )
        self.errors = []
        self.product_name = ""
        self.variants = ""

        self.__launch_browser()

    def __get_script_path(self, filename):
        return os.path.join(
            Path(__file__).parent.parent, "cdp", "scripts", f"{filename}.js"
        )

    def __run_script(self, filename, args=[]):
        """Run the node file and returns the output as JSON"""
        filepath = self.__get_script_path(filename)
        output = subprocess.check_output(
            ["node", f"{filepath}", f"{self.port}", json.dumps(args)]
        )
        try:
            return json.loads(output.decode())
        except Exception:
            return output.decode()

    def sleep(self, sleep_time):
        time.sleep(sleep_time)

    def __launch_browser(self):
        """Use chrome-launcher to launche browser in a random port.
        And store its pid and port in self."""
        script_path = self.__get_script_path("launchBrowser")

        chrome = subprocess.Popen(
            ["node", script_path],
            stdin=None,
            stdout=subprocess.PIPE,
            stderr=None,
            close_fds=True,
            shell=False,
        )
        self.sleep(3)
        if chrome.stdout is not None:
            output = json.loads(chrome.stdout.readline().decode())
            self.port, self.pid = itemgetter("port", "pid")(output)

        print(f"Browser started at port: {self.port}")

    def __close_browser(self):
        os.kill(self.pid, signal.SIGTERM)
        print("Browser closed")

    def create_filename(self, args, extension):
        return (
            f'{self.lregion}_{self.lretailer}_{self.date}_{"_".join(args)}.{extension}'
        )

    def __get_file_name(self, cli=True):
        """Returns the file name from command line argument"""
        if cli:
            return sys.argv[0]
        else:
            return os.path.basename(__file__)

    def __get_file_number(self):
        """Get the file number from the file name"""
        file_number = re.search(r"\d+", self.file_name)

        if file_number is not None:
            return int(file_number.group(0))
        else:
            return 0

    def __get_no_of_files(self):
        file_regex = self.file_name.replace(str(self.file_number), "[0-9]*")

        return len(glob(file_regex))

    def __get_range(self, no_of_items) -> tuple[int, int]:
        """Get range of links based on number of files and number of links"""

        sizes: list[int] = []

        if no_of_items < self.no_of_files:
            raise Exception("No of items cannot be greater than number of files!")

        # If x % n == 0 then the minimum
        # difference is 0 and all
        # numbers are x / n
        elif no_of_items % self.no_of_files == 0:
            for i in range(self.no_of_files):
                sizes.append(no_of_items // self.no_of_files)
        else:
            # upto n-(x % n) the values
            # will be x / n
            # after that the values
            # will be x / n + 1
            zp = self.no_of_files - (no_of_items % self.no_of_files)
            pp = no_of_items // self.no_of_files
            for i in range(self.no_of_files):
                if i >= zp:
                    sizes.append(pp + 1)
                else:
                    sizes.append(pp)

        range_start: int
        range_end: int

        if self.file_number == 1:
            range_start = 0
        else:
            range_start = sum(sizes[: self.file_number - 1])

        if self.no_of_files + 1 == self.file_number:
            range_end = no_of_items - 1
        else:
            range_end = range_start + sizes[self.file_number - 1]

        return range_start, range_end

    def navigate(self, url):
        self.__run_script("navigate", [url])
        self.set_root_id()

    def set_root_id(self):
        self.root_id = itemgetter("rootId")(self.__run_script("getRootId"))

    def get_node_ids(self, selector):
        node_ids = itemgetter("nodeIds")(self.__run_script("getNodeIds", [selector]))
        return node_ids

    def get_node_id(self, selector):
        node_ids = self.get_node_ids(selector)
        node_id = node_ids[0]
        return node_id

    def get_attributes(self, selector, node_id):
        attributes = itemgetter("attributes")(
            self.__run_script("getAttributes", [selector, node_id])
        )
        return attributes

    def get_attribute_js(self, css_selector, attribute_name):
        attribute = self.execute_script(
            f'document.querySelector("{css_selector}").getAttribute("{attribute_name}")'
        )
        if attribute is not None:
            return attribute.strip()

    def execute_script(self, expression):
        value = itemgetter("value")(self.__run_script("executeScript", [expression]))
        if value == "null":
            return None
        else:
            return value

    def get_text_js(self, css_selector):
        value = self.execute_script(
            f'document.querySelector("{css_selector}").textContent'
        )

        if value:
            return value.strip()
        else:
            return ""

    def scroll_into_view(self, css_selector, node_id):
        self.__run_script("scrollIntoView", [css_selector, node_id])

    def get_coordinates(self, css_selector, node_id):
        coordinates = itemgetter("coords")(
            self.__run_script("getCoordinates", [css_selector, node_id])
        )

        return coordinates

    def click_button(self, css_selector, node_id, pass_error=False):
        try:
            x, y = itemgetter("x", "y")(self.get_coordinates(css_selector, node_id))
            if self.use_gui:
                gui.click(x, y)
            else:
                self.__run_script("clickButton", [x, y])

        except Exception as e:
            if pass_error:
                pass
            else:
                raise Exception(e)

    def find_and_click_button(self, css_selector, pass_error=False):
        try:
            node_id = self.get_node_id(css_selector)
            self.click_button(css_selector, node_id, pass_error)
        except Exception as e:
            if pass_error:
                pass
            else:
                raise Exception(e)

    def click_button_js(self, css_selector):
        self.execute_script(f'document.querySelector("{css_selector}").click()')

    def create_dirs(self, *args):
        path = os.path.join(*args)
        os.makedirs(path, exist_ok=True)

        if not os.path.exists(path):
            raise Exception(f"Could not create directory {path}")

    def set_product_details(self, name, variants=[]):
        self.product_name = name
        self.variants = variants
        self.parent_path = os.path.join(
            self.retailer, self.product_name, *self.variants
        )
        self.create_dirs(self.parent_path)

    def display(self, index, url):
        print(f"Model index: {index}")
        print(f"Product name: {self.product_name} {' '.join(self.variants)}")
        print(f"URL: {url}")

    def take_screenshot(self, names=[], fullpage=True, width=None, height=None):
        filename = self.create_filename(
            [self.product_name, *self.variants, *names], "jpeg"
        )
        if width is None:
            width = 1920

        if fullpage:
            scroll_height = self.execute_script("document.body.scrollHeight")
            if scroll_height is not None:
                height = int(scroll_height)
        elif height is None:
            height = 1080

        result = itemgetter("result")(
            self.__run_script(
                "takeScreenshot",
                [os.path.join(self.parent_path, filename), width, height],
            )
        )
        print(result)

    def set_view_port(self, width=1920, height=1080):
        self.__run_script("setViewPort", [width, height])

    def get_text(self, css_selector, node_id):
        text = itemgetter("text")(
            self.__run_script("getInnerHTML", [css_selector, node_id])
        )
        return text.strip()

    def save_csv(self, data, filename):
        """Use url and name as keys"""
        pd.DataFrame(data).to_csv(filename)

    def read_csv(self, filename):
        content = pd.read_csv(filename)
        if self.should_fetch_name:
            return content["url"].to_list()
        else:
            return dict(zip(content["name"].to_list(), content["url"].to_list()))

    def print_line(self):
        print("=" * shutil.get_terminal_size()[0])

    def __get_data_len(self):
        if isinstance(self.data, list):
            return len(self.data)
        elif isinstance(self.data, dict):
            return len(self.data.keys())

    def __set_data(self):
        if self.data is None and os.path.exists(self.links_file):
            self.data = self.read_csv(self.links_file)

        if self.file_number == 0:
            self.max = self.__get_data_len()
        else:
            self.min, self.max = self.__get_range(self.__get_data_len())

    def __slice_data(self):
        if isinstance(self.data, list):
            self.data = self.data[self.min : self.max]
        elif isinstance(self.data, dict):
            self.data = dict(itertools.islice(self.data.items(), self.min, self.max))

    def accept_cookies(self):
        cookie_selector = COOKIES[self.lregion][self.lretailer]
        if cookie_selector is not None:
            self.click_button_js(cookie_selector)

    def choice(self, get_links=None):
        options = [
            "Running First Time",
            "Running After Code Stops",
            "Running Issue CSV URLs Only",
        ]

        for i, option in enumerate(options):
            print(f"{i+1}) {option}")

        if self.data is None and os.path.exists(self.links_file):
            self.__set_data()

        while True:
            try:
                user_input = input("Enter your choice: ")
                match int(user_input):
                    case 1:
                        if self.should_fetch_links and not os.path.exists(
                            self.links_file
                        ):
                            while os.path.exists(self.wait_file):
                                print("Waiting for links to fetch")
                                self.sleep(5)
                            if (
                                not os.path.exists(self.links_file)
                                and get_links is not None
                            ):
                                Path(self.wait_file).touch()
                                get_links(self)
                                os.remove(self.wait_file)

                            if self.data is None:
                                self.__set_data()
                        self.__slice_data()
                        break
                    case 2:
                        index = int(
                            input(
                                f"Enter index value between [{self.min}:{self.max}]: "
                            )
                        )
                        if self.max is not None:
                            if index < self.min:
                                print(f"Value cannot be less than {self.min}")
                            elif index > self.max:
                                print(f"Value cannot be greater than {self.max}")
                            else:
                                self.min = index
                                self.__slice_data()
                                break
                    case 3:
                        if os.path.exists(self.errors_file):
                            self.data = self.read_csv(self.errors_file)
                            self.__slice_data()
                            break
                        else:
                            print(f"{self.errors_file} does not exists")
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                print("Enter a valid choie.")

    def __run_decorator(self, run_function, index, name, url):
        self.print_line()
        try:
            if self.should_fetch_name:
                run_function(self, index, url)
            else:
                run_function(self, index, name, url)
        except Exception as e:
            print(traceback.format_exc())
            print(f"Error: {e}")
            self.errors.append({"name": self.product_name, "url": url, "error": e})

    def run(self, run_function):
        if self.should_fetch_name:
            if isinstance(self.data, list):
                for index, url in enumerate(self.data):
                    self.__run_decorator(run_function, index, name=None, url=url)
        else:
            if isinstance(self.data, dict):
                for index, [name, url] in enumerate(self.data.items()):
                    self.__run_decorator(run_function, index, name, url=url)

        if len(self.errors) > 0:
            self.save_csv(self.errors, self.errors_file)
        elif os.path.exists(self.errors_file) and not len(self.errors_file) > 0:
            os.remove(self.errors_file)
        self.print_line()
        print("Scrapper completed")
        self.__close_browser()
        self.print_line()
