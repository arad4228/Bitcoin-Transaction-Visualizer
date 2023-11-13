from Web_Crawler import *
from RPC_Crawler import *

# start = 'bf05f899c90589cdd3c42a44d032e28933fa819a1c5c19e44d37b2be592afb6b'
# fc359e4309594551cfe597e7bb061189795a25130414886903ac7340271e98a1 
# c882cbecc2da0ca7ca6465f831a5770fbb7b0f4aceeeeccda81be06d3d6dbc62  
# e1aa3eef4368a5ec6b7c3f8c251a141b67bb7b9cfa3ea1f3109b1250fc8374e7

start_list = ['bf05f899c90589cdd3c42a44d032e28933fa819a1c5c19e44d37b2be592afb6b', 'fc359e4309594551cfe597e7bb061189795a25130414886903ac7340271e98a1', 'c882cbecc2da0ca7ca6465f831a5770fbb7b0f4aceeeeccda81be06d3d6dbc62', 'e1aa3eef4368a5ec6b7c3f8c251a141b67bb7b9cfa3ea1f3109b1250fc8374e7']
end_list = ['62d398b57580943f3292868d0e80f450cf6c67b6413bfa977b2443d08cc47e3a', 'df4738ba36031416919dfdf8af5b40990d969847fd64335fbaad66054e11127c', 'e1ca3c173b49d96f3f07db0f4e465b03da2d2b02f9b7cd592f912141cc1dd63a', 'None']

mode = 'RPC'
end_transaction_number = 3000
Result = '\Result_Json'

for start, end in zip(start_list, end_list):
    try:
        if mode == 'Web':
            cr = Web_Crawler(start, end_transaction_number)
        else:
            if end == 'None':
                continue
            cr = RPC_Crawler(end, end_transaction_number)

        cr.crawling_data()
        if cr == "Web":
            cr.save_data(Result, start)
        else:
            cr.save_data(Result, end)
        time.sleep(30)

    except Exception as e:
        print(f"{e} 오류 발생")
        if cr == "Web":
            cr.save_data(Result, start)
        else:
            cr.save_data(Result, end)
        continue

    except :
        if cr == "Web":
            cr.save_data(Result, start)
        else:
            cr.save_data(Result, end)
        continue
