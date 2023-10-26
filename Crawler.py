from bs4 import BeautifulSoup as bs
from threading import Thread
from queue import Queue
import requests as re
import time

class node:
    connectedNode = []

    def __init__(self, tx, vin ,vout, fee, spent) -> None:
        self.transaction = tx
        self.vin_list = vin
        self.vout_list = vout
        self.fee = fee
        self.spented = spent

    def addNewNode(self, nextNode : 'node'):
        self.connectedNode.append(nextNode)

class Crawler:
    queueTransactions = None

    def __init__(self, start) -> None:
        self.baseUrl = 'https://hashxp.org/tx/'
        self.queueTransactions = Queue()
        self.queueTransactions.put(start)

    def get_address_type(self, data, target, listObtainedData):
        data_list = data.select(target)
        if 'vin' in target:
            for data in data_list:
                address = data.find('tt', class_='btcaddr')
                listObtainedData.append(address.text)
                type = data.find('b')
        else:
            for data in data_list:
                address = data.find('tt', class_='btcaddr')
                listObtainedData.append(address.text)
                type = data.find('b')
                if data.find('text') != None:
                    spent = data.find('text')
                else:
                    tx = data.find('a', class_='btctx', href=True).attrs['href'][4:-4]
    

    def crawling_data(self):
        start = self.queueTransactions.get()
        response = re.post(url=self.baseUrl+start)
        if response.status_code != 200:
            time.sleep(5)
            response = re.post(url=self.baseUrl+start)
        
        # Get HTML's hashio2 data(vin, vout, ...)
        soup = bs(response.text, "html.parser")
        hashio2 = soup.find('div', class_="hashio2")
        vins_data = hashio2.find('div', id='vins')
        vouts_data = hashio2.find('div', id='vouts')
        list_datas = [vins_data, vouts_data]
        list_obtained_vin = []
        list_obtained_vout = []
        list_target = ['div[id^="vin"]', 'div[id^="vout"]']

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

        print(list_obtained_vout)