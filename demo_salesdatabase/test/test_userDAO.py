from demo_salesdatabase.dal.userDAO import userDAO

uid="admin"
pwd="123"
us=userDAO.login(uid,pwd)
if us is None:
    print("Login Failed")
else:
    print("Welcome:",us.username)