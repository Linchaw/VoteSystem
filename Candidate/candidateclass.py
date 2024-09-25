import random

class Candiadte():
    def __init__(self):
        # self.Vt = []
        # self.vid = 99
        # self.PK = MyElGammal.PublicKey()
        # self.pk = MyElGammal.PublicKey()
        # self.sk = MyElGammal.PrivateKey()
        pass

    def signup(self):
        self.name = input("请输入姓名：")
        self.id = input("请输入ID:")
        self.pwd = input("请输入密码:")
        self.signupFlag = False

        if len(self.pwd) < 8:
            ex = Exception("密码长度不能小于8位")
            raise ex

    def login(self):
        self.id = input("输入ID:")
        self.pwd = input("输入密码:")
        self.loginFlag = False
    
