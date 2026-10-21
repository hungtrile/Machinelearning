from demo_salesdatabase.connectors.connector import Connector
from demo_salesdatabase.models.user import User


class userDAO:
    @staticmethod
    def login(uid,pwd):
        conn = Connector()
        conn.connect()
        sql = "select * from users where username=%s AND password=%s"
        val = (uid, pwd)
        df = conn.queryDataset(sql, val)
        if df is None:
            return None#login failed
        us=User()
        us.username=uid
        us.password=pwd
        us.is_banned=df["is_banned"]
        us.role=df["role"]
        return us