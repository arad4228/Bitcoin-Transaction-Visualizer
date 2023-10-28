from Crawler import *
from Graph import *

# start = 'bf05f899c90589cdd3c42a44d032e28933fa819a1c5c19e44d37b2be592afb6b'
# fc359e4309594551cfe597e7bb061189795a25130414886903ac7340271e98a1 
# c882cbecc2da0ca7ca6465f831a5770fbb7b0f4aceeeeccda81be06d3d6dbc62  
# e1aa3eef4368a5ec6b7c3f8c251a141b67bb7b9cfa3ea1f3109b1250fc8374e7

start = 'e1aa3eef4368a5ec6b7c3f8c251a141b67bb7b9cfa3ea1f3109b1250fc8374e7'

try:
    cr = Crawler(start=start)
    cr.crawling_data()
    cr.save_data(start)
# Drawing(start)

except Exception as e:
    print(f"{e} 오류 발생")
    cr.save_data(start)
    # Drawing(start)

except :
    cr.save_data(start)
    Drawing(start)