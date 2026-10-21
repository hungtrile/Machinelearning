from demo_salesdatabase.connectors.connector import Connector

conn=Connector()
conn.connect()
sql="SELECT * FROM customer_spend_score"
df=conn.queryDataset(sql)
print(df)
sql2="select * from customer"
df2=conn.queryDataset(sql2)
print(df2)
sql3="select * from users"
df3=conn.queryDataset(sql3)
print(df3)
uid="admin"
pwd="1234"
sql4="select * from users where username=%s AND password=%s"
val=(uid,pwd)
df4=conn.queryDataset(sql4,val)
print(df4)
if df4 is None:
    print("Login Failed")
sql5="select * from customer where Age>=%s AND Age<=%s"
val=(19,25)
df5=conn.queryDataset(sql5,val)
print(df5)
sql6="select * from customer where CustomerID=%s"
val=(40,)
df6=conn.queryDataset(sql6,val)
print(df6)
