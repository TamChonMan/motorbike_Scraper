import requests
from bs4 import BeautifulSoup as Soup
from fake_useragent import UserAgent
import time
import numpy as np

class CarScraper:
    def __init__(self,data_database):
        self_motorcycle_data_database = data_database

    @staticmethod
    def clean_text(txt):
        return str(txt).replace('<li>', '').replace('</li>', '').replace('\t', '').replace('\n', '')

    @staticmethod
    def extract_car_info(page, style):
        try:
            url = requests.get(page, headers={"User-Agent": "XY"})
            url.raise_for_status()
            soup = Soup(url.text, "html.parser")

            car_info = {
                "Name": CarScraper.clean_text(soup.find('dd', class_='value Blod F15px').get_text()),
                "Color": CarScraper.clean_text(soup.find_all('dd', class_='value Blod F15px')[1].get_text()),
                "used year": CarScraper.clean_text(soup.find('span', class_='Blod F15px').get_text().replace('年', '')),
                "gas": CarScraper.clean_text(soup.find_all('dd',class_='value Blod F15px')[2].get_text()).replace(' ',''),
                "mileage": CarScraper.clean_text(soup.find('ul', class_='auto_standard floatLeft').get_text()).replace('行車里程：','').replace('萬','').replace('公里','').replace(' ',''),
                "price": float(CarScraper.clean_text(soup.find('dd',class_='value Blod F15px Red').get_text()).replace('萬',''))*10000
            }

            return car_info
        except Exception as e:
            print(f"Error extracting car info: {str(e)}")
            return None

    @staticmethod
    def scrape_id(page, tag, class_name):
        try:
            sale_id = []
            url = requests.get(page, headers={"User-Agent": "XY"})
            url.raise_for_status()
            soup = Soup(url.text, "html.parser")
            for item in (soup.find_all(tag, class_ = class_name)):
                for link in item.find_all('a', href=True):
                    sale_id.append(link['href'])
            return sale_id
        except Exception as e:
            print(f"Error scraping IDs: {str(e)}")
            return []

    @staticmethod
    def scrape_all_id(start_page, end_page, tag, class_name):
        all_id = []
        try:
            for i in range(start_page, end_page, 30):
                page_link = "https://auto.8891.com.tw/usedauto-moto.html?firstRow="+str(i)+"&totalRows=9299#searchContentBody"
                all_id += CarScraper.scrape_id(page_link, tag, class_name)
                print(f'scraping {((i+30)/30):0.0f} / {end_page/30:0.0f} page')
                time.sleep(np.random.uniform(1, 8))
        except Exception as e:
            print(f"Error scraping all IDs: {str(e)}")
        return all_id

    @staticmethod
    def get_soup(link):
        try:
            user_agent = UserAgent()
            url = requests.get(link, headers={"User-Agent":user_agent.random})
            url.raise_for_status()
            return Soup(url.text, "html.parser")
        except Exception as e:
            print(f"Error getting soup: {str(e)}")
            return None

    @staticmethod
    def get_all_soup(id):
        link_with_soup = []
        try:
            for i in range(len(id)):
                soup = CarScraper.get_soup('https://auto.8891.com.tw/'+id[i])
                if soup:
                    link_with_soup.append((id[i],soup))
                    print(f'scraping {i+1:0.0f} / {len(id):0.0f} links soup')
                    time.sleep(np.random.uniform(1,10))
        except Exception as e:
            print(f"Error getting all soup: {str(e)}")
        return link_with_soup
