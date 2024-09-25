import socket, json, random, time
import threading
from MyCrypto import MyElGammal as EG
from RAS import RASclass as ras      

def OSstart(rs):  # 1.初始化注册机构服务器 2.加载注册机构服务器
    while True:
        print("-"*8,"1.初始化一个注册服务器； 2.加载上一次的注册服务器； 3.开始计票工作；  4.exit","-"*8)
        choice = int(input("请选择："))
        if choice == 1:
            rs.initRS()
            break
        elif choice == 2:
            rs.loadsRS()
            break
        elif choice == 3:
            rs.counting()
            break
        elif choice == 4:
            exit()
        else:
            print("输入错误，请重新输入")

def check(rs,data):
    return True

def VoterSignup(conn, rs, data):
    # data = {"type":"Voter","aim":"VoterSignup","ID":v.id,"PWD":v.pwd,"VPK":v.pk.y}

    # 审查选民资格
    if check(rs,data) == False :
        redata = {"type":"RAS","recall":"ERROR"}
        conn.send(json.dumps(redata).encode())
        return

    # 判断选民是否已经注册
    if data["ID"] in rs.priInfo["Vlist"]:
        rs.priInfo["{}-PWD".format(data["ID"])] = data["PWD"]
        rs.pubInfo["{}-vpk".format(rs.priInfo["{}-vID".format(data["ID"])])] = data["VPK"]

    else:
        rs.priInfo["Vlist"].append(data["ID"])
        rs.priInfo["{}-PWD".format(data["ID"])] = data["PWD"]
        rs.priInfo["{}-vID".format(data["ID"])] = len(rs.priInfo["Vlist"])
        rs.pubInfo["Vlist"].append(rs.priInfo["{}-vID".format(data["ID"])])
        rs.pubInfo["{}-vpk".format(rs.priInfo["{}-vID".format(data["ID"])])] = data["VPK"]

    #存储注册信息
    with open("RAS\priInfo.json","w") as f:
        f.write(json.dumps(rs.priInfo))
    with open("RAS\pubInfo.json","w") as f:
        f.write(json.dumps(rs.pubInfo))

    redata = {"type":"RAS","recall":"SignupSuccess","vID":rs.priInfo["{}-vID".format(data["ID"])]}
    conn.send(json.dumps(redata).encode())

def CandidateSignup(conn, rs, data):
    # 审查候选者资格
    if check(rs,data) == False :
        redata = {"type":"RAS","recall":"ERROR"}
        conn.send(json.dumps(redata).encode())
        return
    
    # 判断候选者是否已经注册
    if data["ID"] in rs.priInfo["Clist"]:
        rs.priInfo["{}-PWD".format(data["ID"])] = data["PWD"]
        rs.pubInfo["{}-name".format(rs.priInfo["{}-cID".format(data["ID"])])] = data["name"]
    
    else:
        rs.priInfo["Clist"].append(data["ID"])
        rs.priInfo["{}-PWD".format(data["ID"])] = data["PWD"]
        rs.priInfo["{}-cID".format(data["ID"])] = len(rs.priInfo["Clist"])
        rs.pubInfo["Clist"].append(rs.priInfo["{}-cID".format(data["ID"])])
        rs.pubInfo["{}-name".format(rs.priInfo["{}-cID".format(data["ID"])])] = data["name"]

    #存储注册信息
    with open("RAS\priInfo.json","w") as f:
        f.write(json.dumps(rs.priInfo))
    with open("RAS\pubInfo.json","w") as f:
        f.write(json.dumps(rs.pubInfo))
    
    # 返回候选者人注册成功的信息
    redata = {"type":"RAS","recall":"SignupSuccess","cID":len(rs.priInfo["Clist"])}
    conn.send(json.dumps(redata).encode())

# 给 BBS 服务器返回选民和候选者的登记信息
def BBSIfno(conn,rs):
    redata1 = {"type":"RAS","recall":"getOK","Ftype":"pubInfo"}
    redata1.update(rs.pubInfo)
    conn.send(json.dumps(redata1).encode())

    redata2 = {"type":"RAS","recall":"getOK","Ftype":"priInfo"}
    redata2.update(rs.priInfo)
    conn.send(json.dumps(redata2).encode())

def CVOSInfo(conn,rs):
    redata = {}
    redata.update(rs.pubInfo)
    redata.update({"type":"RAS","recall":"getOK"})
    conn.send(json.dumps(redata).encode())

def DealConns(conn,rs):
    while True:
        data =  conn.recv(1024)
        if not data:
            break
        data = json.loads(data.decode())
        print(data)

        # 与选民的通信数据处理
        if data["type"] == "Voter":
            # 选民获取系统参数 
            if data["aim"] == "getPubInfo": 
                CVOSInfo(conn,rs)
            # 选民注册
            elif data["aim"] == "VoterSignup": 
                VoterSignup(conn, rs, data)
            # 选民结束连接
            elif data["aim"] == "Over":
                break
            else:
                redata = {"type":"RAS","recall":"ERROR"}
                conns.send(json.dumps(redata).encode())
        
        # 与候选者的通信数据处理
        elif data["type"] == "Candidate":
            # 候选者获取系统信息
            if data["aim"] == "getOS": 
                CVOSInfo(conn,rs)
            # 候选者注册
            elif data["aim"] == "CandidateSignup":
                CandidateSignup(conn, rs, data)
            # 候选者结束与 RAS 服务器连接
            elif data["aim"] == "Over":
                break
            else:
                redata = {"type":"RAS","recall":"ERROR"}
                conns.send(json.dumps(redata).encode())
        
        elif data["type"] == "BBS":
            if data["aim"] == "getOS":
                BBSIfno(conn,rs)
            elif data["aim"] == "Over":
                break
        else:
            redata = {"type":"error"}
            conns.send(json.dumps(redata).encode())
    conn.close()


def main():
    # 初始化注册机构服务器
    rs = ras.RAserver() 
    OSstart(rs) 

    # 建立服务器连接
    RASs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    RASs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    RASs.bind(("127.0.0.1",6686))
    RASs.listen(5)
    print("服务器已启动，等待客户端连接...")
    while True:
        conn, ipport = RASs.accept()
        print("connect from:", ipport)
        sub_thread = threading.Thread(target=DealConns, args=(conn,rs))
        sub_thread.start()
    
    RASs.close()
    
if __name__ == "__main__":
    main()