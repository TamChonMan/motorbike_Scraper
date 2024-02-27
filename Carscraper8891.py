import requests
from bs4 import BeautifulSoup as Soup
from fake_useragent import UserAgent
import time
import numpy as np
import pandas as pd
import re
import mysql.connector

class CarScraper:
    def __init__(self,data_database):
        self.motorcycle_data_database = data_database
        self.id = self.motorcycle_data_database['car_id']
        print('init')

    @staticmethod
    def clean_text(txt):
        return str(txt).replace('<li>', '').replace('</li>', '').replace('\t', '').replace('\n', '').replace('\r',' ')
        
    @staticmethod
    def extract_id(input_string):
        car_id_match = re.search(r'\d+', input_string)
        return car_id_match.group() if car_id_match else None

    def scrape_id(self, page, tag, class_name):
        try:
            sale_id = []
            url = requests.get(page, headers={"User-Agent": "XY"})
            url.raise_for_status()
            soup = Soup(url.text, "html.parser")
            for item in soup.find_all(tag, class_=class_name):
                for link in item.find_all('a', href=True):
                    id = self.extract_id(link['href'])
                    if np.int64(id) not in self.id.values:
                        sale_id.append(id)
                        print(f'added {id}')
                    else:
                        print('This ID has already scraped')
                        # return sale_id, True  # Indicate that the condition was met
            return sale_id, False  # Indicate that the condition was not met
        except Exception as e:
            print(f"Error scraping IDs: {str(e)}")
            return [], False

    def scrape_all_id(self, start_page, end_page, tag, class_name):
        all_id = []
        try:
            for i in range(start_page, end_page, 30):
                print(f'scraping {((i+30)/30):0.0f} / {end_page/30:0.0f} page')
                page_link = "https://auto.8891.com.tw/usedauto-moto.html?firstRow="+str(i)+"&totalRows=9299#searchContentBody"
                scraped_ids, condition_met = self.scrape_id(page_link, tag, class_name)
                all_id += scraped_ids
                # if condition_met:
                #     # print('Done')
                #     continue  # Terminate the loop if the condition was met
                time.sleep(np.random.uniform(1, 8))
        except Exception as e:
            print(f"Error scraping all IDs: {str(e)}")
        print('Done')
        return all_id


    def get_soup(self,link):
        try:
            user_agent = UserAgent()
            url = requests.get(link, headers={"User-Agent":user_agent.random})
            url.raise_for_status()
            return Soup(url.text, "html.parser")
        except Exception as e:
            print(f"Error getting soup: {str(e)}")
            return None
        
    def get_all_soup(self,id):
        link_with_soup = []
        try:
            for i in range(len(id)):
                soup = CarScraper.get_soup(self,'https://auto.8891.com.tw/usedauto-motoInfos-'+id[i]+'.html')
                if soup:
                    link_with_soup.append((id[i],soup))
                    print(f'scraping {i+1:0.0f} / {len(id):0.0f} links soup')
                    time.sleep(np.random.uniform(1,6))
        except Exception as e:
            print(f"Error getting all soup: {str(e)}")
        return link_with_soup


    def extract_car_info(self,link_with_soup):
        try:
            id = link_with_soup[0]
            soup = link_with_soup[1]

            car_info = {
                "car_id": id,
                "Name": self.clean_text(soup.find('dd', class_='value Blod F15px').get_text()),
                "Color": self.clean_text(soup.find_all('dd', class_='value Blod F15px')[1].get_text()),
                "used year": self.clean_text(soup.find('span', class_='Blod F15px').get_text().replace('年', '')),
                "gas": self.clean_text(soup.find_all('dd', class_='value Blod F15px')[2].get_text()).replace(' ', ''),
                "mileage": self.clean_text(soup.find('ul', class_='auto_standard floatLeft').get_text()).replace('行車里程：', '').replace('萬', '').replace('公里', '').replace(' ', ''),
                "Outfit": self.clean_text(''.join([outfit.get_text() for outfit in soup.find_all('li', class_='additionConfig')])),
                "detail": self.clean_text(''.join([detail.get_text() for detail in soup.find_all('div', class_='detail_content', style='line-height: 1.5;')])),
            }

            try:
                car_info["price"] = float(self.clean_text(soup.find('dd', class_='value Blod F15px Red').get_text()).replace('萬', '')) * 10000
            except ValueError:
                car_info["price"] = np.nan

            return car_info
        
        except Exception as e:
            print(f"Error extracting car info: {str(e)}")
            return None
    
    def new_scraped(self,no_page):
        id = self.scrape_all_id(0,no_page,'div','text-box')
        id_all_soup = self.get_all_soup(id)
        car_info = []
        for soup1 in id_all_soup :
            try:
                car_info.append(self.extract_car_info(soup1))
            except:
                print('None')
        return pd.DataFrame(car_info)

    @staticmethod
    def clean_df(df_car_info):
        df_car_info[['Company', 'Model']] = df_car_info['Name'].replace(' ','').str.split('-', n=1, expand=True)
        df_car_info = df_car_info.drop(columns='Name')
        df_car_info.insert(1, 'Company', df_car_info.pop('Company'))
        df_car_info.insert(2, 'Model', df_car_info.pop('Model'))

        df_car_info['Company'] = df_car_info['Company'].str.replace(' ','').replace('','其他廠牌')
        df_car_info['Model'] = df_car_info['Model'].replace(' ','other')

        df_car_info['mileage'] = pd.to_numeric(df_car_info['mileage'],errors='coerce')
        df_car_info['mileage'] = df_car_info['mileage'].apply(lambda x: x * 10000 if x < 100 else x)
        df_car_info['mileage']= pd.to_numeric(df_car_info['mileage'], errors='coerce')

        df_car_info['Color'] = df_car_info["Color"].replace('','其他')
        df_car_info['Color'] = df_car_info["Color"].replace('其他()','其他')

        df_car_info['gas'] = df_car_info["gas"].str.replace('L','')
        df_car_info['gas'] = df_car_info["gas"].str.replace('以上','')
        df_car_info['gas'] = df_car_info["gas"].str.replace('以下','')
        df_car_info['gas'] = df_car_info["gas"].str.replace('-','')
        df_car_info['gas'] = pd.to_numeric(df_car_info['gas'], errors='coerce')

        df_car_info['used year'] = pd.to_numeric(df_car_info['used year'], errors='coerce')
        this_year = 2024
        df_car_info['used year'] = this_year - df_car_info['used year']
        df_car_info['used year'] = df_car_info['used year'].apply(lambda x: 0 if x == 2024 else x )

        df_car_info['detail'] = df_car_info["detail"].str.replace('-','')

        return df_car_info

    def Update_database(self,new_df_car,saved):
        print(f'Add {len(new_df_car)}, From {len(self.motorcycle_data_database)} to {len(self.motorcycle_data_database)+len(new_df_car)}')
        self.motorcycle_data_database = pd.concat([self.motorcycle_data_database, new_df_car], axis = 0 ,ignore_index= True)
        self.motorcycle_data_database.to_csv(saved,index=False)
        return self.motorcycle_data_database