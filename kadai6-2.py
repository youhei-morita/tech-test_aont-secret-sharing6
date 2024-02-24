mport os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def split_message_to_bytes(message, num_blocks):
    words = message.split()
    words_per_block = len(words) // num_blocks
    blocks = []
    remainder = len(words) % num_blocks
    
    start = 0
    for i in range(num_blocks):
        if remainder > 0:
            block_length = words_per_block + 1
            remainder -= 1
        else:
            block_length = words_per_block
        
        block = ' '.join(words[start:start+block_length])
        block_bytes = block.encode('utf-8')
        blocks.append(block_bytes)
        
        start += block_length

    return blocks

blocks = []
m = "This message is for practicing AONT distributed processing."
num_blocks = 5

blocks_bytes = split_message_to_bytes(m, num_blocks)

for i, block_bytes in enumerate(blocks_bytes):
    print(f"m_{i+1}: {block_bytes}")

key_length = 16
k = os.urandom(key_length)
print("共通鍵暗号の鍵:", k)

key_length = 16
k_0 = os.urandom(key_length)
print("公開された共通鍵暗号の鍵:", k_0)

def pad(data):
    padding_length = 16 - (len(data) % 16)
    padded_data = data + bytes([padding_length] * padding_length)
    return padded_data

def Enc(key, plaintext):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padded_plaintext = pad(plaintext)

    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    
    return iv + ciphertext

key = b'\x00' * 16
m = b'This message is for practicing AONT distributed processing.'
encrypted_data = Enc(key, m)
print("任意の共通鍵暗号化:", encrypted_data)

m2_blocks = []
for i, block in enumerate(blocks_bytes, start=1):
    block_bytes = block
    
    encrypted_block = Enc(k, bytes([i]))
    m2_block = bytes(a ^ b for a, b in zip(block_bytes, encrypted_block))
    
    m2_blocks.append(m2_block)

for i, m2_block in enumerate(m2_blocks, start=1):
    print(f"m2_{i}: {m2_block}")

hash_values = []
for i, block in enumerate(blocks_bytes, start=1):
    block_bytes = block
    xor_result = bytes(a ^ b for a, b in zip(block_bytes, bytes([i])))
    hash_value = Enc(k_0, xor_result)
    hash_values.append(hash_value)

for i, hash_value in enumerate(hash_values, start=1):
    print(f"h_{i}: {hash_value}")

m2_splus1 = k
for hash_value in hash_values:
    m2_splus1 = bytes(a ^ b for a, b in zip(m2_splus1, hash_value))

print(f"m2_(s+1): {m2_splus1}")

for i, hash_value in enumerate(hash_values, start=1):
    print(f"h_{i}: {hash_value}")

def xor_bytes(bytes_list):
    result = bytes_list[0]
    for b in bytes_list[1:]:
        result = bytes(a ^ b for a, b in zip(result, b))
    return result

result = xor_bytes([m2_splus1] + hash_values)
print("復号された共通鍵:", result)

decrypted_blocks = []
for i, m2_block in enumerate(m2_blocks, start=1):
    decrypted_block= bytes(a ^ b for a, b in zip(m2_block, result))   
    print(f"復号されたm_{i}: {decrypted_block}")
    decrypted_blocks.append(decrypted_block)

decrypted_message = b"".join(decrypted_block for decrypted_block in decrypted_blocks)
print("復号されたメッセージ:", decrypted_message.decode)
