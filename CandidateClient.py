import socket, json, time, os
from Candidate import candidateclass as CC

RAaddr = ("127.0.0.1",6686)
BSaddr = ("127.0.0.1",6688)

def SendandWait(con,data):
    con.send(json.dumps(data).encode())
    redata = con.recv(1024).decode()
    print(redata)
    return json.loads(redata)

def CandidateSignup():
    # 连接 RAS 服务器
    Rcc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("-"*8,"正在连接服务器","-"*8)
    while True:
        try:
            Rcc_socket.connect(RAaddr)
            break
        except:
            print("连接失败，正在重试")
            time.sleep(1)
    print("-"*8,"连接成功","-"*8)

    # 获取系统参数
    while True:
        initInfo = {"type":"Candidate","aim":"getOS"}
        OSInfo = SendandWait(Rcc_socket,initInfo)
        if OSInfo["type"] == "RAS" and OSInfo["recall"] == "getOK":
            break

    # 初始化候选者对象，并注册
    c = CC.Candiadte()
    c.signup()
    RegInfo = {"type":"Candidate","aim":"CandidateSignup","ID":c.id,"PWD":c.pwd,"name":c.name}
    BackInfo = SendandWait(Rcc_socket,RegInfo)

    # 对 RAS 服务的返回消息进行处理
    if BackInfo["type"] == "RAS" and BackInfo["recall"] =="SignupSuccess":
        c.signupFlag = True
        print("-"*8,"注册成功","-"*8)
    else:
        print("-"*8,"注册失败","-"*8)
        print(BackInfo)
    
    # 注册成功后，选民存储信息
    if c.signupFlag:
        c.cid = BackInfo["cID"]
        c.cInfo = {"name":c.name,"ID":c.id,
                    "PWD":c.pwd,"cID":c.cid,}
        with open("Candidate\{}-cInfo.json".format(c.cid),"w") as f:
            f.write(json.dumps(c.cInfo))

    # 关闭与 RAS 服务器的连接
    finInfo = {"type":"Candidate","aim":"Over"}
    Rcc_socket.send(json.dumps(finInfo).encode())
    Rcc_socket.close()

def CandidateLogin():
    # 连接到 BBS 服务器
    Bcc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("-"*8,"正在连接服务器","-"*8)
    while True:
        try:
            Bcc_socket.connect(BSaddr)
            break
        except:
            print("连接失败，正在重试")
            time.sleep(1)
    print("-"*8,"连接成功","-"*8)

    # 初始化候选者对象，并登录
    c = CC.Candiadte()
    c.login()
    initInfo = {"type":"Candidate","aim":"Login","ID":c.id,"PWD":c.pwd}
    BackInfo = SendandWait(Bcc_socket,initInfo)

    # 对 BBS 返回的消息处理
    if BackInfo["type"] == "BBS" and BackInfo["recall"] == "LoginSuccess":
        c.loginFlag = True
        print("-"*8,"登录成功","-"*8)
    else:
        print("-"*8,"登录失败","-"*8)
    
    # 登录成功
    if c.loginFlag:
        c.cid = BackInfo["cID"]
        c.name = BackInfo["name"]
        c.cInfo = {"name":c.name,"ID":c.id,
                    "PWD":c.pwd,"cID":c.cid,}
        with open("Candidate\{}-cInfo.json".format(c.cid),"w") as f:
            f.write(json.dumps(c.cInfo))
    

def main():
    print("-"*8,"欢迎使用投票系统-候选者客户端","-"*8)
    while True:
        print("-"*8,"1:Regist   2:Login   3:Exit","-"*8)
        choice = input("请输入您的选择：")
        if choice == "1": #注册
            CandidateSignup()
        elif choice == "2": #登录
            CandidateLogin()
        elif choice == "3":
            break
        else:
            print("-"*8,"输入错误，请重新输入","-"*8)
    os.system("pause")
    
if __name__ == "__main__":
    main()