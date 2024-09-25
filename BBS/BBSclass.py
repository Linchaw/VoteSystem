import socket, json, time
RAaddr = ("127.0.0.1",6686)

class BBS:
    def __init__(self):
        pass

    def initBBS(self):
        # 连接到RAS服务器
        print("-"*8,"公告板系统正在信息初始化","-"*8)
        BBc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("-"*8,"正在连接服务器","-"*8)
        while True:
            try:
                BBc_socket.connect(RAaddr)
                break
            except:
                print("连接失败，正在重试")
                time.sleep(1)
        print("-"*8,"连接成功","-"*8)

        # 获取 RAS 服务器信息
        initinfo = {"type":"BBS","aim":"getOS"}
        while True:
            BBc_socket.send(json.dumps(initinfo).encode())
            udata1 = BBc_socket.recv(1024).decode()
            udata2 = BBc_socket.recv(1024).decode()
            (data1,data2) = (json.loads(udata1),json.loads(udata2))
            if data1["type"] == "RAS" and data1["recall"] == "getOK" and data1["Ftype"] == "pubInfo":
                if data2["type"] == "RAS" and data2["recall"] == "getOK" and data2["Ftype"] == "priInfo":
                    break
        
        # 对 RAS 服务器的信息进行处理
        data1.update({"type":"BBS"})
        data2.update({"type":"BBS"})
        print("-"*8,"已有{}位候选者成功注册，请输入获选者数量：".format(len(data1["Clist"])),"-"*8)
        data1["k"] = int(input())
        data3 = {"Vlist":data1["Vlist"],"k":data1["k"]}
        for i in data3["Vlist"]:
            data3["{}-vote".format(i)] = None

        self.pubInfo = data1
        self.priInfo = data2
        self.voteInfo = data3

        # 对处理后的信息进行存储
        with open("BBS\pubInfo.json","w") as f:
            f.write(json.dumps(self.pubInfo))
        with open("BBS\priInfo.json","w") as f:
            f.write(json.dumps(self.priInfo))
        with open("BBS\VoteInfo.json","w") as f:
            f.write(json.dumps(self.voteInfo))
        
        print("-"*8,"公告板系信息初始化完成","-"*8)
        self.showInfo()

        # 关闭与 RAS 服务器的连接
        fininfo = {"type":"BBS","aim":"Over"}
        BBc_socket.send(json.dumps(fininfo).encode())
        BBc_socket.close()

    def loadBBS(self):
        print("-"*8,"正在加载BBS服务器","-"*8)

        # 从存储文件中加载数据
        with open("BBS\pubInfo.json","r") as f:
            self.pubInfo = json.loads(f.read())
        with open("BBS\priInfo.json","r") as f:
            self.priInfo = json.loads(f.read())
        with open("BBS\VoteInfo.json","r") as f:
            self.voteInfo = json.loads(f.read())

        self.showInfo()
        print("-"*8,"BBS服务器加载完成","-"*8)

    def showInfo(self):
        print(self.priInfo)
        print(self.pubInfo)
        print(self.voteInfo)