from bs4 import BeautifulSoup as bs
from threading import Thread
from collections import OrderedDict
import requests as re
import pandas as pd
import time

class Crawler:
    queueTransactions = None
    datafram = None
    iteration = 0

    # {'txid':'', 'address':'', 'vin':['address':'','type':'','spent':''], 'vout':['address':'','type':'','spent':'']}
    json_list = list()
    def __init__(self, start) -> None:
        self.baseUrl = 'https://hashxp.org/tx/'
        self.queueTransactions = OrderedDict()
        self.queueTransactions[start]="Strat"

    def get_address_type(self, data, target, listObtainedData):
        data_list = data.select(target)
        if 'vin' in target:
            for data in data_list:
                vin = dict()
                address = data.find('tt', class_='btcaddr')
                type = data.find('b')
                vin['address'] = address.text
                vin['type'] = type.text[1:-1]
                vin['spent'] = "Yes"
                print(vin)
                listObtainedData.append(vin)
        else:
            for data in data_list:
                vout = dict()
                address = data.find('tt', class_='btcaddr')
                type = data.find('b')
                # key: txid, value: address
                if data.find('text') != None:
                    # UnSpent
                    spent = data.find('text')
                    self.queueTransactions[spent] = address
                    vout['address'] = address.text
                    vout['type'] = type.text[1:-1]
                    vout['spent'] = spent.text
                else:
                    # Spent
                    tx = data.find('a', class_='btctx', href=True).attrs['href'][4:-4]
                    self.queueTransactions[tx] = address
                    vout['address'] = address.text
                    vout['type'] = type.text[1:-1]
                    vout['spent'] = tx.text
                listObtainedData.append(vout)

    

    def crawling_data(self):
        for idx, (transaction, addr) in enumerate(self.queueTransactions.items()):
            if self.iteration >= 300:
                break

            print(transaction)
            self.queueTransactions.pop(transaction)
            # Get HTML Data
            response = re.post(url=self.baseUrl+transaction)
            if response.status_code != 200:
                time.sleep(5)
                response = re.post(url=self.baseUrl+transaction)
            
            # Get HTML's hashio2 data(vin, vout, ...)
            soup = bs(response.text, "html.parser")
            hashio2 = soup.find('div', class_="hashio2")
            vins_data = hashio2.find('div', id='vins')
            vouts_data = hashio2.find('div', id='vouts')
            
            list_datas = [vins_data, vouts_data]
            list_obtained_vin = []
            list_obtained_vout = []
            
            list_target = ['div[id^="vin"]', 'div[id^="vout"]']

            # Parsing Vin, Vout Data
            threads = []
            for data, target in zip(list_datas, list_target):
                if 'vin' in target:
                    ths = Thread(target=self.get_address_type, args=(data, target, list_obtained_vin))
                else:
                    ths = Thread(target=self.get_address_type, args=(data, target, list_obtained_vout))
                threads.append(ths)
                ths.start()

            for th in threads:
                th.join()
                
            json = dict()
            json['transaction'] = transaction
            json['address'] = addr
            json['vin'] = list_obtained_vin
            json['vout'] = list_obtained_vout
            print(json)

            time.sleep(3)
            self.iteration +=1
        
