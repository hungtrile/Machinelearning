class User:
    def __init__(self,id=None,username=None,password=None,is_banned=False,role=None):
        self.id = id
        self.username = username
        self.password = password
        self.is_banned = is_banned
        self.role = role