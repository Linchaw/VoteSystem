from MyCrypto import MyElGammal as EG
import socket, json, math

BSaddr = ("127.0.0.1",6688)

class RAserver:
    def __init__(self):
        self.Sort = {}
        self.winCandidate = []

    def initRS(self):
        print("-"*8,"正在初始化注册机构服务器","-"*8)
        self.im = int(input("请输入系统素数大小(为2的阶数)："))
        self.p = EG.find_prime(self.im)
        self.g = EG.find_primitive_root(self.p)
        self.key = EG.genkeyspg(self.p, self.g)
        self.pk = self.key.get("publicKey")
        self.sk = self.key.get("privateKey")
        self.KeyInfo ={"p":self.p,"g":self.g,"pk":self.pk.y,"sk":self.sk.x}
        self.pubInfo = {"Clist":[],"Vlist":[],"p":self.p,"g":self.g,"pk":self.pk.y}
        self.priInfo = {"Clist":[],"Vlist":[]}
        with open("RAS\KeyInfo.json","w") as f:
            f.write(json.dumps(self.KeyInfo))
        with open("RAS\pubInfo.json","w") as f:
            f.write(json.dumps(self.pubInfo))
        with open("RAS\priInfo.json","w") as f:
            f.write(json.dumps(self.priInfo))
        print("-"*8,"注册机构服务器初始化完成","-"*8)
    
    def loadsRS(self):
        print("-"*8,"正在加载注册机构服务器","-"*8)
        try :
            with open("RAS\KeyInfo.json","r") as f:
                self.KeyInfo = json.loads(f.read())
            with open("RAS\pubInfo.json","r") as f:
                pubInfo = json.loads(f.read())
            with open("RAS\priInfo.json","r") as f:
                priInfo = json.loads(f.read())
        except :
            print("-"*8,"加载注册机构服务器失败，请重新初始化","-"*8)
        else :
            self.p = self.KeyInfo.get("p")
            self.g = self.KeyInfo.get("g")
            self.pk = EG.PublicKey(self.p,self.g,self.KeyInfo.get("pk"))
            self.sk = EG.PrivateKey(self.p,self.g,self.KeyInfo.get("sk"))
            self.pubInfo = pubInfo
            self.priInfo = priInfo
            print("-"*8,"注册机构服务器加载完成","-"*8)


    def counting(self):
        # 连接到 BBS 服务器
        self.loadsRS()
        BRc_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("-"*8,"正在连接公告板服务器","-"*8)
        while True:
            try :
                BRc_socket.connect(BSaddr)
                break
            except :
                print("-"*8,"连接服务器失败，正在重新连接","-"*8)
        print("-"*8,"连接公告板服务器成功","-"*8)

        # 获取 BBS 服务器投票信息
        initInfo = {"type":"RAS","aim":"CountVote"}
        BRc_socket.send(json.dumps(initInfo).encode())
        data = BRc_socket.recv(2048)
        data = json.loads(data.decode())
        
        if data.get("type") == "BBS" and data.get("recall") == "VoteInfo":
            print("-"*8,"收到投票信息","-"*8)
            self.vote = data["Vote"]
            vote = []
            for i in range(1,len(self.vote)):
                vote.append(EG.decryptNum(self.sk, self.vote[i]))
            print("-"*8,"解密投票信息","-"*8)
            dict = {}
            s = []
            for i in range(len(vote)):
                dict["{}".format(i+1)] = int(math.log2(vote[i]))
                s.append(int(math.log2(vote[i])))
            s.sort(reverse=True)
            for i in range(len(s)):
                self.Sort["{}".format(i+1)] = s.index(dict["{}".format(i+1)])+1
            print("-"*8,"投票信息计算完成","-"*8)
            for key, value in self.Sort.items():
                if value <= data["k"]:
                    self.winCandidate.append(key)
            print(self.winCandidate)
            winInfo = {"type":"RAS","aim":"WinCandidate","winCandidate":self.winCandidate}
            BRc_socket.send(json.dumps(winInfo).encode())
            data = BRc_socket.recv(2048)
            data = json.loads(data.decode())
            if data.get("type") == "BBS" and data.get("recall") == "FINE":
                print("-"*8,"注册机构服务器结束","-"*8)
            else:
                print("-"*8,"注册机构服务器结束失败","-"*8)
        else:
            print("-"*8,"收到错误信息","-"*8)
        

        # 关闭与 BBS 服务器的连接
        finInfo = {"type":"RAS","aim":"Over"}
        BRc_socket.send(json.dumps(finInfo).encode())
        BRc_socket.close()


