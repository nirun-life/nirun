"""
# Dependency
```
pip install cryptography
```
"""
import base64
import time
import secrets
import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import zlib


def presense_token_encode(secret_token: str, patient_id: str) -> str:
    """
    ใช้เข้ารหัสข้อมูลเพื่อสร้าง token ไว้ส่งยัง presense server
    :param secret_token: secret token ที่ใช้เข้ารหัสข้อมูล โดยจะเป็นเลขฐาน 16 ที่มีความยาว 96 ตัวอักษร
    :param patient_id: รหัสผู้ป่วย
    """
    if len(secret_token) != 96:
        raise ValueError("Invalid secret token length")

    key_str = secret_token[0:64]
    iv_str = secret_token[64:]

    key = bytes.fromhex(key_str)
    iv = bytes.fromhex(iv_str)

    salt_base64 = base64.b64encode(secrets.token_bytes(8)).decode('utf-8')
    unix_time = int(time.time())

    # สร้าง checksum จาก salt, patient_id และเวลา
    for_check_sum = salt_base64 + patient_id + str(unix_time)
    crc32_checksum = zlib.crc32(for_check_sum.encode('utf-8'))

    # สร้างข้อมูลที่จะเข้ารหัส จาก salt, patient_id เวลา และ checksum
    data = {
        "salt": salt_base64,
        "id": patient_id,
        "time": unix_time,
        "cksum": crc32_checksum
    }
    json_data = json.dumps(data)
    json_data_bytes = json_data.encode('utf-8')

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_data_bytes) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return ciphertext.hex()
