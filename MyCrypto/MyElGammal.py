"""
	这是一个ElGammal数字加密算法模块，不支持字符加密！！！
	包含了两个类：
		1. ElGammalPublicKey：用于生成公钥 p g h iNumBits
		2. ElGammalPrivateKey：用于生成私钥 p g x iNumBits
	实现了的功能有：
		大素数的生成：find_prime()
		对于一个有限域中生成元的求解：find_primitive_root()
		对数字的加密和解密：encryptNum() decryptNum()
		对密文进行同态转换：transCiper()
	作者：黄林超
"""

import random
import math
import sys

#私钥
class PrivateKey(object):
	def __init__(self, p=None, g=None, x=None):
		self.p = p
		self.g = g
		self.x = x

#公钥
class PublicKey(object):
	def __init__(self, p=None, g=None, y=None):
		self.p = p
		self.g = g
		self.y = y

#生成密钥对，以字典形式返回，参数带有素数和生成元
def genkeyspg(p,g):
		x = random.randint( 1, (p - 1) // 2 )
		y = modexp( g, x, p )
		publicKey = PublicKey(p, g, y)
		privateKey = PrivateKey(p, g, x)
		return {'privateKey': privateKey, 'publicKey': publicKey}

#数字加密
def encryptNum(pk, num):
		k = random.randint(1, pk.p - 1)
		c1 = pow(pk.g, k, pk.p)
		c2 = num * pow(pk.y, k, pk.p) % pk.p
		return [c1, c2]

#数字解密
def decryptNum(sk, cipher):
		c1 = cipher[0]
		c2 = cipher[1]
		v = pow(c1, sk.x, sk.p)
		v_1 = e_gcd(v, sk.p)[1]
		m_d = c2 * v_1 % sk.p
		return m_d

#密文转换
def transCiper(pk, cipher):
		[x,y] = encryptNum(pk, 1)
		[c1, c2] = cipher
		c1 = c1 * x % pk.p
		c2 = c2 * y % pk.p
		return [c1, c2]

#分布式ElGammal算法-解密步骤1
def getGxp(sk, cipher):
	c1 = cipher[0]
	v = pow(c1, sk.x, sk.p)
	return v

#分布式ElGammal算法-解密步骤2
def getM(p,cipher):
	v_1 = e_gcd(cipher[0], p)[1]
	m_d = cipher[1] * v_1 % p
	return m_d

#ElGammal-数字签名
def sign(sk, m):
	k = random.randint(1, sk.p - 2)
	while gcd(k, sk.p - 1) != 1:
		k = random.randint(1, sk.p - 2)
	r = pow(sk.g, k, sk.p)
	tmp = e_gcd(k, sk.p-1)[1] % (sk.p-1)
	s = (tmp * (m - sk.x * r) ) % (sk.p - 1)
	return [r, s]

#ElGammal-数字签名验证
def verify(pk, m, signature):
	r = signature[0]
	s = signature[1]
	v1 = pow(pk.g, m, pk.p)
	print(v1)
	v2 = (pow(pk.y,r,pk.p) * pow(r,s,pk.p)) % pk.p
	print(v2)
	if v1 == v2:
			return True
	else:
			return False

#欧几里得求逆元
def e_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x, y = e_gcd(b, a%b)
    return g, y, x-a//b*y  #1.gcd 2.a^-1 mod b 3.b^-1 mod a

#最大公因数运算
def gcd( a, b ):
		while b != 0:
			c = a % b
			a = b
			b = c
		return a

#模幂运算
def modexp(base, exp, modulus):
		return pow(base, exp, modulus)

#solovay-strassen 素性检验
def SS(num, iConfidence):
		#iConfidence为素性检验的次数
		for i in range(iConfidence):
				a = random.randint( 1, num-1 )
				if gcd( a, num ) > 1:
						return False
				if not jacobi( a, num ) % num == modexp ( a, (num-1)//2, num ):
						return False
		return True

#计算jacobi积
def jacobi(a, n):
    if a == 0:
            if n == 1:
                    return 1
            else:
                    return 0
    elif a == -1:
            if n % 2 == 0:
                    return 1
            else:
                    return -1
    elif a == 1:
            return 1
    elif a == 2:
            if n % 8 == 1 or n % 8 == 7:
                    return 1
            elif n % 8 == 3 or n % 8 == 5:
                    return -1
    elif a >= n:
            return jacobi( a%n, n)
    elif a%2 == 0:
            return jacobi(2, n)*jacobi(a//2, n)
    else:
            if a % 4 == 3 and n%4 == 3:
                    return -1 * jacobi( n, a)
            else:
                    return jacobi(n, a )

#寻找有限域的生成元
def find_primitive_root(p):
    if p == 2:
            return 1
    p1 = 2
    p2 = (p-1) // p1 #结果为素数

    #重复随机生成整数，直到找到g
    while( 1 ):
            g = random.randint( 2, p-1 )
            if not (modexp( g, (p-1)//p1, p ) == 1):
                    if not modexp( g, (p-1)//p2, p ) == 1:
                        g = modexp( g, 2, p )
                        return g

#生成大素数
def find_prime(iNumBits=256, iConfidence=32):
		while(1):
				#生成大奇数
				p = random.randint( 2**(iNumBits-2), 2**(iNumBits-1) )
				while( p % 2 == 0 ):
						p = random.randint(2**(iNumBits-2),2**(iNumBits-1))

				#素性检测
				while( not SS(p, iConfidence) ):
						p = random.randint( 2**(iNumBits-2), 2**(iNumBits-1) )
						while( p % 2 == 0 ):
								p = random.randint(2**(iNumBits-2), 2**(iNumBits-1))
                #p-1 只有2个因子
				p = p * 2 + 1
				if SS(p, iConfidence):
						return p

def main():#TEST
    p = find_prime(32)
    g = find_primitive_root(p)
    print("生成素数测试：p =", p)
    print("寻找生成元测试：g =", g)
    key = genkeyspg(p, g)
    sk = key["privateKey"]
    pk = key["publicKey"]
    print("生成私钥测试：sk =", sk.x)
    print("生成公钥测试：pk =", pk.y)
    m = 12345
	
    cipher = encryptNum(pk, m)
    print("加密测试：cipher =", cipher)
    m_d = decryptNum(sk, cipher)
    print("解密测试：m_d =", m_d)

    cipher2 = transCiper(pk, cipher)
    print("密文转换测试：cipher2 =", cipher2)
    m_d3 = decryptNum(sk, cipher2)
    print("转换密文解密测试：m_d2 =", m_d3)

    cipher[0] = getGxp(sk, cipher)
    print("分布式解密-1 测试：cipher =", cipher)
    m_d2 = getM(p, cipher)
    print("分布式解密-1 测试：m_d2 =", m_d2)

    s = sign(sk, m)
    print("签名测试：s =", s)
    v = verify(pk, m, s)
    print("验证测试：v =", v)    

if __name__ == "__main__":
    main()