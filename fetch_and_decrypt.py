import time
import urllib.request
import binascii
import base64
import json
import os
import sys
from Crypto.Cipher import AES

sys.stdout.reconfigure(encoding="utf-8")

# Load configuration
config_path = "config.json"
if not os.path.exists(config_path):
    print(f"Error: {config_path} not found.")
    sys.exit(1)

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

# Base Pages URL
github_user = os.environ.get("GITHUB_REPOSITORY_OWNER", "mdjamsad9")
github_repo = os.environ.get("GITHUB_REPOSITORY", "mdjamsad9/api").split("/")[-1]
base_pages_url = f"https://{github_user}.github.io/{github_repo}/public_decrypted/"

print(f"Base Pages URL: {base_pages_url}")

def encrypt_xor_hex(text):
    data = text.encode('utf-8')
    encrypted = bytes([b ^ xor_key_val for b in data])
    return binascii.hexlify(encrypted).decode('utf-8')

# cfgMaterial & decrypt_cfj1
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

# Target directories
out_dir = "public_decrypted"
os.makedirs(out_dir, exist_ok=True)

categories_dir = os.path.join(out_dir, "categories")
os.makedirs(categories_dir, exist_ok=True)

events_dir = os.path.join(out_dir, "events")
os.makedirs(events_dir, exist_ok=True)

channels_dir = os.path.join(out_dir, "channels")
os.makedirs(channels_dir, exist_ok=True)

# 1. Decrypt genzdev config
if genz_url:
    print("Processing URL 1 (GenzDev)...")
    try:
        raw_genz = make_request(genz_url)
        dec_genz = decrypt_cfj1(raw_genz)
        parsed_genz = json.loads(dec_genz)
        
        # Inject custom routing URLs for the app developer
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
parsed_cats = []
try:
    raw_cats = make_request(categories_url)
    dec_cats = decode_v2(raw_cats)
    parsed_cats = json.loads(dec_cats)
    
    with open(os.path.join(out_dir, "categories.json"), "w", encoding="utf-8") as f:
        json.dump(parsed_cats, f, indent=2, ensure_ascii=False)
    print("-> Decrypted categories.json successfully!")
except Exception as e:
    print("-> Failed categories processing:", e)

# 3. Iterate and fetch each category's channels list dynamically (if online)
if parsed_cats:
    for cat_item in parsed_cats:
        cat_name = "Unknown"
        try:
            table_name = cat_item.get("table_name")
            cat_id = cat_item.get("id")
            
            # Save parsed individual category file to categories/{id}.json
            clean_cat = {
                "id": cat_id,
                "table_name": table_name,
                "order_index": cat_item.get("order_index", 0)
            }
            cat_meta_raw = cat_item.get("cat")
            if cat_meta_raw:
                if isinstance(cat_meta_raw, str):
                    clean_cat["cat"] = json.loads(cat_meta_raw)
                else:
                    clean_cat["cat"] = cat_meta_raw
                cat_name = clean_cat["cat"].get("name", "Unknown")
            
            if cat_id is not None:
                with open(os.path.join(categories_dir, f"{cat_id}.json"), "w", encoding="utf-8") as cat_f:
                    json.dump(clean_cat, cat_f, indent=2, ensure_ascii=False)
            
            # Try to fetch sub-channels
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

# 4. Fetch additional keys configured in config.json
parsed_channels = []
parsed_events = []
for filename, key in keys.items():
    if not key:
        continue
    url = f"https://cricyplayers.com/data/getData.php?key={key}&hmac={fresh_hmac_encrypted}"
    print(f"Processing key {key} -> {filename}...")
    try:
        raw_res = make_request(url)
        dec_res = decode_v2(raw_res)
        parsed_res = json.loads(dec_res)
        
        # Save main feed file
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as f:
            json.dump(parsed_res, f, indent=2, ensure_ascii=False)
        print(f"-> Decrypted {filename} successfully!")
        
        if filename == "channels.json":
            parsed_channels = parsed_res
        elif filename == "events.json":
            parsed_events = parsed_res
    except Exception as e:
        print(f"-> Failed {filename}: {e}")

# 5. Extract every individual channel JSON file under channels/{id}.json
if parsed_channels:
    print(f"Extracting {len(parsed_channels)} individual channels from channels.json...")
    for channel_item in parsed_channels:
        channel_id = channel_item.get("id")
        if channel_id is not None:
            try:
                # Build combined clean JSON object
                clean_obj = {
                    "id": channel_id,
                    "order_index": channel_item.get("order_index", 0)
                }
                
                # Parse stringified channel metadata
                chan_meta_raw = channel_item.get("channel")
                if chan_meta_raw:
                    if isinstance(chan_meta_raw, str):
                        chan_meta = json.loads(chan_meta_raw)
                    else:
                        chan_meta = chan_meta_raw
                    clean_obj["name"] = chan_meta.get("name")
                    clean_obj["logo"] = chan_meta.get("logo")
                    clean_obj["visible"] = chan_meta.get("visible", True)
                    clean_obj["is_playlist"] = chan_meta.get("is_playlist", False)
                    clean_obj["links_metadata_path"] = chan_meta.get("links")
                
                # Parse stringified links array
                links_raw = channel_item.get("links")
                if links_raw:
                    if isinstance(links_raw, str):
                        clean_obj["links"] = json.loads(links_raw)
                    else:
                        clean_obj["links"] = links_raw
                else:
                    clean_obj["links"] = []
                
                # Save clean channel file to channels/{id}.json
                ch_out_path = os.path.join(channels_dir, f"{channel_id}.json")
                with open(ch_out_path, "w", encoding="utf-8") as ch_f:
                    json.dump(clean_obj, ch_f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"-> Failed extracting individual channel {channel_id}: {e}")
    print(f"-> Individual channel JSON files extracted to {channels_dir}/ successfully!")

# 6. Extract every individual event JSON file under events/{id}.json
if parsed_events:
    print(f"Extracting {len(parsed_events)} individual events from events.json...")
    for event_item in parsed_events:
        event_id = event_item.get("id")
        if event_id is not None:
            try:
                # Build combined clean JSON object
                clean_evt = {
                    "id": event_id,
                    "order_index": event_item.get("order_index", 0)
                }
                
                # Parse stringified event metadata
                evt_meta_raw = event_item.get("event")
                if evt_meta_raw:
                    if isinstance(evt_meta_raw, str):
                        evt_meta = json.loads(evt_meta_raw)
                    else:
                        evt_meta = evt_meta_raw
                    clean_evt["eventDetails"] = evt_meta.get("eventDetails", {})
                    clean_evt["teamA"] = evt_meta.get("teamA", {})
                    clean_evt["teamB"] = evt_meta.get("teamB", {})
                    clean_evt["visible"] = evt_meta.get("visible", True)
                    clean_evt["priority"] = evt_meta.get("priority", -1)
                    clean_evt["date"] = evt_meta.get("date")
                    clean_evt["time"] = evt_meta.get("time")
                    clean_evt["links_metadata_path"] = evt_meta.get("links")
                
                # Parse stringified links array
                links_raw = event_item.get("links")
                if links_raw:
                    if isinstance(links_raw, str):
                        clean_evt["links"] = json.loads(links_raw)
                    else:
                        clean_evt["links"] = links_raw
                else:
                    clean_evt["links"] = []
                
                # Save clean event file to events/{id}.json
                evt_out_path = os.path.join(events_dir, f"{event_id}.json")
                with open(evt_out_path, "w", encoding="utf-8") as evt_f:
                    json.dump(clean_evt, evt_f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"-> Failed extracting individual event {event_id}: {e}")
    print(f"-> Individual event JSON files extracted to {events_dir}/ successfully!")

# 7. Generate Dynamic api_spec.json for developers
api_spec = {
    "api_name": "Cricfy TV Decrypted API",
    "base_url": base_pages_url.rstrip("/"),
    "description": "This is a clean, decrypted static JSON API database for CricFy TV, generated automatically every 5 minutes via GitHub Actions.",
    "endpoints": {
        "startup_config": {
            "path": "/genzdev_config.json",
            "description": "Global app configuration, popups, and API redirection URLs.",
            "fields": {
                "schema": "Schema version number",
                "Mode": "Configuration mode (e.g. GenZ)",
                "api_url": "Decrypted pages base URL for fallback operations",
                "api2": "Decrypted pages base URL for fallback operations",
                "categories_api": "Static categories API URL",
                "events_api": "Static events API URL",
                "channels_api_base": "Base directory URL for dynamic category channels",
                "message": "Global announcement/notice text displayed in the app",
                "latest_version_code": "Latest Android app version code",
                "update_url": "App update or landing page URL"
            }
        },
        "categories_menu": {
            "path": "/categories.json",
            "description": "Main category menu list. Contains the category names, logos, types, and table_names.",
            "fields": {
                "id": "Unique category identifier",
                "cat": "Raw or parsed JSON metadata containing name, logo, type, and source endpoint",
                "table_name": "Dynamic category table name (used to fetch the category's channel list from /channels/{table_name}.json)",
                "order_index": "Sort priority order"
            },
            "usage_flow": "Step 1: Fetch categories.json to render the main menu. For each item: if 'table_name' is present, fetch the category channels list from 'base_url + /channels/{table_name}.json', or load individual parsed category metadata from '/categories/{id}.json'."
        },
        "sports_tv_channels": {
            "path": "/channels.json",
            "description": "Global list of standard TV channels with raw stringified and nested attributes.",
            "fields": {
                "id": "Unique TV channel identifier",
                "channel": "Stringified TV channel details (name, logo, visible, links_path)",
                "links": "Stringified JSON array containing playback servers and links",
                "order_index": "Sort priority order"
            },
            "usage_flow": "To play a TV channel: Fetch its clean, fully parsed direct streaming links using '/channels/{id}.json' (e.g. '/channels/2.json')."
        },
        "live_events": {
            "path": "/events.json",
            "description": "List of active live and upcoming sports matches and events.",
            "fields": {
                "id": "Unique event identifier (e.g. 35)",
                "event": "Stringified event details including eventDetails, teamA, teamB details, visible, date, and time",
                "links": "Stringified JSON array containing active playback streams and DRM keys for the event"
            },
            "usage_flow": "To play a live event: Fetch its clean, fully parsed direct streaming links and match info using '/events/{id}.json' (e.g. '/events/35.json')."
        },
        "tournament_logos": {
            "path": "/event_cats.json",
            "description": "Filter categories/tournament logo mappings for live events (e.g. Boxing, Cricket, Football).",
            "fields": {
                "TournamentName": "Tournament category name associated with a logo URL string"
            }
        }
    },
    "sub_directories": {
        "individual_category_details": {
            "path_pattern": "/categories/{id}.json",
            "description": "Contains clean, parsed metadata for any specific category.",
            "fields": {
                "id": "Unique category identifier",
                "table_name": "Category table name",
                "order_index": "Category display sorting order index",
                "cat": "Object containing name, logo, visible, type, and source API endpoint"
            }
        },
        "category_channels": {
            "path_pattern": "/channels/{table_name}.json",
            "description": "Contains list of channels inside a specific custom category (e.g. `/channels/SW5kaWExNzY5NjIyNDI1NzM5.json`).",
            "fields": {
                "id": "Channel identifier",
                "name": "Channel display name",
                "logo": "Channel logo thumbnail URL",
                "links": "Array of stream objects containing name, playback link, and DRM decryption keys"
            }
        },
        "decrypted_channel_links": {
            "path_pattern": "/channels/{id}.json",
            "description": "Contains clean decrypted playback streams, name, logo, and DRM decryption keys for any specific TV Channel ID.",
            "fields": {
                "id": "Channel identifier",
                "name": "Channel display name",
                "logo": "Channel logo URL",
                "visible": "Visibility status in application",
                "is_playlist": "Boolean flag if channel is an M3U playlist",
                "links": "Array of stream objects containing name, link, scheme, and api (DRM Key)",
                "order_index": "Sort priority order"
            }
        },
        "decrypted_event_links": {
            "path_pattern": "/events/{id}.json",
            "description": "Contains clean decrypted playback streams, tournament details, teams information, and DRM keys for any specific Live Event ID.",
            "fields": {
                "id": "Event identifier",
                "eventDetails": "Object containing category, eventName, and eventLogo",
                "teamA": "Object containing name and logo for Team A",
                "teamB": "Object containing name and logo for Team B",
                "visible": "Visibility status",
                "priority": "Sort priority",
                "date": "Event scheduled date",
                "time": "Event scheduled start time",
                "links": "Array of stream objects containing server name, playback link, scheme, and api (DRM Key)"
            },
            "player_decryption_handling": "If 'api' is present in stream links (e.g. 'daa8ea92...:4042e04...'), it represents a DRM protected stream. Split the 'api' string by ':' to get the Key ID (left) and Key (right), and pass them to your player's DRM ClearKey configuration."
        }
    }
}
try:
    with open(os.path.join(out_dir, "api_spec.json"), "w", encoding="utf-8") as f:
        json.dump(api_spec, f, indent=2, ensure_ascii=False)
    print("-> Generated api_spec.json successfully!")
except Exception as e:
    print("-> Failed to generate api_spec.json:", e)

print("\nDone! Decrypted files written to directory:", os.path.abspath(out_dir))
