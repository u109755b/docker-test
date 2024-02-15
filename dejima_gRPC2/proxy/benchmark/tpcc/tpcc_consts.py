# scale factor {W} = ceil( {the number of peers} / 10 )
# {W} : {the number of peers} = 1 : 10

# the number of records inserted when it is loaded
# warehouse
# 1 / 10 peers

# district
# 1 / peer

# customer
RECORDS_NUM_CUSTOMER = 3000 # 3,000 / peer
BATCH_SIZE_CUSTOMER = 1000

# stock
RECORDS_NUM_STOCK = 10000   # 10,000 / peer
BATCH_SIZE_STOCK = 500

# oorder
RECORDS_NUM_OORDER = 3000   # 3000 / peer

# item
RECORDS_NUM_ITEM = 100000   # 100,000 / overall
