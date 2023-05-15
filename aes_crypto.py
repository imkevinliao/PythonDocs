import os.path
from hashlib import md5
from os import urandom

from Crypto.Cipher import AES


class UserCrypto(object):
    def __init__(self,in_file,out_file,password):
        self.block_size = 16 # 这里可以改为 self.block_size = AES.block_size 必须是16的倍数
        self.iv_length = 16
        self.key_length = 32
        self.password = password
        self.in_filepath = in_file
        self.out_filepath = out_file
    def set_aes_mode(self, mode="AES-256"):
        if "AES-256" == mode:
            self.key_length = 32
        elif "AES-192" == mode:
            self.key_length = 24
        elif "AES-128" == mode:
            self.key_length = 16
    def set_password(self,value):
        self.password = value
    @staticmethod
    def __derive(_password, _salt, key_length, iv_length):
        d = d_i = b""
        while len(d) < (key_length + iv_length):
            d_i = md5(d_i + str.encode(_password) + _salt).digest()  # 获取md5哈希值
            d += d_i
        return d[0:key_length], d[key_length:key_length + iv_length]
    def encrypt(self):
        salt = urandom(self.block_size) # 为了使相同的密码拥有不同的hash值的一种手段，就是盐化。作为二次输入并入单向函数或加密函数，用于导出口令验证数据的随机变量。
        secret_key , iv = self.__derive(self.password,salt,self.key_length,self.iv_length)
        cipher = AES.new(secret_key,AES.MODE_CBC,iv)
        is_finished = False
        in_file = open(self.in_filepath,'rb')
        out_file = open(self.out_filepath,'wb')
        out_file.write(salt)
        while not is_finished:
            chunk =in_file.read(1024*self.block_size)
            if len(chunk) == 0 or len(chunk) % self.block_size != 0:  # 加密前填充最终块
                padding_length = (self.block_size - len(chunk) % self.block_size) or self.block_size
                chunk += str.encode(padding_length * chr(padding_length))
                is_finished = True
            out_file.write(cipher.encrypt(chunk))
        in_file.close()
        out_file.close()
    
    def decrypt(self):
        in_file = open(self.in_filepath,'rb')
        out_file = open(self.out_filepath,'wb')
        salt = in_file.read(self.block_size)
        secret_key, iv = self.__derive(self.password, salt, self.key_length, self.iv_length)
        cipher = AES.new(secret_key, AES.MODE_CBC, iv)
        next_chunk = ""
        is_finished = False
        while not is_finished:
            chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * self.block_size))
            if len(next_chunk) == 0:
                padding_length = int(chunk[-1])
                chunk = chunk[:-padding_length]
                is_finished = True
            out_file.write(bytes(x for x in chunk))
        in_file.close()
        out_file.close()


origin_file = os.path.join(os.path.dirname(__file__),"origin.txt")
with open(origin_file,'w',encoding='utf-8') as f:
    f.write("Hello,World.")
encrypt_file = os.path.join(os.path.dirname(origin_file),"encrypt_"+os.path.basename(origin_file))
decrypt_file = os.path.join(os.path.dirname(origin_file),"decrypt_"+os.path.basename(origin_file))

UserCrypto(origin_file,encrypt_file,password="123456").encrypt()
UserCrypto(encrypt_file,decrypt_file,password="123456").decrypt()

is_delete = False
if is_delete:
    os.remove(origin_file)
    os.remove(encrypt_file)
    os.remove(decrypt_file)
