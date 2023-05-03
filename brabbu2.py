#!env/Scripts/python python

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import csv
import datetime
import logging
import re
import json

products = []
tmp_var1 = ""
tmp_var2=""
tmp_varLabel1 = ""
tmp_varLabel2 = ""
tmp_swatch_image1 = ""
tmp_swatch_image2 = ""

# -------------- USER INPUT
# un = "customer"
# pw = "123456"
filename = 'brabbu-softgoods_pillows3'

test1 = "" # no variant
test2 = "" # 1 row variants
TEST_URLS = [test1]
TEST_MODE = False

with open('config_softgoods_pillows.json', 'r') as f:
    config_json = json.load(f)
    #----------------------- links
    initial_url = (config_json['initial_url'])
    supplier_name =(config_json['supplier_name'])
    initial_page_xpath = (config_json['config_links']['initial_page_xpath']['xpath'])
    # cat1_xpath = (config_json['config_links']['category1']['xpath'])
    prod_links_xpath = (config_json['config_links']['products']['xpath'])
    next_page_xpath = (config_json['config_links']['next_page']['xpath'])
    # view_all_xpath = (config_json['config_others']['view_all']['xpath'])
    variants_flag_xpath = (config_json['config_others']['variants_flag']['xpath'])
    variants_xpath = (config_json['config_others']['variants']['xpath'])
    # ---------------------- product attributes
    product_code_xpath = (config_json['config_products']['product_code']['xpath'])
    product_name_xpath = (config_json['config_products']['product_name']['xpath'])
    # category1_xpath = 
    description_xpath = (config_json['config_products']['description']['xpath'])
    image1_xpath = (config_json['config_products']['image1']['xpath'])
    image2_xpath = (config_json['config_products']['image2']['xpath'])
    image3_xpath = (config_json['config_products']['image3']['xpath'])
    image4_xpath = (config_json['config_products']['image4']['xpath'])
    image5_xpath = (config_json['config_products']['image5']['xpath'])
    image6_xpath = (config_json['config_products']['image6']['xpath'])
    image7_xpath = (config_json['config_products']['image7']['xpath'])
    image8_xpath = (config_json['config_products']['image8']['xpath'])
    image9_xpath = (config_json['config_products']['image9']['xpath'])
    image10_xpath = (config_json['config_products']['image10']['xpath'])
    # images_xpath = (config_json['config_products']['images']['xpath'])
    # # ---------------------- variants
    # variant1_xpath = (config_json['custom_attributes']['variant1'])
    # variant2_xpath = (config_json['custom_attributes']['variant2'])
    # variant_label1_xpath = (config_json['custom_attributes']['variant_label1'])
    # variant_label2_xpath = (config_json['custom_attributes']['variant_label2'])
    # swatch_image1_xpath = (config_json['custom_attributes']['swatch_image1'])
    # swatch_image2_xpath = (config_json['custom_attributes']['swatch_image2'])
    video_xpath = (config_json['config_products']['video']['xpath'])
    availability_xpath = (config_json['custom_attributes']['availability'])
    materials_and_dimensions_xpath = (config_json['custom_attributes']['materials_and_dimensions'])
    # ------- custome attributes
    custom_attributes = config_json['custom_attributes']

    for ca, xpath in custom_attributes.items():
        if xpath:
            custom_attributes[ca] = xpath

category1_urls = []
category2_urls = []
product_urls = []
products = []

def chr_driver():
    op = webdriver.ChromeOptions()
    op.add_experimental_option('excludeSwitches', ['enable-logging']) #removes the annoying DevTools listening on ws://127.0.0.1 message in the terminal (windows)
    op.add_argument("window-size=1920x1080")
    op.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
    #-- pop up blocking
    op.add_argument("--disable-notifications")  # Disable notifications
    op.add_argument("--disable-popup-blocking")  # Block pop-ups
    op.add_argument("--disable-infobars")  # Disable infobars
    op.add_experimental_option("prefs", {
    "profile.default_content_setting_values.notifications": 2,  # Disable notifications
    "profile.default_content_setting_values.popups": 2,  # Block pop-ups
    "profile.default_content_setting_values.automatic_downloads": 2  # Block automatic downloads
    })

    op.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # disable images
    serv = Service('/home/m3wt/enzo/chromedriver')
    h_mode = input('mode ([h]headless | [f]full): ')
    op.headless = h_mode == 'h'
    if not op.headless:
        if h_mode != 'f':
            logging.warning('check driver headless option')

    logging.debug('Using Selenium WebDriver with Chrome browser')
    browser = webdriver.Chrome(service=serv, options=op)
    return browser


def scrape_initial_page():
    tmp_cat1 = ""
    urls = set()

    # menu
    menu_cat_links = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, initial_page_xpath))
    )
    # menu_cat_links = driver.find_elements(By.XPATH, initial_page_xpath)
    for link in menu_cat_links:
        url = link.get_attribute('href')
        # child_elem = link.find_element(By.XPATH, "./div")
        tmp_cat1 = link.get_attribute("textContent").strip() # optional text extract
        # tmp_cat1=""
        if url not in category1_urls:
            # urls.append((link,tmp_cat1))
            urls.add((url, tmp_cat1))
    return list(urls)


def get_category_links():
    for url in category1_urls:
        logging.debug(f'Scraping category URL: {url[0]} | cat1: {url[1]}')
        driver.get(url[0])
        sleep(3)
        tmp_cat2 = url[1]
        current_url = driver.current_url
        pattern = r'([^/]+)(?=/[^/]+$)'
        match = re.search(pattern, current_url)
        if match:
            tmp_cat1 = match.group(1)
        # sleep(0.5)
        # get_cat1_urls(cat1_xpath, tmp_cat1) # 2nd level category optional
        get_prod_urls(prod_links_xpath, tmp_cat1, tmp_cat2)
        pagination(tmp_cat1, tmp_cat2)


def get_cat1_urls(xpath, cat1):
    tmp_cat2 = ""
    count = 0
    # urls=set()
    cat_links = driver.find_elements(By.XPATH, xpath)
    for link in cat_links:
        url = link.get_attribute('href')
        tmp_cat1 = cat1
        tmp_cat2=""
        # tmp_cat2 = link.get_attribute("textContent")
        if url not in category2_urls:
            # urls.add((url, tmp_cat1, tmp_cat2))
            category2_urls.append((url, tmp_cat1, tmp_cat2))
            count += 1
    print(f'Added {count} urls in the category links queue.')

def get_prod_links():
    for link in category2_urls:
    # for link in category2_urls[1:2]:
        logging.debug(f'Scraping catalogue URL: {link[0]} | cat1: {link[1]} | cat2: {link[2]}')
        driver.get(link[0])
        tmp_cat1 = link[1]
        tmp_cat2 = link[2]
        sleep(1)
        # pagination() #OPTIONAL INFINITE PAGINATION
        get_prod_urls(prod_links_xpath, tmp_cat1, tmp_cat2)
        pagination(tmp_cat1, tmp_cat2)


def get_prod_urls(xpath, cat1, cat2):
    urls = set()
    prod_links = driver.find_elements(By.XPATH,xpath)
    count = 0
    for link in prod_links:
        url = link.get_attribute('href')
        if url not in urls:
            urls.add((url, cat1, cat2))
        set2list = list(urls)
        for i in set2list:
            if i not in product_urls:
                count += 1
                product_urls.append(i)
    print(f'Added {count} urls in the product links queue.')
   
# def pagination(cat1, cat2):
#     next_page_x = next_page_xpath
#     while True:
#         try:
#             # Check whether nextPage_xpath exists
#             nextPage_elem = driver.find_element(By.XPATH, next_page_x)
#             screen_center_x = driver.execute_script("return window.innerWidth / 2;")
#             screen_center_y = driver.execute_script("return window.innerHeight / 2;")
#             driver.execute_script("window.scrollTo(arguments[0] - (arguments[2] / 2), arguments[1] - (arguments[3] / 2));", nextPage_elem.location['x'], nextPage_elem.location['y'], screen_center_x, screen_center_y)
#             sleep(2)
#             # Add this before clicking the button element
#             try:
#                 button_element = driver.find_element(By.XPATH, "//div[@class='container-fluid to-inspire-popup fade p-0 is_visible']")
#                 driver.execute_script('arguments[0].click();', button_element)
#             except:
#                 pass
#             nextPage_elem.click()
#             sleep(2)
#             get_prod_urls(prod_links_xpath, cat1, cat2)
#         except NoSuchElementException:
#             # If nextPage_xpath does not exist, break out of the loop
#             break

def pagination(cat1, cat2):
    count = 0
    next_page_x = next_page_xpath
    while count < 7:
        try:
            # Check whether nextPage_xpath exists
            nextPage_elem = driver.find_element(By.XPATH, next_page_x)
            screen_center_x = driver.execute_script("return window.innerWidth / 2;")
            screen_center_y = driver.execute_script("return window.innerHeight / 2;")
            driver.execute_script("window.scrollTo(arguments[0] - (arguments[2] / 2), arguments[1] - (arguments[3] / 2));", nextPage_elem.location['x'], nextPage_elem.location['y'], screen_center_x, screen_center_y)
            sleep(2)
            # Add this before clicking the button element
            try:
                button_element = driver.find_element(By.XPATH, "//div[@class='container-fluid to-inspire-popup fade p-0 is_visible']")
                driver.execute_script('arguments[0].click();', button_element)
            except:
                pass
            nextPage_elem.click()
            sleep(2)
            get_prod_urls(prod_links_xpath, cat1, cat2)
            count += 1
        except:
            # If nextPage_xpath does not exist, break out of the loop
            break

def scrape_prod_links_test():
    for test_url in TEST_URLS:
        logging.debug(f'Scraping TEST URL: {test_url}')
        driver.get(test_url)
        sleep(1)
        if variantsCheck() is True:
            get_variants('test', 'test')
        else:
            extract_data('test', 'test')

def scrape_prod_links():
    for link in product_urls:
        logging.debug(f'Scraping product URL: {link[0]} | category1: {link[1]} | category2: {link[2]}')
        driver.get(link[0])
        tmp_cat1 = link[1]
        tmp_cat2 = link[2]
        sleep(3)
        if variantsCheck() is True:
            get_variants(tmp_cat1, tmp_cat2)
        else:
            extract_data(tmp_cat1, tmp_cat2)

def variantsCheck():
    try:
        driver.find_element(By.XPATH,variants_flag_xpath)
        istherevariants = True
    except:
        istherevariants = False
    return istherevariants

def get_element_attribute(xpath, attribute):
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute(attribute)
    except NoSuchElementException:
        return ''

def getImages():
    images=[]
    thumbnails_elem = driver.find_elements(By.XPATH, images_xpath)
    # thumbnails_elem = WebDriverWait(driver, 10).until(
    #             EC.presence_of_element_located((By.XPATH, images_xpath))
    #         )

    for i in thumbnails_elem:
        # driver.execute_script("arguments[0].click();", i)
        # i.click() # CLICKS THUMBNAILS
        # sleep(2)
        # active_image_elem = driver.find_element(By.XPATH, image1_xpath)
        url = i.get_attribute("srcset")
        if url not in images:
            pattern = r"^(.*?)(?:\s1x,)"
            match = re.search(pattern, url)
            if match:
                images.append(match.group(1))
    return images
product_counter = 0

def extract_data(cat1, cat2):
    global product_info
    global product_counter
    # if checkVar == True:
    #     pcode = get_element_attribute(product_code_xpath, "textContent") + " - " +  tmp_var1
    # else:
    #     pcode = get_element_attribute(product_code_xpath, "textContent")
    pcode = get_element_attribute(product_code_xpath, "textContent").strip()
    if pcode not in [product['product_code'] for product in products]:
        pname = get_element_attribute(product_name_xpath, "textContent").strip()
        # category1 = get_element_attribute(product_category1_xpath, "textContent")
        # category2 = get_element_attribute(product_category2_xpath, "textContent")
        category1 = cat1
        category2 = cat2
        # getImages() # if more than 1 images
        image1 = get_element_attribute(image1_xpath, "src")
        image2 = get_element_attribute(image2_xpath, "src")
        image3 = get_element_attribute(image3_xpath, "src")
        image4 = get_element_attribute(image4_xpath, "src")
        image5 = get_element_attribute(image5_xpath, "src")
        image6 = get_element_attribute(image6_xpath, "src")
        image7 = get_element_attribute(image7_xpath, "src")
        image8 = get_element_attribute(image8_xpath, "src")
        image9 = get_element_attribute(image9_xpath, "src")
        image10 = get_element_attribute(image10_xpath, "src")
        description = get_element_attribute(description_xpath, "innerHTML")
        video = get_element_attribute(video_xpath, "src")
        availability = get_element_attribute(availability_xpath, "textContent").strip()
        materials_and_dimensions = get_element_attribute(materials_and_dimensions_xpath, "innerHTML")
        supplier = supplier_name
        #variants
        # variant1 = get_element_attribute(variant1_xpath, "textContent")
        # variant2 = get_element_attribute(variant2_xpath, "textContent")
        # variant_label1 = get_element_attribute(variant_label1_xpath, "textContent")
        # variant_label2 = get_element_attribute(variant_label2_xpath, "textContent")
        # swatch_image1 = get_element_attribute(swatch_image1_xpath, "src")
        # swatch_image2 = get_element_attribute(swatch_image2_xpath, "src")

        today = datetime.datetime.today()
        scrape_date = today.strftime("%d/%m/%Y")
        pageUrl = driver.current_url


        product_info = {
            'product_code': pcode,
            'product_name': pname,
            'category1' : category1,
            'category2': category2,
            'description': description,           
            'image1': image1,
            'image2': image2,
            'image3': image3,
            'image4': image4,
            'image5': image5,
            'imageUrl6': image6,
            'imageUrl7': image7,
            'imageUrl8': image8,
            'imageUrl9': image9,
            'imageUrl10': image10,
            'video': video,
            'availability': availability,
            'materials_and_dimensions': materials_and_dimensions,
            'pageUrl': pageUrl,
            'scrape_date': scrape_date,
            'supplier': supplier
        }
        # for ca, xpath in custom_attributes.items():
        #     extracted_text = get_element_attribute(xpath,'textContent')
        #     # print(f'{ca} {extracted_text}')
        #     product_info[ca] = extracted_text

        # product_info['variant1'] = tmp_var1
        # product_info['variantLabel1'] = tmp_varLabel1
        # product_info['swatch_image1'] = tmp_swatch_image1
        # product_info['variant2'] = tmp_var2
        # product_info['variantLabel2'] = tmp_varLabel2
        # product_info['swatch_image2'] = tmp_swatch_image2

        # product_info['variant1'] = tmp_var1 if tmp_var1 else ''
        # product_info['variantLabel1'] = tmp_varLabel1 if tmp_varLabel1 else ''
        # product_info['swatch_image1'] = swatch_image1 if swatch_image1 else ''


        # image_lst = getImages()
        # # Define the maximum number of iterations
        # max_iterations = 15
        # # Loop through the list of images and assign to corresponding variables
        # for i in range(max_iterations):
        #     if i < len(image_lst):
        #         product_info[f'image{i+1}'] = image_lst[i]
        #     else:
        #         product_info[f'image{i+1}'] = ""
        
        
        product_counter +=1
        logging.debug(f'{product_counter}.Extracted product: {pcode} | {pname}')
        products.append(product_info)
        #call pagination function
        # pagination()
    else:
        print('Product exists. Skipping...')

def get_variants(cat1, cat2):
    global tmp_var1, tmp_var2, tmp_varLabel1, tmp_varLabel2, tmp_swatch_image1, tmp_swatch_image2
    count_var = 0
    # global var_list
    count_var_elem = driver.find_elements(By.XPATH, variants_xpath)
    count_var = len(count_var_elem)
    if count_var == 1:
        var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
        var_elem1_lst = var_elem1.find_elements(By.XPATH, "./div[2]/div")
        for i in range(0, len(var_elem1_lst)):
            # scroll to the top of the page
            driver.execute_script("window.scrollTo(0, 0)")
            # sleep(1)
            try: # catch page not found errors
                var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
            except:
                break 
            var_elem1.find_elements(By.XPATH, "./div[2]/div")[i].click()
            sleep(1)
            # try:
            #     WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located((By.XPATH, image1_xpath))
            #     )
            # except:
            #     pass
            try: #catch PAGE NOT FOUND errors
                var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
            except:
                break
            tmp_var1 = var_elem1.find_element(By.XPATH,"./div[1]/span[2]").get_attribute("textContent")
            varLabel1_elem = var_elem1.find_element(By.XPATH,"./div[1]/span[1]")
            tmp_varLabel1 = varLabel1_elem.get_attribute('textContent')
            try:
                tmp_swatch_image1 = var_elem1.find_element(By.XPATH,"./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')

            except:
                tmp_swatch_image1 =""
            extract_data(cat1, cat2)
    elif count_var == 2:
        var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
        var_elem1_lst = var_elem1.find_elements(By.XPATH, "./div[2]/div")
        for i in range(0, len(var_elem1_lst)):
            # scroll to the top of the page
            driver.execute_script("window.scrollTo(0, 0)")
            # sleep(1)
            try: #catch page not found errors
                var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
            except:
                break
            var_elem1.find_elements(By.XPATH, "./div[2]/div")[i].click()
            sleep(1)
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, image1_xpath))
            # )
            try: #catch page not found errors
                var_elem1 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[1]")
            except:
                break
            tmp_var1 = var_elem1.find_element(By.XPATH,"./div[1]/span[2]").get_attribute("textContent")
            varLabel1_elem = var_elem1.find_element(By.XPATH,"./div[1]/span[1]")
            tmp_varLabel1 = varLabel1_elem.get_attribute('textContent')
            try:
                tmp_swatch_image1 = var_elem1.find_element(By.XPATH,"./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')

            except:
                tmp_swatch_image1 =""
            try: #catch page not found errors
                var_elem2 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[2]")
            except:
                break
            var_elem2_lst = var_elem2.find_elements(By.XPATH, "./div[2]/div")
            for i in range(0, len(var_elem2_lst)):
                driver.execute_script("window.scrollTo(0, 0)") # scroll to the top of the page
                # sleep(1)
                var_elem2.find_elements(By.XPATH, "./div[2]/div")[i].click()
                sleep(1)
                # WebDriverWait(driver, 10).until(
                #     EC.presence_of_element_located((By.XPATH, image1_xpath))
                # )
                try: #catch page not found errors
                    var_elem2 = driver.find_element(By.XPATH, "//div[@id='product-arrangement-and-colors-wrapper']/div/div/div[2]")
                except:
                    break
                tmp_var2 = var_elem2.find_element(By.XPATH,"./div[1]/span[2]").get_attribute("textContent")
                varLabel2_elem = var_elem2.find_element(By.XPATH,"./div[1]/span[1]")
                tmp_varLabel2 = varLabel2_elem.get_attribute('textContent')
                try: 
                    tmp_swatch_image2 = var_elem1.find_element(By.XPATH,"./div[2]/div/@class[contains(.,'active')]/parent::div/img").get_attribute('src')

                except:
                    tmp_swatch_image1 =""
                extract_data(cat1, cat2)



def save():
    #save to csv
    with open(f'{filename}.csv', 'w', newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=product_info.keys())
        writer.writeheader()
        writer.writerows(products)
    logging.info(f"Export to CSV file {filename} is finished.")

    # with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(["URL"])
    #     writer.writerows(product_urls)
    # logging.info(f"Export to CSV file {filename} is finished.")

def allowCookie():
    cookie_xpath = "//button[normalize-space()='Accept all cookies']"
    cookie_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, cookie_xpath))
        )
    cookie_btn.click()
 
def close_random_popup(driver):
    popup_xpath = "//div[@class='container-fluid to-inspire-popup fade p-0 is_visible']"
    while True:
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.XPATH, popup_xpath))
            )
            close_button = driver.find_element(By.XPATH, popup_xpath)
            close_button.click()
        except TimeoutException:
            pass
        sleep(5)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.DEBUG)
    logging.getLogger("selenium").setLevel(logging.INFO)
    # ---- block logs from the urllib3.connectionpool logger
    # Set the root logger's level to debug
    logging.getLogger().setLevel(logging.DEBUG)
    # Get the logger for the `urllib3.connectionpool` module
    connectionpool_logger = logging.getLogger("urllib3.connectionpool")
    # Set the logger's level to warning, which is above debug
    connectionpool_logger.setLevel(logging.WARNING)
    driver = chr_driver()
    if TEST_MODE is True:
        print('RUNNING ON TEST MODE')
        scrape_prod_links_test()
        
    else:
        logging.debug(f'Parsing initial URL: {initial_url}')
        driver.get(initial_url)
        sleep(2)
        # login(un,pw)
        # allowCookie()

        category1_urls = scrape_initial_page()
        get_category_links()
        # get_prod_links()

        scrape_prod_links()
    save()
    driver.quit()

