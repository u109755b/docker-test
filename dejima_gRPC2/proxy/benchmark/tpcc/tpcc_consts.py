W_P_N = 10   # 10 peers / warehouse

# scale factor {W} = ceil( {the number of peers} / {W_P_N} )
# {W} : {the number of peers} = 1 : {W_P_N}

# the number of records inserted when it is loaded
# warehouse
# 1 record / {W_P_N} peers

# district
# 10 records / {W_P_N} peers

# customer
RECORDS_NUM_CUSTOMER = 3000     # 3,000 records / district
BATCH_SIZE_CUSTOMER = 1000

# stock
RECORDS_NUM_STOCK = 100000      # 100,000 records / {W_P_N} peers
BATCH_SIZE_STOCK = 500

# oorder
RECORDS_NUM_OORDER = 3000       # 3,000 records / district

# item
RECORDS_NUM_ITEM = 100000       # 100,000 records / overall
