import hashlib
import os.path
import zipfile
from os import urandom

from Crypto.Cipher import AES


class UserCrypto(object):
    def __init__(self,in_file,out_file,_password):
        self.block_size = 16 # 这里可以改为 self.block_size = AES.block_size 必须是16的倍数
        self.iv_length = 16
        self.key_length = 32
        self.password = _password
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
            d_i = hashlib.sha256(d_i + str.encode(_password) + _salt).digest()
            # d_i = hashlib.md5(d_i + str.encode(_password) + _salt).digest()  # 获取md5哈希值（md5已经被破解，不安全）
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
        
def compress_dir(_input_dir,_output_file):
    z = zipfile.ZipFile(_output_file, mode="w", compression=zipfile.ZIP_DEFLATED, allowZip64=True)
    for root,dirs,files in os.walk(_input_dir):
        fpath = root.replace(_input_dir,"") # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        for file in files:
            z.write(os.path.join(root,file),arcname=os.path.join(fpath,file))

def TEST_UserCrypto(is_clean=False):
    basedir = os.path.dirname(__file__)
    filename = "origin.txt"
    origin_file = os.path.join(basedir,filename)
    with open(origin_file,'w',encoding='utf-8') as f:
        f.write("Hello,World.")
    encrypt_file = os.path.join(os.path.dirname(origin_file),"encrypt_"+os.path.basename(origin_file))
    decrypt_file = os.path.join(os.path.dirname(origin_file),"decrypt_"+os.path.basename(origin_file))
    # user_password = input("请输入密码：")
    user_password = "kevin"
    UserCrypto(origin_file,encrypt_file,_password=user_password).encrypt()
    UserCrypto(encrypt_file,decrypt_file,_password=user_password).decrypt()
    if is_clean:
        os.remove(origin_file)
        os.remove(encrypt_file)
        os.remove(decrypt_file)
        
def TEST_compress_encrypt():
    input_dir = r""
    password = "kevin"
    # input_dir = input("请输入需要打包的文件夹完整路径：")
    # _password = input("请输入密码：")
    father_dir ,fold_name = os.path.split(input_dir)
    zip_file = os.path.join(father_dir,fold_name+".zip")
    compress_dir(_input_dir=input_dir,_output_file=zip_file)
    file_dir,file_name  = os.path.split(zip_file)
    encrypt_file = os.path.join(file_dir,"encrypt_"+ file_name)
    UserCrypto(in_file=zip_file,out_file=encrypt_file,_password=password).encrypt()
    decrypt_file = os.path.join(file_dir, "decrypt_" + file_name)
    UserCrypto(in_file=encrypt_file,out_file=decrypt_file,_password=password).decrypt()
    
if __name__ == '__main__':
    TEST_UserCrypto(False)
