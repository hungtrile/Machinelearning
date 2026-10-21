from demo_salesdatabase.dal.customerDAO import customerDAO

df = customerDAO.getCustomer()

print(df.columns)