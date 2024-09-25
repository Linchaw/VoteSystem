import socket, json, random, time
import threading
from MyCrypto import MyElGammal
from BBS import BBSclass

def OSstart(bbs):  # 1.初始化注册机构服务器 2.加载注册机构服务器
    while True:
        print("-"*8,"1.初始化公告板服务器； 2.加载缓存公告板服务器； 3.退出","-"*8)
        choice = int(input("请选择："))
        if choice == 1:
            bbs.initBBS()
            break
        elif choice == 2:
            bbs.loadBBS()
            break
        elif choice == 3:
            exit()
        else:
            print("输入错误，请重新输入")

def VoterLogin(conn, bbs, data):
    if data["ID"] in bbs.priInfo["Vlist"] and data["PWD"] == bbs.priInfo["{}-PWD".format(data["ID"])]:
        tmp = {"type":"BBS","recall":"LoginSuccess","vID":bbs.priInfo["{}-vID".format(data["ID"])]}
    else:
        tmp = {"type":"BBS","recall":"LoginFail"}
    conn.send(json.dumps(tmp).encode())

def CandidateLogin(conn,bbs,data):
    if data["ID"] in bbs.priInfo["Clist"] and data["PWD"] == bbs.priInfo["{}-PWD".format(data["ID"])]:
        cid = bbs.priInfo["{}-cID".format(data["ID"])]
        tmp = {"type":"BBS","recall":"LoginSuccess",
                "cID":cid,"name":bbs.pubInfo["{}-name".format(cid)]}
    else:
        tmp = {"type":"BBS","recall":"LoginFail"}
    conn.send(json.dumps(tmp).encode())

def dealVote(conn,bbs,data):
    # {"type":"Voter","aim":"Vote","vID":v.vid,"vote":v.Vtc}
    bbs.voteInfo["{}-vote".format(data["vID"])] = data["vote"]
    tmp = {"type":"BBS","recall":"VoteSuccess"}
    conn.send(json.dumps(tmp).encode())

    #计算投票密文结果
    bbs.voteInfo["Vote"] = []
    for j in range(len(bbs.voteInfo["Vlist"])+1):
        bbs.voteInfo["Vote"].append([1,1])
    for i in bbs.voteInfo["Vlist"]:
        if bbs.voteInfo["{}-vote".format(i)] is not None:
            tmpvote = bbs.voteInfo["{}-vote".format(i)]
            for j in range(len(bbs.voteInfo["Vlist"])+1):
                bbs.voteInfo["Vote"][j][0] = bbs.voteInfo["Vote"][j][0] * tmpvote[j][0] % bbs.pubInfo["p"]
                bbs.voteInfo["Vote"][j][1] = bbs.voteInfo["Vote"][j][1] * tmpvote[j][1] % bbs.pubInfo["p"]
    with open("BBS\VoteInfo.json","w") as f:
        f.write(json.dumps(bbs.voteInfo))

def dealWinner(conn,bbs,data):
    tmp = data["winCandidate"]
    bbs.pubInfo["winCadidate"] = []
    for i in tmp :
        vname = bbs.pubInfo["{}-name".format(i)]
        bbs.pubInfo["winCadidate"].append(vname)
    with open("BBS\pubInfo.json","w") as f:
        f.write(json.dumps(bbs.pubInfo))
    print("-"*8,"投票结束，获胜者为：","-"*8)
    print(bbs.pubInfo["winCadidate"])

    FineInfo = {"type":"BBS","recall":"FINE"}
    conn.send(json.dumps(FineInfo).encode())

def BackVoteInfo(conn,bbs):
    tmp = {}
    tmp.update(bbs.voteInfo)
    tmp.update({"type":"BBS",'recall':'VoteInfo'})
    conn.send(json.dumps(tmp).encode())

def BackPubInfo(conn,bbs):
    tmp = {}
    tmp.update(bbs.pubInfo)
    tmp.update({"recall":"PubInfo"})
    conn.send(json.dumps(tmp).encode())

def DealConns(conn,bbs):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        data = json.loads(data.decode())
        print(data)
        if data["type"] == "Voter":
            if data["aim"] == "Login":
                VoterLogin(conn,bbs,data)
            elif data["aim"] == "PubInfo":
                BackPubInfo(conn, bbs)
            elif data["aim"] == "Vote":
                dealVote(conn,bbs,data)
            elif data["aim"] == "Check":
                pass
            elif data["aim"] == "Over":
                break
        elif data["type"] == "Candidate":
            if data["aim"] == "Login":
                CandidateLogin(conn,bbs,data)
            elif data["aim"] == "PubInfo":
                pass
            
            elif data["aim"] == "Over":
                break
        elif data["type"] == "RAS":
            if data["aim"] == "CountVote":
                BackVoteInfo(conn,bbs)
            elif data["aim"] == "WinCandidate":
                dealWinner(conn,bbs,data)
            elif data["aim"] == "Over":
                break
            

def main():
    bbs = BBSclass.BBS()
    OSstart(bbs)

    BBSs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    BBSs.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    BBSs.bind(("127.0.0.1",6688))
    BBSs.listen(5)
    print("-"*8,"等待连接","-"*8)
    while True:
        con, ipport = BBSs.accept()
        print("connect from:", ipport)
        sub_thread = threading.Thread(target=DealConns, args=(con,bbs))
        sub_thread.start()

    BBSs.close()

if __name__ == "__main__":
    main()