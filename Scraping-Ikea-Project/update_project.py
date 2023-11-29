from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


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
                WebDriverWait(driver, 10, poll_frequency=5).until(EC.presence_of_element_located((By.CLASS_NAME, 'd-flex flex-row')))
            except TimeoutException:
                print("TimeoutError")
                # Return None if the page didn't load successfully
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        return soup


def read_excel_to_list_of_dicts(file_path):
    try:
            df = pd.read_excel(file_path)
            records = df.to_dict(orient='records')
            return records
    except PermissionError as e:
        print(f"An error occurred: {str(e)}")
        return None


def scrape_process():
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
        return final_result


def merge_lists_of_dicts(list1, list2, key):
    # Create sets of unique keys from each list of dictionaries
    keys_set1 = set(item[key] for item in list1)
    keys_set2 = set(item[key] for item in list2)

    # Find the common keys between the two sets
    common_keys = keys_set1.intersection(keys_set2)

    # Filter out the dictionaries with common keys from list2
    filtered_list2 = [item for item in list2 if item[key] not in common_keys]

    # Combine the two lists of dictionaries
    merged_list = list1 + filtered_list2

    return merged_list

""""""
if __name__ == "__main__":
        start_time = time.time()
        chrome_options = Options()
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument("--log-level=3") # to clear logging, while try to run your program. 
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        #chrome_options.add_experimental_option("prefs",{"profile.managed_default_content_settings.images" : 2})# for minimize, while load that data
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--ignore-certificate-errors') # handling ssl certificate
        driver = webdriver.Chrome(options=chrome_options)
        
        final_result = []
        page = 1
        """
        Sebuah kasus untuk mengupdate data yang sudah ada
        Keterangannya adalah
        JIka ada data satuan/produk baru, itu wajib ditaruh paling terakhir
        Ex : 
        data = [1,3,2,4,6]
        data_baru = [8,7,10]
        data_final = [1,3,2,4,6,8,7,10]
        """

        """
        Cara solvingnya
        1. Kita pakai if condition untuk ngecek apakah file xlsx nya sudah ada atau belum v
        1a. logikanya, jika hasil xlsx nya ada, berarti sudah discrape sebelumnya
        2. kita harus membaca hasil xlsx nya kedalam python (R dari CRUD), berbentuk list of dictionaries
        3. scrape seperti biasa (mungkin)
        4. Validasi data, jika data baru tidak ada di data awal, maka masukkan data tersebut ke data baru
        5. Menyimpan datanya sebagai hasil akhir
        [1,2,3,4,5,6]
        [1,2,3,8,9,0]
        [8,9,0]
        datalama.extend(databaru)
        [1,2,3,4,5,6,8,9,0]
        """
        #Markus(502.611.51) Hattefja(704.945.12)
        if os.path.isfile("projectscraping - Copy.xlsx"):
               origin_data = read_excel_to_list_of_dicts("projectscraping - Copy.xlsx")
               result = scrape_process()
               final_result = merge_lists_of_dicts(origin_data, result, "Product Code")
        else: 
               final_result = scrape_process()
                                               
    
        df = pd.DataFrame(final_result)
        df.to_excel("projectscraping - Copy.xlsx", index=False)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Script execution time: {elapsed_time} seconds")
        #driver.quit()
