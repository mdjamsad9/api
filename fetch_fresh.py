import time
import urllib.request
import binascii
import base64
import json
import os
from Crypto.Cipher import AES

# Load dynamic configuration
config_path = "app_control.json"
if not os.path.exists(config_path):
    # Fallback to defaults if file is missing
    active_name = "cricfy"
    profile = {
        "genz_url": "https://p.genzdev.xyz/2-xmnhab.json",
        "token": "8f4gha9affeegg7cigafdgc7hegfkefaicigdgg1haffhekgeeigcfgahedfhef",
        "aes_key": "WT1sdkEvUlR4ckd2",
        "aes_iv": "Q7sKcm9LR4VaX2pN",
        "xor_key": 90,
        "keys": {
            "event_cats.json": "2c68753f2c3f342e05393b2e29742e222e",
            "events.json": "2c68753f2c3f342e29742e222e",
            "channels.json": "2c687539323b34343f3629750f69182c39340820131f322c380d0f3d0f12102c170e3968150e0b6a170e1769151e036a171b742e222e"
        }
    }
else:
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    active_name = config.get("active_source", "cricfy")
    profile = config["sources"][active_name]

print(f"Active Source Profile: {active_name}")

genz_url = profile["genz_url"]
token = profile["token"]
aes_key_bytes = profile["aes_key"].encode('utf-8')
aes_iv_bytes = profile["aes_iv"].encode('utf-8')
xor_key_val = profile["xor_key"]
keys = profile["keys"]

# Determine user github pages url based on context or env, default to mdjamsad9/api
github_user = os.environ.get("GITHUB_REPOSITORY_OWNER", "mdjamsad9")
github_repo = os.environ.get("GITHUB_REPOSITORY", "mdjamsad9/api").split("/")[-1]
base_pages_url = f"https://{github_user}.github.io/{github_repo}/decrypted_output/"

def encrypt_xor_hex(text):
    data = text.encode('utf-8')
    encrypted = bytes([b ^ xor_key_val for b in data])
    return binascii.hexlify(encrypted).decode('utf-8')

def cfgMaterial():
    bArr = [29, 88, 17, 104, 66, 7, 91, 34, 113, 5, 47, 96]
    bArr2 = [71, 12, 83, 44, 9, 121, 36, 58, 101, 22, 63]
    bArr3 = [6, 39, 95, 14, 74, 52, 117, 27, 68, 3, 86, 41, 109]
    bArr4 = bytearray(32)
    for i in range(32):
        i10 = bArr[i % 12] & 255
        i11 = bArr2[((i * 3) + 1) % 11] & 255
        i12 = i & 7
        
        shift_r = 8 - i12
        term1 = (i11 & 0xffffffff) >> shift_r
        term2 = (i11 << i12) & 0xffffffff
        rotated = (term1 | term2) & 255
        
        val = (((i10 ^ rotated) ^ (bArr3[((i * 5) + 2) % 13] & 255)) ^ 90) ^ i
        bArr4[i] = val & 255
    return bArr4

def decrypt_cfj1(str_val):
    str_val = str_val.strip()
    if str_val.startswith("cfj1:"):
        str_val = str_val[5:]
    
    str_val = str_val.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "")
    bArrDecode = base64.b64decode(str_val)
    bArrCfgMaterial = cfgMaterial()
    bArr = bytearray(len(bArrDecode))
    
    for i in range(len(bArrDecode)):
        val = (((bArrCfgMaterial[i % len(bArrCfgMaterial)] & 255) ^ bArrDecode[i]) ^ (((i * 29) + 71) & 255)) & 255
        bArr[len(bArrDecode) - 1 - i] = val
        
    return bArr.decode('utf-8', errors='ignore')

def swap_pairs(chars):
    for i in range(0, len(chars) - 1, 2):
        chars[i], chars[i+1] = chars[i+1], chars[i]
    return chars

def reverse_chars(chars):
    return chars[::-1]

def clean_base64(s):
    sb = []
    for c in s:
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z') or ('0' <= c <= '9') or c == '+' or c == '/':
            sb.append(c)
    s_cleaned = "".join(sb)
    while len(s_cleaned) % 4 != 0:
        s_cleaned += '='
    return s_cleaned

def decrypt_aes_v2(ciphertext):
    cipher = AES.new(aes_key_bytes, AES.MODE_CBC, aes_iv_bytes)
    decrypted = cipher.decrypt(ciphertext)
    pad_len = decrypted[-1]
    if 1 <= pad_len <= 16:
        if all(x == pad_len for x in decrypted[-pad_len:]):
            decrypted = decrypted[:-pad_len]
    return decrypted

def decode_v2(encoded_str):
    try:
        decoded_bytes = base64.b64decode(encoded_str)
        char_array = list(decoded_bytes.decode('utf-8', errors='ignore'))
        char_array = swap_pairs(char_array)
        char_array = reverse_chars(char_array)
        decoded_str2 = "".join(char_array)
        
        if not decoded_str2.endswith("abcdefghijklmnop"):
            return f"Error: Decoded stage 1 does not end with abcdefghijklmnop. Output was: {decoded_str2[:100]}..."
        
        sub_str = decoded_str2[:-len("abcdefghijklmnop")]
        sub_bytes = base64.b64decode(sub_str)
        decrypted_aes = decrypt_aes_v2(sub_bytes)
        
        char_array_aes = list(decrypted_aes.decode('utf-8', errors='ignore'))
        char_array_aes = swap_pairs(char_array_aes)
        char_array_aes = reverse_chars(char_array_aes)
        
        cleaned_b64 = clean_base64("".join(char_array_aes))
        final_bytes = base64.b64decode(cleaned_b64)
        return final_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Decoding error: {e}"

def make_request(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Cricfy2/1.0'})
    response = urllib.request.urlopen(req, timeout=15)
    return response.read().decode('utf-8').strip()

# Target directory
out_dir = "decrypted_output"
os.makedirs(out_dir, exist_ok=True)

# 1. Decrypt genzdev config
if genz_url:
    print("Processing URL 1 (GenzDev)...")
    try:
        raw_genz = make_request(genz_url)
        dec_genz = decrypt_cfj1(raw_genz)
        parsed_genz = json.loads(dec_genz)
        
        # Inject custom routing URLs for the app developer (Single Entry Point)
        parsed_genz["api_url"] = base_pages_url
        parsed_genz["api2"] = base_pages_url
        parsed_genz["categories_api"] = f"{base_pages_url}categories.json"
        parsed_genz["events_api"] = f"{base_pages_url}events.json"
        parsed_genz["channels_api_base"] = f"{base_pages_url}channels/"
        
        with open(os.path.join(out_dir, "genzdev_config.json"), "w", encoding="utf-8") as f:
            json.dump(parsed_genz, f, indent=2, ensure_ascii=False)
        print("-> Decrypted genzdev_config.json successfully!")
    except Exception as e:
        print("-> Failed URL 1:", e)

# Token for HMAC
current_time = int(time.time())
fresh_hmac_plain = f"{current_time}|{token}"
fresh_hmac_encrypted = encrypt_xor_hex(fresh_hmac_plain)

# 2. Fetch Category List
categories_path = "v2/categories.txt"
categories_key = encrypt_xor_hex(categories_path)
categories_url = f"https://cricyplayers.com/data/getData.php?key={categories_key}&hmac={fresh_hmac_encrypted}"
print("Processing categories.json...")
try:
    raw_cats = make_request(categories_url)
    dec_cats = decode_v2(raw_cats)
    parsed_cats = json.loads(dec_cats)
    
    with open(os.path.join(out_dir, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(parsed_cats, f, indent=2, ensure_ascii=False)
    print("-> Decrypted categories.json successfully!")
    
    # Create channels directory
    channels_dir = os.path.join(out_dir, "channels")
    os.makedirs(channels_dir, exist_ok=True)
    
    # 3. Iterate and fetch each category's channels list dynamically
    for cat_item in parsed_cats:
        try:
            table_name = cat_item.get("table_name")
            cat_info = json.loads(cat_item.get("cat", "{}"))
            cat_name = cat_info.get("name", "Unknown")
            
            if table_name:
                chan_path = f"v2/channels/{table_name}.txt"
                chan_key = encrypt_xor_hex(chan_path)
                chan_url = f"https://cricyplayers.com/data/getData.php?key={chan_key}&hmac={fresh_hmac_encrypted}"
                
                raw_chan = make_request(chan_url)
                if raw_chan == "Not Found" or raw_chan == "":
                    print(f"-> Category '{cat_name}' ({table_name}) is currently offline on server.")
                    continue
                
                dec_chan = decode_v2(raw_chan)
                parsed_chan = json.loads(dec_chan)
                
                # Save to channels/{table_name}.json
                with open(os.path.join(channels_dir, f"{table_name}.json"), "w", encoding="utf-8") as f:
                    json.dump(parsed_chan, f, indent=2, ensure_ascii=False)
                print(f"-> Decrypted channels for '{cat_name}' successfully!")
        except Exception as inner_e:
            print(f"-> Failed processing category item '{cat_name}': {inner_e}")
except Exception as e:
    print("-> Failed categories processing:", e)

# 4. Fetch additional keys configured in app_control
for filename, key in keys.items():
    if not key:
        continue
    url = f"https://cricyplayers.com/data/getData.php?key={key}&hmac={fresh_hmac_encrypted}"
    print(f"Processing key {key} -> {filename}...")
    try:
        raw_res = make_request(url)
        dec_res = decode_v2(raw_res)
        parsed_res = json.loads(dec_res)
        
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
            json.dump(parsed_res, f, indent=2, ensure_ascii=False)
        print(f"-> Decrypted {filename} successfully!")
    except Exception as e:
        print(f"-> Failed {filename}: {e}")

print("\nDone! Decrypted files written to directory:", os.path.abspath(out_dir))
