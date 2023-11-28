from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time


def collect_link_products(url, driver):
        get_page = access_page_selenium(url=url, driver=driver)
        cards = get_page.find_all("div", "d-flex flex-row")
        product_urls = []
        for card in cards:
                target_url = card.find('a')['href']
                final_url = f"https://www.ikea.co.id{target_url}"
                product_urls.append(final_url)
        return product_urls


def product_price(soup):
        product_price = soup.find("span", {"data-price": True})
        if product_price:
                data_price = product_price.get("data-price")  
                return data_price
        else: 
                return None # if the atrribute not found 


def parsing(tag, classname, soup): 
       element = soup.find(tag, class_=classname)
       if element: 
               return element.text.replace("\n", "")
       else: 
               return None


def scraping(soup, product_url):
        price = product_price(soup)
        return {
                "Product Name" : parsing("div", "d-flex flex-row", soup),
                "Urls" : product_url, 
                "Price" : price,
                "Sold" : None if parsing("p", "partNumber", soup) == None else parsing("p", "partNumber", soup).replace("orang telah membeli produk ini", ""),
                "Description" : parsing("div", "product-desc-wrapper mb-4", soup),
                "Product Code": parsing("span","partnumber__code black-code black-box", soup),        
        }

def access_page_selenium(url, driver):
        driver.get(url)
        if "Recommended" in url:
            try:
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'd-flex flex-row')))
            except TimeoutException:
                print("TimeoutError")
                # Return None if the page didn't load successfully
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup


if __name__ == "__main__":
        start_time = time.time()
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument("--log-level=3") # to clear logging, while try to run your program. 
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--ignore-certificate-errors') # handling ssl certificate
        driver = webdriver.Chrome(options=chrome_options)
        
        final_result = []
        page = 1
        while True: 
                get_catalogue_urls_product = collect_link_products(f"https://www.ikea.co.id/in/produk/ruang-kerja-kantor?sort=SALES&page={page}", driver)
                print(len(get_catalogue_urls_product))
                print(f"acessing_page : {page}")
                page = page + 1
                if len(get_catalogue_urls_product) == 0:
                        break
                else: 
                        for product_url in get_catalogue_urls_product: 
                                print(f"Processing_Product_Url : {product_url}")
                                get_product_Data = access_page_selenium(product_url, driver)
                                if get_product_Data: 
                                        result = scraping(get_product_Data, product_url=product_url)
                                        print(result)
                                        final_result.append(result)
                                               
    
        df = pd.DataFrame(final_result)
        df.to_excel("testsiang.xlsx", index=False)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Script execution time: {elapsed_time} seconds")
        #driver.quit()
