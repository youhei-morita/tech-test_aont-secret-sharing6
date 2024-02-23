import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def split_message_to_bytes(message, num_blocks):
    # メッセージをスペースで分割して単語ごとのリストにする
    words = message.split()
    
    # 単語数をブロック数で分割する
    words_per_block = len(words) // num_blocks
    
    # 分割されたブロックを格納するリスト
    blocks = []

    # 単語数がブロック数で割り切れない場合、余りを処理するための変数
    remainder = len(words) % num_blocks
    
    # ブロックごとに単語を割り当てる
    start = 0
    for i in range(num_blocks):
        # 残りの余りが0でない場合、1つのブロックに余りを追加する
        if remainder > 0:
            block_length = words_per_block + 1
            remainder -= 1
        else:
            block_length = words_per_block
        
        # ブロックを作成し、ブロックリストに追加
        block = ' '.join(words[start:start+block_length])
        # ブロックをバイト表現に変換して追加
        block_bytes = block.encode('utf-8')
        blocks.append(block_bytes)
        
        # 次の開始位置を更新
        start += block_length

    return blocks

blocks = []

# 平文
m = "This message is for practicing AONT distributed processing."
# 分割するブロック数
num_blocks = 5

# メッセージを分割してブロックを取得
blocks_bytes = split_message_to_bytes(m, num_blocks)

# ブロックを出力
for i, block_bytes in enumerate(blocks_bytes):
    print(f"m_{i+1}: {block_bytes}")

# 鍵の長さ（バイト単位）
key_length = 16  # 例として16バイトの鍵を生成します

# ランダムなバイト列を生成して鍵として使用する
k = os.urandom(key_length)

# 共通鍵暗号の鍵を表示
print("共通鍵暗号の鍵:", k)

# 鍵の長さ（バイト単位）
key_length = 16  # 例として16バイトの鍵を生成します

# ランダムなバイト列を生成して鍵として使用する
k_0 = os.urandom(key_length)

# 公開された共通鍵暗号の鍵を表示
print("公開された共通鍵暗号の鍵:", k_0)

def pad(data):
    # PKCS7 パディングを適用
    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length] * padding_length)
    return padded_data

def Enc(key, plaintext):
    # 鍵と初期化ベクトル（IV）の生成
    iv = os.urandom(16)  # 16バイトのIVを生成
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # データをパディング
    padded_plaintext = pad(plaintext)

    # 暗号化
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    return iv + ciphertext

# 暗号化する鍵
key = b'\x00' * 16

# 暗号化するデータ
m = b'This message is for practicing AONT distributed processing.'

# 暗号化
encrypted_data = Enc(key, m)
print("任意の共通鍵暗号化:", encrypted_data)

# 各ブロックを m2_i に変換
m2_blocks = []
for i, block in enumerate(blocks, start=1):
    # ブロックをバイト列に変換
    block_bytes = block.encode('utf-8')
    
    # Enc 関数を使用して暗号化し、ブロックを変換
    encrypted_block = Enc(k, bytes([i]))  # i をバイト列に変換して暗号化に渡す
    m2_block = bytes(a ^ b for a, b in zip(block_bytes, encrypted_block))
    
    m2_blocks.append(m2_block)

# 結果を出力
for i, m2_block in enumerate(m2_blocks, start=1):
    print(f"m2_{i}: {m2_block}")

hash_values = []
for i, block in enumerate(blocks, start=1):
# m2_i + i の排他的論理和を計算
    xor_result = bytes(a ^ b for a, b in zip(block_bytes, bytes([i])))
    
    # Enc 関数を使用して暗号化し、ハッシュ値を計算
    hash_value = Enc(k_0, xor_result)
    
    hash_values.append(hash_value)

# 結果を出力
for i, hash_value in enumerate(hash_values, start=1):
    print(f"h_{i}: {hash_value}")

# m2_(s+1) を計算
m2_splus1 = k
for hash_value in hash_values:
    m2_splus1 = bytes(a ^ b for a, b in zip(m2_splus1, hash_value))

# 結果を出力
print(f"m2_(s+1): {m2_splus1}")

# 共通鍵暗号の鍵 k を破棄する
del k

#シェアのハッシュ値（再掲）
for i, hash_value in enumerate(hash_values, start=1):
    print(f"h_{i}: {hash_value}")

# 排他的論理和を計算する関数
def xor_bytes(bytes_list):
    result = bytes_list[0]
    for b in bytes_list[1:]:
        result = bytes(a ^ b for a, b in zip(result, b))
    return result

# 共通鍵の復号
result = xor_bytes([m2_splus1] + hash_values)
print("復号された共通鍵:", result)

# Enc 関数を使用して暗号化
encrypted_result = Enc(result, bytes([i]))

# m2_iと復号した共通鍵の排他的論理和を計算    
for i, m2_block in enumerate(m2_blocks, start=1):
    decrypted_block= bytes(a ^ b for a, b in zip(m2_block, encrypted_result))   
    print(f"復号されたm_{i}: ",decrypted_block)
