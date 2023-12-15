# 安装问题
卸载所有名字中带 crypto 的，然后再安装 pip install pycryptodome
# RSA 使用
```
import os.path

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

def generate_key(_public_path,_private_path,bits=2048):
    if os.path.exists(_public_path) and os.path.exists(_private_path):
        return
    # if os.path.exists(_private_path):
    #     os.remove(_private_path)
    # if os.path.exists(_public_path):
    #     os.remove(_public_path)
    private_key = RSA.generate(bits=bits)
    with open(_public_path, "wb") as f:
        f.write(private_key.publickey().export_key())
    with open(_private_path, "wb") as f:
        f.write(private_key.export_key())

def encryption_decryption(_public_path, _private_path, _message = u"你好，我的全世界！"):
    bytes_message = bytes(_message, encoding ="utf-8")
    with open (_public_path,"rb") as f:
        _public_key = RSA.importKey(f.read())
    cipher = PKCS1_OAEP.new(_public_key)
    encrypted_message = cipher.encrypt(bytes_message)
    print(f"加密后的数据:{encrypted_message}")
    
    with open (_private_path,"rb") as f:
        _private_key = RSA.importKey(f.read())
    cipher = PKCS1_OAEP.new(_private_key)
    decrypted_message = cipher.decrypt(encrypted_message)
    print(f'解密后的数据:{decrypted_message.decode("utf-8")}')

if __name__ == '__main__':
    key_dir = os.path.dirname(__file__) # 当前文件的文件夹路径
    private_path = os.path.join(key_dir,"id_rsa")
    public_path = os.path.join(key_dir,"id_rsa.pub")
    generate_key(_public_path=public_path,_private_path=private_path,bits=2048)
    encryption_decryption(_public_path=public_path,_private_path=private_path)
```

# AES 使用
```
import os
from hashlib import md5
from Crypto.Cipher import AES
from os import urandom

def derive_key_and_iv(password, salt, key_length, iv_length): #derive key and IV from password and salt.
    d = d_i = b''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + str.encode(password) + salt).digest() #obtain the md5 hash value
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def encrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size #16 bytes
    salt = urandom(bs) #return a string of random bytes
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write(salt)
    finished = False

    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:#final block/chunk is padded before encryption
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += str.encode(padding_length * chr(padding_length))
            finished = True
        out_file.write(cipher.encrypt(chunk))

def decrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = chunk[-1]
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(bytes(x for x in chunk))


password = '123456789' # 你应该使用强度高的密码

with open("origin.txt","w+",encoding="utf-8") as f:
    f.write("你好，我的全世界！")

with open('origin.txt', 'rb') as in_file, open('encrypt_origin.txt', 'wb') as out_file:
    encrypt(in_file, out_file, password)

with open('encrypt_origin.txt', 'rb') as in_file, open('decrypt_origin.txt', 'wb') as out_file:
    decrypt(in_file, out_file, password)
    
is_delete = False
if is_delete:
    files = ['origin.txt','encrypt_origin.txt','decrypt_origin.txt']
    for file in files:
        os.remove(file)
```
# 其他
AES 详细分析：<https://www.cnblogs.com/Hellowshuo/p/15706590.html>
