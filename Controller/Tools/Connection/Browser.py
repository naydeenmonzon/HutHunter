import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from subprocess import CREATE_NO_WINDOW
from os import environ
from selenium.common import exceptions


formatter = logging.Formatter('%(levelname)s %(asctime)s: %(message)s', datefmt="%Y-%b-%d %H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
eh = logging.FileHandler("C:/Users/Administrator/Documents/Projects/www/naydeenmonzon/PythonProjects/HutExplorer/Log/Logerror.log")
eh.setLevel(logging.ERROR)
wh = logging.FileHandler("C:/Users/Administrator/Documents/Projects/www/naydeenmonzon/PythonProjects/HutExplorer/Log/Logwarning.log")
wh.setLevel(logging.WARNING)
eh.setFormatter(formatter)
wh.setFormatter(formatter)
logger.addHandler(eh)
logger.addHandler(wh)




class ChromeDriver(webdriver.Chrome):
    def __init__(self):
        self.service = Service(executable_path='C:\\chromedriver.exe')
        # self.service.creationflags = CREATE_NO_WINDOW
        self.options = Options()
        self.options.headless = False
        self.options.add_experimental_option("detach", True)
        # environ['PATH']= "C:"
        super().__init__(service=self.service, options=self.options)
        
    def __enter__(self):
        logger.setLevel(logging.WARNING)
        try:
            self.implicitly_wait(180)
            self.maximize_window()
            return self
        except exceptions.WebDriverException as err:
            logger.error(err)

    def __exit__(self, *args):
        time.sleep(5)
        self.close()
    
        