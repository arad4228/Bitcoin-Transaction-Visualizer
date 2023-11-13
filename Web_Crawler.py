from bs4 import BeautifulSoup as bs
from threading import Thread
from collections import OrderedDict
import requests as re
import json
import time
import os

# Crawling Forwarding Transaction
class Web_Crawler:

    def __init__(self, start, end_transaction_number:'int') -> None:
        self.baseUrl = 'https://hashxp.org/tx/'
        self.queueTransactions = OrderedDict()
        self.queueTransactions[start]="Start"
        self.iteration = 0
        self.end_transaction_number = end_transaction_number
        # {'txid':'', 'address':'', 'vin':['address':'','type':'','spent':''], 'vout':['address':'','type':'','spent':'']}
        self.json_list = list()

    def __str__(self) -> str:
        return 'Web'
    
    def get_address_info(self, data, target, listObtainedData):
        data_list = data.select(target)
        # Vin
        if 'vin' in target:
            for data in data_list:
                vin = dict()
                address = data.find('tt', class_='btcaddr')
                type = data.find('b')
                money = data.find('a', class_='btctx').text.replace(' ', '')
                money = money.split('$')[0]
                vin['address'] = address.text
                vin['type'] = "None"
                if type != None:
                    vin['type'] = type.text[1:-1]
                vin['spent'] = "spent"
                vin['money'] = money
                listObtainedData.append(vin)
        # Vout
        else:
            for data in data_list:
                vout = dict()
                address = data.find('tt', class_='btcaddr')
                type = data.find('b')
                money = data.find('a', class_='btctx')
                if money != None:
                    money = money.text.replace(' ', '').split('$')[0]
                else:
                    money = data.find_all('div')[1]
                    money = money.text.replace('unspent','').replace(' ', '').split('$')[0]

                # key: txid, value: address
                if data.find('text') != None:
                    # UnSpent
                    spent = data.find('text').text
                    self.queueTransactions[spent] = address
                    vout['address'] = address.text
                    if type == None:
                        vout['type'] = "None"
                    else:
                        vout['type'] = type.text[1:-1]
                    vout['spent'] = spent
                else:
                    # Spent
                    tx = data.find('a', class_='btctx', href=True).attrs['href'][4:-4]
                    self.queueTransactions[tx] = address.text
                    vout['address'] = address.text
                    if type == None:
                        vout['type'] = "None"
                    else:
                        vout['type'] = type.text[1:-1]
                    vout['spent'] = tx
                    vout['money'] = money
                listObtainedData.append(vout)

    def crawling_data(self):
        while self.iteration <= self.end_transaction_number:
            transaction, addr = self.queueTransactions.popitem(last=False)
            if transaction == 'unspent':
                continue
            print(f'Iter: {self.iteration}, transaction: {transaction}')
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
                    ths = Thread(target=self.get_address_info, args=(data, target, list_obtained_vin))
                else:
                    ths = Thread(target=self.get_address_info, args=(data, target, list_obtained_vout))
                threads.append(ths)
                ths.start()

            for th in threads:
                th.join()

            json = dict()
            json['transaction'] = transaction
            json['vin'] = list_obtained_vin
            json['vout'] = list_obtained_vout
            self.json_list.append(json)

            self.iteration +=1
            time.sleep(5)
    
    def save_data(self, location, starttransaction):
        path = os.getcwd()
        if location not in path:
            os.chdir(path+location)      
        with open(f'Web_{starttransaction}.json', 'a', encoding='UTF-8') as f:
            json.dump(self.json_list, f)