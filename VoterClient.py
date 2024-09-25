import socket, json, time, os
from Voter import voteclass
from MyCrypto import MyElGammal as EG

RAaddr = ("127.0.0.1",6686)
BSaddr = ("127.0.0.1",6688)

def SendandWait(con,data):
    con.send(json.dumps(data).encode())
    redata = con.recv(2048).decode()
    print(json.loads(redata))
    return json.loads(redata)

# 选民注册
def VoterSignup(): 
    # 连接到RAS服务器
    Rvc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("-"*8,"正在连接服务器","-"*8)
    while True:
        try:
            Rvc_socket.connect(RAaddr)
            break
        except:
            print("连接失败，正在重试")
            time.sleep(1)
    print("-"*8,"连接成功","-"*8)

    # 获取系统参数
    while True:
        initinfo = {"type":"Voter","aim":"getPubInfo"}
        OSInfo = SendandWait(Rvc_socket,initinfo)
        if OSInfo["type"] == "RAS" and OSInfo["recall"] == "getOK":
            break
    
    # 初始化选民对象，并注册
    v = voteclass.Voter()
    v.initkey(OSInfo["p"],OSInfo["g"])
    v.PK = EG.PublicKey(OSInfo["p"],OSInfo["g"],OSInfo["pk"])
    v.signup()
    print("-"*8,"正在注册","-"*8)
    RegisterInfo = {"type":"Voter","aim":"VoterSignup","ID":v.id,"PWD":v.pwd,"VPK":v.pk.y}
    BackInfo = SendandWait(Rvc_socket,RegisterInfo)

    # 对 RAS 服务的返回消息进行处理
    if BackInfo["type"] == "RAS" and BackInfo["recall"] == "SignupSuccess":
        v.signupFlag = True
        print("-"*8,"注册成功","-"*8)
    else:
        print("-"*8,"注册失败","-"*8)
    
    # 注册成功后，选民存储信息
    if v.signupFlag:
        v.vid = BackInfo["vID"]
        v.vInfo = {"ID":v.vid,"PWD":v.pwd,"vID":v.vid,
                    "p":v.PK.p,"g":v.PK.g,"pk":v.PK.y,
                    "vpk":v.pk.y,"vsk":v.sk.x}
        with open("Voter\{}-vInfo.json".format(v.vid),"w") as f:
            f.write(json.dumps(v.vInfo))

    # 关闭与RAS服务器的连接
    finInfo = {"type":"Voter","aim":"Over"}
    Rvc_socket.send(json.dumps(finInfo).encode())
    Rvc_socket.close()

# 选民登录
def VoterLogin():
    # 连接到BBS服务器 
    Bvc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("-"*8,"正在连接服务器","-"*8)
    while True:
        try:
            Bvc_socket.connect(BSaddr)
            break
        except:
            print("连接失败，正在重试")
            time.sleep(1)
    print("-"*8,"连接成功","-"*8)

    # 初始化选民对象，并登录
    v = voteclass.Voter()
    v.login()
    initinfo = {"type":"Voter","aim":"Login","ID":v.id,"PWD":v.pwd}
    LoginInfo = SendandWait(Bvc_socket,initinfo)

    # 选民登录返回信息
    if LoginInfo["type"] == "BBS" and LoginInfo["recall"] == "LoginSuccess":
        print("-"*8,"登录成功","-"*8)
        v.loginFlag = True
    else:
        print("-"*8,"登录失败","-"*8)
    
    # 选民登录成功
    if v.loginFlag:
        v.vid = LoginInfo["vID"]
        with open("Voter\{}-vInfo.json".format(v.vid),"r") as f:
            v.vInfo = json.loads(f.read())
        v.PK = EG.PublicKey(v.vInfo["p"],v.vInfo["g"],v.vInfo["pk"])

        while True:
            tmp = {"type":"Voter","aim":"PubInfo"}
            pubInfo = SendandWait(Bvc_socket,tmp)
            if pubInfo["type"] == "BBS" and pubInfo["recall"] == "PubInfo":
                v.pubInfo = pubInfo
                break
        while True:
            print("-"*8,"1:Vote   2:ReNewBBSInfo   3:Exit","-"*8)
            choice = input("请输入您的选择：")
            if choice == "1":
                voterVote(Bvc_socket,v)
            elif choice == "2":
                ReNewBBSInfo(Bvc_socket)
            elif choice == "3":
                break
            else:
                print("-"*8,"输入错误，请重新输入","-"*8)
    
    # 选民断开与 BBS 服务器的连接
    finInfo = {"type":"Voter","aim":"Over"}
    Bvc_socket.send(json.dumps(finInfo).encode())
    Bvc_socket.close()

def voterVote(Bvc_socket,v):
    print("-"*8,"正在投票","-"*8)
    m = len(v.pubInfo["Clist"])
    k = v.pubInfo["k"]
    for i in range(m):
        print("-"*8,"第{}个候选者人名为：{}".format(i+1,v.pubInfo["{}-name".format(i+1)]),"-"*8)
    v.vote(k,m)

    temp = {"type":"Voter","aim":"Vote","vID":v.vid,"vote":v.Vtc}
    print("-"*8,"正在发送投票信息","-"*8)
    BackInfo = SendandWait(Bvc_socket,temp)

    if BackInfo["type"] == "BBS" and BackInfo["recall"] == "VoteSuccess":
        print("-"*8,"投票成功","-"*8)
    else:
        print("-"*8,"投票失败","-"*8)

def ReNewBBSInfo(Bvc_socket):
    initInfo = {"type":"Voter","aim":"PubInfo"}
    BackInfo = SendandWait(Bvc_socket,initInfo)
    if BackInfo["type"] == "BBS" and BackInfo["recall"] == "getOK":
        print("-"*8,"获取公共信息成功","-"*8)
    else:
        print("-"*8,"获取公共信息失败","-"*8)
    print(BackInfo)

def main():
    print("-"*8,"欢迎使用投票系统-选民客户端","-"*8)
    while True:
        print("-"*8,"1:Regist   2:Login   3:Exit","-"*8)
        choice = input("请输入您的选择：")
        if choice == "1": #注册
            VoterSignup()
        elif choice == "2": #登录vote
            VoterLogin()
        elif choice == "3":
            break
        else:
            print("-"*8,"输入错误，请重新输入","-"*8)

    os.system("pause")
    
if __name__ == "__main__":
    main()