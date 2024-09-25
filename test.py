import math
from MyCrypto import MyElGammal as EG

# #欧几里得求逆元
# def e_gcd(a, b):
#     if b == 0:
#         return a, 1, 0
#     g, x, y = e_gcd(b, a%b)
#     return g, y, x-a//b*y  #1.gcd 2.a^-1 mod b 3.b^-1 mod a


sk = EG.PrivateKey(29,2,12)
pk = EG.PublicKey(29,2,7)
# print(5*17%28)
x = 26
s =EG.sign(sk, x)
print(s)
print(EG.verify(pk, x, s))


# import json
# import math 

# with open("RAS\KeyInfo.json","r") as f:
#     tmp = json.loads(f.read())
# with open("BBS\pubInfo.json","r") as f:
#     tmp2 = json.loads(f.read())
# Vote = tmp2["Vote"]
# sk = EG.PrivateKey(tmp["p"],tmp["g"],tmp["sk"])

# m = []
# for i in range(len(Vote)):
#     m.append(EG.decryptNum(sk, Vote[i]))
# # print(m)

# dict = {}
# s = []
# for i in range(1,len(m)):
#     dict["{}".format(i)] = int(math.log2(m[i]))
#     s.append(int(math.log2(m[i])))

# s.sort(reverse=True)
# print(s)
# print(dict)
# Sort = {}
# for i in range(len(s)):
#     Sort["{}".format(i+1)] = s.index(dict["{}".format(i+1)])+1
# print(Sort)
    

# v = V.Voter()
# p = V.MyElGammal.find_prime(32)
# g = V.MyElGammal.find_primitive_root(p)
# key = V.MyElGammal.genkeyspg(p, g)
# pk = key.get("publicKey")
# v.PK.y = pk.y
# v.initkey(p, g)
# v.signup()
# v.login()
# v.vote(2,5)

