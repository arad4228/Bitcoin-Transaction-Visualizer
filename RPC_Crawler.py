from bitcoinrpc.authproxy import AuthServiceProxy
from threading import Thread
from collections import OrderedDict
from RPC_Config import *
import json
import os

# Crawling Backward Transactions
class RPC_Crawler:

    def __init__(self, end, end_transaction_count:'int') -> None:
        self.end = end
        self.rpc_connect = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")
        self.queueTransactions = OrderedDict()
        self.queueTransactions[end] = "end"
        self.iteration = 0
        self.end_transaction_number = end_transaction_count
        self.json_list = list()

    def __str__(self) -> str:
        return 'RPC'

    def get_address_info(self, data, target, listObtainedData):
        if target == 'vin':
            for vins in data:
                vin = dict()
                if 'coinbase' in vins:
                    address = 'Coinbase'
                    type = 'Coinbase'
                    money = '0'
                else:
                    utxo_transaction_id = vins['txid']
                    utxo_transaction = self.rpc_connect.getrawtransaction(utxo_transaction_id, 2)
                    utxo_location = vins['vout']
                    address = utxo_transaction['vout'][utxo_location]['scriptPubKey']['address']
                    type = 'Unknown'
                    money = str(utxo_transaction['vout'][utxo_location]['value'])

                spent = "spent"
                vin['address'] = address
                vin['type'] = type
                vin['spent'] = spent
                vin['money'] = money
                listObtainedData.append(vin)
                if address != 'Coinbase':
                    self.queueTransactions[utxo_transaction_id] = address
        else:
            for vouts in data:
                vout = dict()
                if 'address' in vouts['scriptPubKey']:
                    address = vouts['scriptPubKey']['address']
                else:
                    address = "Unknown"
                type = 'Unknown'
                spent = 'Unknown'
                money = str(vouts['value'])
                vout['address'] = address
                vout['type'] = type
                vout['spent'] = spent
                vout['money'] = money
                listObtainedData.append(vout)

    def crawling_data(self):
        while self.iteration <= self.end_transaction_number:
            transaction, addr = self.queueTransactions.popitem(last=False)
            print(f'Iter: {self.iteration}, transaction: {transaction}')

            # Dict 형식으로 가져온다.
            rpc_transaction = self.rpc_connect.getrawtransaction(transaction, 2)
            vin_list = list()
            vout_list = list()
            list_datas = [rpc_transaction['vin'], rpc_transaction['vout']]
            list_target = ['vin', 'vout']
            threads = []

            for data, target in zip(list_datas, list_target):
                if 'vin' in target:
                    ths = Thread(target=self.get_address_info, args=(data, target, vin_list))
                else:
                    ths = Thread(target=self.get_address_info, args=(data, target, vout_list))
                threads.append(ths)
                ths.start()

            for th in threads:
                th.join()
                
            json = dict()
            json['transaction'] = transaction
            json['vin'] = vin_list
            json['vout'] = vout_list
            self.json_list.append(json)
            self.iteration+=1
    
    def reverse_json_list(self):
        self.json_list.reverse

    def save_data(self, location, starttransaction):
        path = os.getcwd()
        if location not in path:
            os.chdir(path+location)      
        self.reverse_json_list()
        with open(f'RPC_{starttransaction}.json', 'a', encoding='UTF-8') as f:
            json.dump(self.json_list, f)