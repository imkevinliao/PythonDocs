# selenium
```
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
```

driver 配置
```
"""
可自行配置下载路径
prefs = {"download.default_directory": driver_download_path}
options.add_experimental_option("prefs", prefs)
"""
def get_driver() -> WebDriver:
    options = Options()
    options.add_argument("--headless")
    options.add_experimental_option("detach", True) # 执行完后是否自动退出 
    options.add_argument('--disable-gpu')
    options.add_argument("--start-maximized")
    service = Service(r'D:\msedgedriver.exe') # 驱动路径
    driver = webdriver.Edge(service=service, options=options)
    return driver
```

handle 标签切换
```
"""
driver.get 有问题时候，通过这种方式打开网页
driver.execute_script("window.open('{}');".format(url))
"""
current_page = user_driver.current_window_handle
driver.get("https://www.baidu.com")
window_after = driver.window_handles[1]
driver.switch_to.window(window_after)

html_source = driver.page_source  # 获取整个html

driver.close()
driver.switch_to.window(current_page)
```

综合操作
```
driver.get("https://www.baidu.com")
element = driver.find_element(By.XPATH, '//*[@id="kw"]')
element.send_keys("hello selenium")
driver.find_element(By.XPATH, '//*[@id="su"]').click()

# js 进行点击
click_element = driver.find_element(By.XPATH, '//*[@id="su"]')
driver.execute_script("arguments[0].click();", click_element)

# 模拟鼠标 进行点击
ActionChains(driver).click(click_element).perform() 
```
