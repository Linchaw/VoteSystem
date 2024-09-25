import random
from MyCrypto import MyElGammal

class Voter():
    def __init__(self):
        self.Vt = []
        self.vid = 99
        self.PK = MyElGammal.PublicKey()
        self.pk = MyElGammal.PublicKey()
        self.sk = MyElGammal.PrivateKey()
    
    def initkey(self, p = None, g = None):
        key = MyElGammal.genkeyspg(p, g)
        self.sk = key.get("privateKey")
        self.pk = key.get("publicKey")
        # self.PK.p = p
        # self.PK.g = g

    def signup(self):
        self.id = input("输入ID:")
        self.pwd = input("输入密码:")
        self.signupFlag = False

        if len(self.pwd) < 8:
            ex = Exception("密码长度不能小于8位")
            raise ex

    def login(self):
        self.id = input("输入ID:")
        self.pwd = input("输入密码:")
        self.loginFlag = False
    
    def vote(self,k,m):
        #将选票 vt[0]设计为vid
        self.vt = [int(self.vid)]

        kv = 0
        for j in range(1,m+1):
            vj = input("是否对候选人{}投票？(Y/N): ".format(j))
            if vj == 'Y' or vj == 'y':
                kv += 1
                self.vt.append(2)
            elif vj == 'N' or vj == 'n':
                self.vt.append(1)
            else:
                ex = Exception("输入错误")
                raise ex
        
        if kv <= k:
            self.mixVote()
            self.encryptVote()
            print("投票结果加密成功")
        else:
            print("投票失败,投票数量不能超过{}".format(k))
    
    def mixVote(self):
        r = random.choice([1, 2, 4])
        self.vm = [1]

        l = len(self.vt) - 1
        while  l > 0:
            self.vm.append(r)
            l -= 1

        for i in range(len(self.vm)):
            self.Vt.append(self.vm[i]*self.vt[i])
    
    def encryptVote(self):
        self.Vtc = []
        for i in range(len(self.Vt)):
            self.Vtc.append(MyElGammal.encryptNum(self.PK, self.Vt[i]))
        print(self.Vtc)

    def showInfo(self):
        print("-"*8,"选民信息","-"*8)
        print("ID:",self.id)
        print("密码:",self.pwd)
        print("素数:",self.PK.p)
        print("生成元:",self.PK.g)
        print("公钥:",self.PK.y)
        print("-"*8,"投票信息","-"*8)
    
def main():#测试使用  但是需将此文件放入与MyCrypto文件同一目录下
    v = Voter()
    p = MyElGammal.find_prime(32)
    g = MyElGammal.find_primitive_root(p)
    key = MyElGammal.genkeyspgi(p, g)
    pk = key.get("publicKey")
    v.PK.y = pk.y
    v.initkey(p, g)
    v.signup()
    v.login()
    v.vote(2,5)

if __name__ == "__main__":
    main()

    

        

