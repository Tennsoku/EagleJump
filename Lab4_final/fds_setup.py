import pandas as pd
import pymysql

conn = pymysql.connect(host='...', user="...", passwd="...",
                      db="csc326lab3", port=3306)

word_id = pd.read_sql('select word_id from Lexicon;', con=conn)

print word_id