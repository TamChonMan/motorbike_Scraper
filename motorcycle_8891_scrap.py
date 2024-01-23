import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as Soup
from fake_useragent import UserAgent
import requests
import time

# 删除不必要的文本
def clean_text(txt):
    return str(txt).replace('<li>', '').replace('</li>', '').replace('\t', '').replace('\n', '')

# 提取车辆信息
def extract_car_info(page, style):
    url = requests.get(page, headers={"User-Agent": "XY"})
    soup = Soup(url.text, "html.parser")

    car_info = {
        "Name": clean_text(soup.find('dd', class_='value Blod F15px').get_text()),
        "Color": clean_text(soup.find_all('dd', class_='value Blod F15px')[1].get_text()),
        "used year": clean_text(soup.find('span', class_='Blod F15px').get_text().replace('年', '')),
        "gas": clean_text(soup.find_all('dd',class_='value Blod F15px')[2].get_text()).replace(' ',''),
        "mileage": clean_text(soup.find('ul', class_='auto_standard floatLeft').get_text()).replace('行車里程：','').replace('萬','').replace('公里','').replace(' ',''),
        "price": float(clean_text(soup.find('dd',class_='value Blod F15px Red').get_text()).replace('萬',''))*10000
    }

    return car_info

# 抓取车辆ID
def scrape_id(page,tag,class_name):
    sale_id = []
    url = requests.get(page, headers={"User-Agent": "XY"})
    soup = Soup(url.text, "html.parser")
    for item in (soup.find_all(tag, class_ = class_name)):
        for link in item.find_all('a',href=True):
            sale_id.append(link['href'])
    return sale_id

def scrape_all_id(start_page,end_page,tag,class_name):
    all_id = []
    for i in range(start_page,end_page,30):
        page_link = "https://auto.8891.com.tw/usedauto-moto.html?firstRow="+str(i)+"&totalRows=9299#searchContentBody"
        all_id += scrape_id(page_link,tag,class_name)
        print(f'scraping {((i+30)/30):0.0f} / {end_page/30:0.0f} page')
        time.sleep(np.random.uniform(1, 8))
    return all_id

# 提取车辆HTML
def get_soup(link):
    #random user-agent
    user_agent = UserAgent()
    url = requests.get(link, headers={"User-Agent":user_agent.random})
    return Soup(url.text, "html.parser")

def get_all_soup(id):
    link_with_soup = []
    length = len(id)
    for i in range(0,length-1):
        soup = get_soup('https://auto.8891.com.tw/'+id[i])
        link_with_soup.append((id[i],soup))
        print(f'scraping {i+1:0.0f} / {length:0.0f} links soup')
        time.sleep(np.random.uniform(1,10))
    return link_with_soup


# 主函数

# def main():
#     driver = webdriver.Chrome("./chromedriver")
#     driver.get("https://auto.8891.com.tw/usedauto-moto.html")

#     test_links = []
#     train_links = []

#     scrape_links(driver, test_links, 'test')
#     scrape_links(driver, train_links, 'train')

#     test_data = []
#     train_data = []

#     for link in test_links:
#         car_info = extract_car_info(link, 'test')
#         test_data.append(car_info)
#         time.sleep(1)

#     for link in train_links:
#         car_info = extract_car_info(link, 'train')
#         train_data.append(car_info)
#         time.sleep(1)

#     test_df = pd.DataFrame(test_data)
#     train_df = pd.DataFrame(train_data)

#     test_df.to_csv("TestCarData60.csv", index=False)
#     train_df.to_csv("TrainCarData60.csv", index=False)

#     print("Test Data:")
#     print(test_df.head())

#     print("\nTrain Data:")
#     print(train_df.head())

#     driver.quit()

# if __name__ == "__main__":
#     main()
