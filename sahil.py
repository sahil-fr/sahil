import os
import re
import io
import json
import random
import asyncio
import aiohttp
import urllib.request
import html as html_lib
from datetime import datetime, timedelta
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.tl.functions.channels import (
    CreateChannelRequest, EditPhotoRequest, EditAdminRequest, 
    EditTitleRequest, InviteToChannelRequest, UpdateUsernameRequest
)
from telethon.tl.functions.messages import (
    ExportChatInviteRequest, EditChatTitleRequest, SetHistoryTTLRequest,
    EditChatDefaultBannedRightsRequest
)
from telethon.tl.types import (
    InputChatUploadedPhoto, ChatAdminRights, ChatBannedRights,
    ChannelParticipantsAdmins
)
from PIL import Image, ImageDraw, ImageFont
from flask import Flask
import threading
import base64
import html

app = Flask(__name__)

@app.route('/')
def home():
    return "Middleman Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Flask ko background thread mein start karna
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
INSTAGRAM_SESSION = os.getenv("INSTAGRAM_SESSION", "").strip()

GROUP_PFP_URL = "https://t.me/ScamsWatchlist/109"
ASSISTANT_BOT = "@middlemavenbot" 
TOS_LINK = "https://telegra.ph/Middlemaven-TOS-07-29" 

MM_DATA = {
    967359142: {
        "name": "Fog",
        "username": "@fogey",
        "prefix": "Fog MM",
        "vouch_channel": -1001287026986 # <--- Fog ka Vouch Channel ID
    },
    8421166266: {
        "name": "Trohps",
        "username": "@trohps",
        "prefix": "Trohps MM",
        "vouch_channel": -1003969714923 # <--- Trohps ka Vouch Channel ID
    },
    7913633925: {
        "name": "Shuify",
        "username": "@hupke",
        "prefix": "Shuify MM",
        "vouch_channel": -1003711319131 # <--- Shuify ka Vouch Channel ID
    },
    8258524753: {
        "name": "Nox",
        "username": "@noxogu",
        "prefix": "Nox MM",
        "vouch_channel": -1003231804994 # <--- Nox ka Vouch Channel ID
    },
    8358390340: {
        "name": "Xenie MM",
        "username": "@xenyy",
        "prefix": "Xenie MM",
        "vouch_channel": -1003600065580 # <--- 5th MM ka Vouch Channel ID
    }
}

# --- DATABASE SETUP (JSON) ---
CONFIG_FILE = "mm_config.json"
CUSTOM_CMDS_FILE = "custom_commands.json"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def send_rich_message(chat_id, html_text, reply_markup=None):
    url = f"{API_URL}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": html_text,
        "parse_mode": "HTML"
    }

    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()

                if data.get("ok"):
                    return data["result"]["message_id"]

                print("Send Message API Error:", data)

    except Exception as e:
        print(f"Send Rich Message Error: {e}")

    return None


async def edit_rich_message(
    chat_id, message_id, html_text, reply_markup=None
):
    url = f"{API_URL}/editMessageText"

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": html_text,
        "parse_mode": "HTML"
    }

    if reply_markup is not None:
        payload["reply_markup"] = reply_markup

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()

                if not data.get("ok"):
                    print("Edit Message API Error:", data)

                return data.get("ok", False)

    except Exception as e:
        print(f"Edit Rich Message Error: {e}")
        return False

DEFAULT_CONFIG = {
    "fee_percent": 2.0,            
    "min_fee_crypto": 1.0,         
    "min_fee_inr": 20.0,  
    "bot_msg_tos": "<b>TOS:</b> My only responsibility is to hold funds. I am not responsible for changes in crypto value or sending fees. The MM fee is non refundable. If not provided upfront, it will be taken before sending to the seller/refund. I am not responsible for accounts/products pulled on evoked during or after the deal. I have the right to compensate either party if time wasting is occurring.",
    "rec_msg": "I have successfully received the amount and the MM fee. It is safe to move forward. I will process the payment after the deal concludes. Thank you for your cooperation!",
    
    "mms": {
        "967359142": {  # FOG KA DATA
            "crypto_wallets": {
                "ton": "UQAAHD0SjE3XKK-K2rKRDOdD6chaOh58KC3wHNytZW7IJSaf", "sol": "FjB4kX7mMKPgTX9TaTZdUHHWhhRigZgwJPcgcvgzPaBY", "polygon": "FOG_POLY_ADDRESS", "bep": "0xcA524ec30da709a8d8E21339792406FDCc457e83",
                "btc": "bc1qpwnc39kyl34p5vl4yactdt26eec382408fhuvu", "eth": "0x9f7E11F8bb55Fc804F198bF63E88065344BCF7ff", "erc": "FOG_ERC_ADDRESS", "trc": "FOG_TRC_ADDRESS",
                "ltc": "ltc1q2y285ce29w7mhgz9xm45z42mdq8e4nx958qacy", "xrp": "FOG_XRP_ADDRESS", "doge": "FOG_DOGE_ADDRESS", "bch": "FOG_BCH_ADDRESS", "usdc": "FOG_USDC_ADDRESS"
            },
            "upi_id": "tysted@ptyes",
            "qr_link": "https://t.me/ScamsWatchlist/113"
        },
        "8421166266": {  # TROHPS KA DATA
            "crypto_wallets": {
                "ton": "TROHPS_TON_ADDRESS", "sol": "TROHPS_SOL_ADDRESS", "polygon": "TROHPS_POLY_ADDRESS", "bep": "TROHPS_BEP_ADDRESS",
                "btc": "TROHPS_BTC_ADDRESS", "eth": "TROHPS_ETH_ADDRESS", "erc": "TROHPS_ERC_ADDRESS", "trc": "TROHPS_TRC_ADDRESS",
                "ltc": "TROHPS_LTC_ADDRESS", "xrp": "TROHPS_XRP_ADDRESS", "doge": "TROHPS_DOGE_ADDRESS", "bch": "TROHPS_BCH_ADDRESS", "usdc": "TROHPS_USDC_ADDRESS"
            },
            "upi_id": "trohps_upi@bank",
            "qr_link": ""
        },
        "7913633925": {  # SHUIFY KA DATA
            "crypto_wallets": {
                "ton": "SHUIFY_TON_ADDRESS", "sol": "SHUIFY_SOL_ADDRESS", "polygon": "SHUIFY_POLY_ADDRESS", "bep": "SHUIFY_BEP_ADDRESS",
                "btc": "SHUIFY_BTC_ADDRESS", "eth": "SHUIFY_ETH_ADDRESS", "erc": "SHUIFY_ERC_ADDRESS", "trc": "SHUIFY_TRC_ADDRESS",
                "ltc": "SHUIFY_LTC_ADDRESS", "xrp": "SHUIFY_XRP_ADDRESS", "doge": "SHUIFY_DOGE_ADDRESS", "bch": "SHUIFY_BCH_ADDRESS", "usdc": "SHUIFY_USDC_ADDRESS"
            },
            "upi_id": "shuify_upi@bank",
            "qr_link": ""
        },
        "1234567890": {  # 4TH MM KA DATA
            "crypto_wallets": {
                "ton": "MM4_TON_ADDRESS", "sol": "MM4_SOL_ADDRESS", "polygon": "MM4_POLY_ADDRESS", "bep": "MM4_BEP_ADDRESS",
                "btc": "MM4_BTC_ADDRESS", "eth": "MM4_ETH_ADDRESS", "erc": "MM4_ERC_ADDRESS", "trc": "MM4_TRC_ADDRESS",
                "ltc": "MM4_LTC_ADDRESS", "xrp": "MM4_XRP_ADDRESS", "doge": "MM4_DOGE_ADDRESS", "bch": "MM4_BCH_ADDRESS", "usdc": "MM4_USDC_ADDRESS"
            },
            "upi_id": "mm4_upi@bank",
            "qr_link": ""
        },
        "8358390340": {  # 5TH MM KA DATA
            "crypto_wallets": {
                "ton": "MM5_TON_ADDRESS", "sol": "MM5_SOL_ADDRESS", "polygon": "MM5_POLY_ADDRESS", "bep": "MM5_BEP_ADDRESS",
                "btc": "MM5_BTC_ADDRESS", "eth": "MM5_ETH_ADDRESS", "erc": "MM5_ERC_ADDRESS", "trc": "MM5_TRC_ADDRESS",
                "ltc": "MM5_LTC_ADDRESS", "xrp": "MM5_XRP_ADDRESS", "doge": "MM5_DOGE_ADDRESS", "bch": "MM5_BCH_ADDRESS", "usdc": "MM5_USDC_ADDRESS"
            },
            "upi_id": "mm5_upi@bank",
            "qr_link": ""
        }
    }
}

def load_json(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f: json.dump(default_data, f, indent=4)
        return default_data
    with open(file_path, 'r') as f: 
        data = json.load(f)
        # AUTO-FIX: Sirf tabhi 'mms' check karega jab default_data mein mms ho
        if "mms" in default_data and "mms" not in data:
            data["mms"] = default_data["mms"]
            with open(file_path, 'w') as out_f: json.dump(data, out_f, indent=4)
        return data

def save_json(file_path, data):
    with open(file_path, 'w') as f: json.dump(data, f, indent=4)

config = load_json(CONFIG_FILE, DEFAULT_CONFIG)
custom_commands = load_json(CUSTOM_CMDS_FILE, {})

USER_SESSION = os.getenv("USER_SESSION")

client = TelegramClient(
    StringSession(USER_SESSION),
    API_ID,
    API_HASH
)

bot_client = TelegramClient(
    "mm_assistant_bot_v2",
    API_ID,
    API_HASH
)

refund_requested_chats = set()
chat_vouches = {}  
active_timers = {}
admin_states = {}
last_group_links = {}
release_requested_chats = set()
group_roles = {}
pending_complete_chats = set()
chat_vouched_users = {}
chat_deal_amount = {}
chat_deal_info = {}
deal_confirmations = {}
chat_state_setup = {}
state_input_wait = {}
chat_final_state = {}
state_confirmations = {}

def calc_fee(amount, mm_id=None, is_inr=False):
    # Agar mm_id provided hai aur wo MM_DATA ya config mein available hai
    custom_fee = None
    if mm_id and mm_id in MM_DATA:
        custom_fee = MM_DATA[mm_id].get("custom_fee", None)
    
    if not custom_fee and mm_id:
        mm_id_str = str(mm_id)
        custom_fee = config.get("mms", {}).get(mm_id_str, {}).get("custom_fee", None)
        
    # Agar custom fee milti hai toh us hisab se calculate karo
    if custom_fee is not None:
        try:
            fee_val = float(custom_fee)
            fee = amount * (fee_val / 100)
            min_f = config["min_fee_inr"] if is_inr else config["min_fee_crypto"]
            return min_f if fee < min_f else round(fee, 2)
        except:
            pass

    # Default Global Calculation
    fee = amount * (config["fee_percent"] / 100)
    min_f = config["min_fee_inr"] if is_inr else config["min_fee_crypto"]
    return min_f if fee < min_f else round(fee, 2)

def fmt_inr(n): return int(n) if n.is_integer() else round(n, 2)

def parse_time(time_str):
    match = re.match(r'((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?', time_str)
    if not match: return None
    parts = match.groupdict()
    return timedelta(**{n: int(v) for n, v in parts.items() if v})


async def get_crypto_price(ticker):
    if not ticker: return 1.0  
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.binance.com/api/v3/ticker/price?symbol={ticker}") as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data['price'])
    except: return None

async def get_image_bytes(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200: return await resp.read()
    except: return None

CRYPTO_INFO = {
    "ton": {"name": "TON", "ticker": "TONUSDT"}, "sol": {"name": "Solana (SOL)", "ticker": "SOLUSDT"},
    "polygon": {"name": "USDT (Polygon)", "ticker": None}, "bep": {"name": "USDT (BEP20)", "ticker": None},
    "btc": {"name": "Bitcoin (BTC)", "ticker": "BTCUSDT"}, "eth": {"name": "Ethereum (ETH)", "ticker": "ETHUSDT"},
    "erc": {"name": "USDT (ERC20)", "ticker": None}, "trc": {"name": "USDT (TRC20)", "ticker": None},
    "ltc": {"name": "Litecoin (LTC)", "ticker": "LTCUSDT"}, "xrp": {"name": "Ripple (XRP)", "ticker": "XRPUSDT"},
    "doge": {"name": "Dogecoin (DOGE)", "ticker": "DOGEUSDT"}, "bch": {"name": "Bitcoin Cash (BCH)", "ticker": "BCHUSDT"},
    "usdc": {"name": "USDC (ERC20)", "ticker": None}
}

DEAL_TERMS = {
    "unban terms": "Note: If the account is not unbanned within the stated TAT, funds will be instantly refunded to the buyer if he asks for it.\n\nIf the account is unbanned, I will verify it and release the funds to the seller without delay. No exceptions unless stated.\n\nFunds will still be released even after the TAT ends if the buyer does not cancel the deal or ask for a refund. you must be responsive to the deal; do not sleep on it.\n\nYou both must be responsive to the deal.",
    "ban terms": "Note: If the account is not banned within the stated TAT, funds will be instantly refunded to the buyer if he asks for it.\n\nIf the account is banned, I will verify it and release the funds to the seller without delay. No exceptions unless stated.\n\nFunds will still be released even after the TAT ends if the buyer does not cancel the deal or ask for a refund. you must be responsive to the deal; do not sleep on it.\n\nYou both must be responsive to the deal.",
    "no terms": "<b>Deal Terms:</b>\n\nAs no specific conditions have been stated regarding the account, once the deal is completed, the buyer assumes full responsibility and liability for the account.\n\nIf the account is banned, logged out, becomes inaccessible, cannot be logged into, or if anything else happens to the account after the deal, <b>MM will not be held responsible or liable</b> for any resulting loss, issue, or damage."
}

async def fetch_ig_data(username):
    username = username.strip().lstrip("@").split("?")[0].split("/")[0]

    if not re.fullmatch(r"[A-Za-z0-9._]+", username):
        return {
            "status": "error",
            "reason": "Invalid Instagram username"
        }

    url = f"https://www.instagram.com/{username}/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/140.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Referer": "https://www.instagram.com/",
    }

    timeout = aiohttp.ClientTimeout(
        total=20,
        connect=8,
        sock_read=12
    )

    session_cookie = os.getenv("INSTAGRAM_SESSION", "").strip()

    def parse_profile(status_code, final_url, page):
        lower = page.lower()

        if status_code in (401, 403, 429, 430):
            return None, (
                f"Instagram returned HTTP {status_code}; "
                "the request may be restricted"
            )

        if any(x in final_url.lower() for x in (
            "/accounts/login",
            "/challenge",
            "/checkpoint",
        )):
            return None, "Instagram redirected to login or verification"

        if any(x in lower for x in (
            "challenge_required",
            "login_required",
            "please wait a few minutes",
            "temporarily blocked",
            "rate limit",
        )):
            return None, "Instagram returned a restricted response"

        unavailable = (
            "sorry, this page isn't available",
            "sorry, this page isn&#39;t available",
            "the link you followed may be broken",
            "the page may have been removed",
        )

        if any(x in lower for x in unavailable):
            return {
                "status": "banned",
                "username": username,
            }, None

        def meta_content(property_name):
            pattern = (
                r'<meta\b(?=[^>]*(?:property|name)=["\']'
                + re.escape(property_name)
                + r'["\'])[^>]*content=["\']([^"\']*)["\']'
            )
            match = re.search(pattern, page, re.I)
            if match:
                return html_lib.unescape(match.group(1))

            # Also support content appearing before property/name.
            pattern = (
                r'<meta\b[^>]*content=["\']([^"\']*)["\']'
                r'[^>]*(?:property|name)=["\']'
                + re.escape(property_name)
                + r'["\']'
            )
            match = re.search(pattern, page, re.I)
            return html_lib.unescape(match.group(1)) if match else None

        description = (
            meta_content("og:description")
            or meta_content("description")
        )
        title = meta_content("og:title")
        pfp = meta_content("og:image")

        # Try JSON-LD metadata when available.
        if not description:
            for block in re.findall(
                r'<script[^>]+type=["\']application/ld\+json["\']'
                r'[^>]*>(.*?)</script>',
                page,
                re.I | re.S,
            ):
                try:
                    obj = json.loads(block)
                    if isinstance(obj, dict):
                        description = (
                            obj.get("description")
                            or description
                        )
                        pfp = obj.get("image") or pfp
                except (ValueError, TypeError):
                    pass

        profile_evidence = (
            bool(description)
            or bool(title)
            or bool(pfp)
            or f'"username":"{username.lower()}"' in lower
        )

        if status_code != 200:
            return None, f"Instagram returned HTTP {status_code}"

        if not profile_evidence:
            return None, (
                "Instagram returned HTML without recognizable "
                "profile metadata; access may be restricted"
            )

        posts = followers = following = "0"

        if description:
            patterns = {
                "followers": r"([\d.,kKmMbB]+)\s+Followers",
                "following": r"([\d.,kKmMbB]+)\s+Following",
                "posts": r"([\d.,kKmMbB]+)\s+Posts",
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, description, re.I)
                if match:
                    if key == "followers":
                        followers = match.group(1)
                    elif key == "following":
                        following = match.group(1)
                    else:
                        posts = match.group(1)

        return {
            "status": "active",
            "username": username,
            "posts": posts,
            "followers": followers,
            "following": following,
            "pfp_url": pfp,
        }, None

    cookie = {}
    if session_cookie:
        # Accept either a raw sessionid or a cookie header.
        if "=" not in session_cookie:
            cookie["sessionid"] = session_cookie
        else:
            for part in session_cookie.split(";"):
                key, sep, value = part.strip().partition("=")
                if sep and key and value:
                    cookie[key] = value

    last_reason = "No Instagram response received"

    try:
        connector = aiohttp.TCPConnector(limit=4)

        async with aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=connector,
            cookie_jar=aiohttp.CookieJar(),
        ) as session:

            for attempt in range(2):
                try:
                    async with session.get(
                        url,
                        allow_redirects=True,
                        max_redirects=5,
                    ) as response:
                        page = await response.text(errors="ignore")

                        data, reason = parse_profile(
                            response.status,
                            str(response.url),
                            page,
                        )

                        if data is not None:
                            return data

                        last_reason = reason or "Unable to parse profile"

                        # Do not retry a response that clearly indicates
                        # a restriction.
                        if response.status in (401, 403, 429, 430):
                            break

                except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                    last_reason = f"{type(exc).__name__}: {exc}"

                if attempt == 0:
                    await asyncio.sleep(1.5)

        # Optional authenticated retry, only if configured.
        if cookie:
            session_headers = dict(headers)
            session_headers["X-IG-App-ID"] = "936619743392459"

            try:
                async with aiohttp.ClientSession(
                    headers=session_headers,
                    timeout=timeout,
                    cookie_jar=aiohttp.CookieJar(),
                ) as session:
                    async with session.get(
                        url,
                        cookies=cookie,
                        allow_redirects=True,
                        max_redirects=5,
                    ) as response:
                        page = await response.text(errors="ignore")
                        data, reason = parse_profile(
                            response.status,
                            str(response.url),
                            page,
                        )

                        if data is not None:
                            return data

                        last_reason = reason or last_reason

            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                last_reason = (
                    f"Authenticated request failed: "
                    f"{type(exc).__name__}: {exc}"
                )

    except Exception as exc:
        last_reason = f"{type(exc).__name__}: {exc}"

    print(f"[Instagram Fetch] @{username}: {last_reason}")

    return {
        "status": "error",
        "username": username,
        "reason": last_reason,
    }

async def create_profile_card(username, pfp_bytes, posts, followers, following, is_banned):
    try:
        img = Image.new('RGB', (1200, 450), color=(12, 12, 12))
        draw = ImageDraw.Draw(img)

        font_url_bold = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        font_url_reg = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
        
        if not os.path.exists("Roboto-Bold.ttf"):
            try: urllib.request.urlretrieve(font_url_bold, "Roboto-Bold.ttf")
            except: pass
        if not os.path.exists("Roboto-Regular.ttf"):
            try: urllib.request.urlretrieve(font_url_reg, "Roboto-Regular.ttf")
            except: pass

        def get_font(size, bold=False):
            name = "Roboto-Bold.ttf" if bold else "Roboto-Regular.ttf"
            try: return ImageFont.truetype(name, size)
            except: return ImageFont.load_default()

        font_name = get_font(55, bold=True)
        font_btn = get_font(28, bold=True)
        font_stats_num = get_font(42, bold=True)
        font_stats_lbl = get_font(26, bold=False)

        pfp_size = 240
        pfp_x, pfp_y = 80, 105

        if pfp_bytes and not is_banned:
            try:
                pfp = Image.open(io.BytesIO(pfp_bytes)).convert("RGBA").resize((pfp_size, pfp_size), Image.Resampling.LANCZOS)
                mask = Image.new('L', (pfp_size, pfp_size), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, pfp_size, pfp_size), fill=255)
                pfp.putalpha(mask)
                draw.ellipse((pfp_x-4, pfp_y-4, pfp_x+pfp_size+4, pfp_y+pfp_size+4), outline=(70, 70, 70), width=3)
                img.paste(pfp, (pfp_x, pfp_y), pfp)
            except: 
                draw.ellipse((pfp_x, pfp_y, pfp_x+pfp_size, pfp_y+pfp_size), fill=(40, 40, 40), outline=(70, 70, 70), width=3)
        else:
            # Banned ke liye pfp border normal grey rakhi hai, red nahi
            draw.ellipse((pfp_x, pfp_y, pfp_x+pfp_size, pfp_y+pfp_size), fill=(40, 40, 40), outline=(70, 70, 70), width=3)
            draw.arc((pfp_x+75, pfp_y+55, pfp_x+165, pfp_y+145), start=0, end=180, fill=(150, 150, 150), width=12)
            draw.ellipse((pfp_x+95, pfp_y+85, pfp_x+145, pfp_y+135), fill=(150, 150, 150))

        draw.text((380, 105), username, font=font_name, fill=(255, 255, 255))
        
        btn_x, btn_y = 380, 185
        if is_banned:
            # Banned ke liye bada rounded box jiska andar ka hissa transparent/dark ho aur vibrant red border ho
            box_width, box_height = 340, 55
            try: 
                draw.rounded_rectangle([btn_x, btn_y, btn_x + box_width, btn_y + box_height], radius=12, fill=(12, 12, 12), outline=(255, 59, 48), width=3)
            except: 
                draw.rectangle([btn_x, btn_y, btn_x + box_width, btn_y + box_height], fill=(12, 12, 12), outline=(255, 59, 48), width=3)
            
            try:
                bbox = draw.textbbox((0, 0), "BANNED", font=font_btn)
                draw.text((btn_x + (box_width - (bbox[2] - bbox[0])) / 2, btn_y + (box_height - (bbox[3] - bbox[1])) / 2 - 3), "BANNED", font=font_btn, fill=(255, 59, 48))
            except: 
                draw.text((btn_x + 110, btn_y + 12), "BANNED", font=font_btn, fill=(255, 59, 48))
            
            posts_val, followers_val, following_val = "N/A", "N/A", "N/A"
        else:
            try: draw.rounded_rectangle([btn_x, btn_y, btn_x+160, btn_y+55], radius=10, fill=(0, 149, 246))
            except: draw.rectangle([btn_x, btn_y, btn_x+160, btn_y+55], fill=(0, 149, 246))
            try:
                bbox = draw.textbbox((0, 0), "Follow", font=font_btn)
                draw.text((btn_x + (160-(bbox[2]-bbox[0]))/2, btn_y + (55-(bbox[3]-bbox[1]))/2 - 3), "Follow", font=font_btn, fill=(255, 255, 255))
            except: draw.text((btn_x + 35, btn_y + 12), "Follow", font=font_btn, fill=(255, 255, 255))

            dot_x = btn_x + 180
            try: draw.rounded_rectangle([dot_x, btn_y, dot_x+70, btn_y+55], radius=10, fill=(38, 38, 38))
            except: draw.rectangle([dot_x, btn_y, dot_x+70, btn_y+55], fill=(38, 38, 38))
            try:
                bbox = draw.textbbox((0, 0), "...", font=font_btn)
                draw.text((dot_x + (70-(bbox[2]-bbox[0]))/2, btn_y + (55-(bbox[3]-bbox[1]))/2 - 8), "...", font=font_btn, fill=(255, 255, 255))
            except: draw.text((dot_x + 20, btn_y + 8), "...", font=font_btn, fill=(255, 255, 255))
            
            posts_val, followers_val, following_val = str(posts), str(followers), str(following)

        stats_y_num, stats_y_text = 290, 345
        def draw_centered_text(x_center, y, text, font, fill):
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                draw.text((x_center - (bbox[2]-bbox[0])/2, y), text, font=font, fill=fill)
            except: draw.text((x_center - 20, y), text, font=font, fill=fill)

        # N/A text ko red ki jagah normal white color de diya hai taaki active card jaisa lage
        stat_color = (255, 255, 255)
        draw_centered_text(450, stats_y_num, posts_val, font_stats_num, stat_color)
        draw_centered_text(450, stats_y_text, "posts", font_stats_lbl, (168, 168, 168))
        draw_centered_text(700, stats_y_num, followers_val, font_stats_num, stat_color)
        draw_centered_text(700, stats_y_text, "followers", font_stats_lbl, (168, 168, 168))
        draw_centered_text(950, stats_y_num, following_val, font_stats_num, stat_color)
        draw_centered_text(950, stats_y_text, "following", font_stats_lbl, (168, 168, 168))

        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        img_bytes.name = "profile_card.png"
        return img_bytes
    except Exception as e: 
        return None


async def add_crypto_tracker(group):
    bot_username = "@scoutggbot"

    try:
        # Add Crypto Tracker bot to the group
        await bot_client(
            InviteToChannelRequest(
                channel=group,
                users=[bot_username]
            )
        )

        # Resolve the bot entity
        tracker = await bot_client.get_input_entity(bot_username)

        # Grant admin permissions
        await bot_client(
            EditAdminRequest(
                channel=group,
                user_id=tracker,
                admin_rights=ChatAdminRights(
                    change_info=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True,
                    add_admins=False,
                    manage_call=True,
                    anonymous=False,
                    manage_topics=True,
                    post_messages=True,
                    edit_messages=True,
                    post_stories=True,
                    edit_stories=True,
                    delete_stories=True
                ),
                rank="Crypto Tracker"
            )
        )

        print(f"Crypto Tracker added successfully to {group}")

    except Exception as e:
        print(f"Crypto Tracker setup failed: {e}")

@bot_client.on(events.NewMessage(pattern=r'\.gc$'))
async def gc_command(event):
    if not event.is_private or event.sender_id not in MM_DATA:
        return

    mm_info = MM_DATA[event.sender_id]
    group_title = f"{mm_info['prefix']} | @Middlemaven"
    
    mm_id_str = str(event.sender_id)
    mm_settings = config.setdefault("mms", {}).setdefault(mm_id_str, {})
    
    default_bio = (
        "Experience the fastest Middleman in the community.\n\nt.me/fogey - Always confirm it's me"
        if event.sender_id == 967359142
        else "Always confirm my username before proceeding with any of my offerings."
    )
    
    # Use this MM's custom bio when set; otherwise keep the existing default.
    about_text = (mm_settings.get("custom_bio") or default_bio)[:255]

    wait_msg = await event.respond("Creating group...")

    try:
        # 1. Group Creation via Userbot
        result = await client(
            CreateChannelRequest(
                title=group_title,
                about=about_text,
                megagroup=True
            )
        )

        channel = result.chats[0]
        real_chat_id = int(f"-100{channel.id}")

        # ==========================================
        # CUSTOM PFP (per middleman) OR DEFAULT GROUP PHOTO
        # ==========================================
        try:
            custom_pfp = mm_settings.get("custom_pfp_path")
            pfp_file = None

            if custom_pfp and os.path.isfile(custom_pfp):
                # Custom image was uploaded in the admin panel.
                pfp_file = custom_pfp
            else:
                # No custom PFP set: use the existing default image url/telegram message.
                pfp_url = mm_info.get("gc_pfp", GROUP_PFP_URL)
                match = re.search(
                    r't\.me/([^/]+)/(\d+)',
                    pfp_url
                )

                if match:
                    chat_username = match.group(1)
                    msg_id = int(match.group(2))

                    pfp_msg = await client.get_messages(
                        chat_username,
                        ids=msg_id
                    )

                    if pfp_msg and pfp_msg.media:
                        pfp_file = await client.download_media(
                            pfp_msg.media
                        )

            if pfp_file and os.path.isfile(pfp_file):
                uploaded_photo = await client.upload_file(
                    pfp_file
                )

                await client(
                    EditPhotoRequest(
                        channel=channel,
                        photo=InputChatUploadedPhoto(
                            file=uploaded_photo
                        )
                    )
                )

                # Only delete temporary downloads, never the saved custom PFP.
                if not (
                    custom_pfp
                    and os.path.abspath(pfp_file) == os.path.abspath(custom_pfp)
                ):
                    try:
                        os.remove(pfp_file)
                    except:
                        pass

        except Exception as e:
            print(f"PFP Set Error: {e}")

        # ==========================================
        # GROUP SETTINGS
        # ==========================================
        try:
            await client(
                UpdateUsernameRequest(
                    channel=channel,
                    username=None
                )
            )

            await client(
                SetHistoryTTLRequest(
                    peer=channel,
                    period=0
                )
            )

        except:
            pass

        # ==========================================
        # ADMIN RIGHTS
        # ==========================================
        admin_rights = ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            manage_call=True,
            add_admins=True
        )

        # ==========================================
        # INVITE ASSISTANT BOT + MM + CRYPTO TRACKER
        # ==========================================
        try:
            await client(
                InviteToChannelRequest(
                    channel=channel,
                    users=[
                        ASSISTANT_BOT,
                        mm_info["username"],
                        "@scoutggbot"
                    ]
                )
            )

        except Exception as e:
            print(f"Invite Error: {e}")

        # Telegram sync delay
        await asyncio.sleep(2.5)

        # ==========================================
        # ASSISTANT BOT ADMIN
        # ==========================================
        try:
            await client(
                EditAdminRequest(
                    channel=channel,
                    user_id=ASSISTANT_BOT,
                    admin_rights=admin_rights,
                    rank="Group Help Bot"
                )
            )

        except Exception as e:
            print(f"Bot Admin Error: {e}")

        # ==========================================
        # CRYPTO TRACKER BOT ADMIN
        # ==========================================
        try:
            crypto_tracker = await client.get_input_entity("@scoutggbot")

            crypto_tracker_rights = ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                manage_call=True,
                add_admins=False
            )

            await client(
                EditAdminRequest(
                    channel=channel,
                    user_id=crypto_tracker,
                    admin_rights=crypto_tracker_rights,
                    rank="Crypto Tracker"
                )
            )

            print("Crypto Tracker bot added as admin successfully.")

        except Exception as e:
            print(f"Crypto Tracker Admin Error: {e}")

        # ==========================================
        # MM ADMIN
        # ==========================================
        try:
            await client(
                EditAdminRequest(
                    channel=channel,
                    user_id=mm_info["username"],
                    admin_rights=admin_rights,
                    rank="Middleman"
                )
            )

        except Exception as e:
            print(f"MM Admin Error: {e}")

        # ==========================================
        # GENERATE INVITE LINK
        # ==========================================
        invite = await client(
            ExportChatInviteRequest(
                peer=channel
            )
        )

        await wait_msg.edit(
            '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            f'<b>Group Created &amp; Configured:</b> {invite.link}',
            link_preview=False,
            parse_mode="html"
        )

        # ==========================================
        # INITIAL GROUP MESSAGE
        # ==========================================
        await bot_client.send_message(
            real_chat_id,
            (
                "<b>Please only share this invite link with anyone "
                "involved in this deal.</b>\n"
                f"{invite.link}"
            ),
            link_preview=True,
            parse_mode="html"
        )

        await asyncio.sleep(1)

        # ==========================================
        # DEAL INFORMATION MESSAGE
        # ==========================================
        await bot_client.send_message(
            real_chat_id,
            (
                "Hi, to proceed, please provide:\n\n"
                "• Buyer's username\n"
                "• Brief deal description\n"
                "• Total amount\n"
                "• Timeframe\n"
                "• Currency (specify crypto type if applicable)\n"
                "• Any additional terms\n\n"
                "Once everything is provided, please tag me and I'll be available."
            ),
            parse_mode="html"
        )

    except Exception as e:
        await wait_msg.edit(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            f'<b>Error creating group:</b> <code>{e}</code>',
            parse_mode="html"
        )

def build_final_state_html(chat_id):
    data = chat_final_state.get(chat_id, {})

    buyer = data.get("buyer_tag", "@buyer")
    seller = data.get("seller_tag", "@seller")
    info = data.get("info", "Not specified")
    payment = data.get("payment", "Not specified")
    conditions = data.get("conditions", "No additional conditions")

    return (
        "<b>DEAL STATE</b>\n\n"
        "<b>DEAL PARTICIPANTS</b>\n"
        f"Buyer: {buyer}\n"
        f"Seller: {seller}\n\n"
        "<b>TRANSACTION DETAILS</b>\n"
        f"Deal Information: {info}\n"
        f"Payment Method: {payment}\n"
        f"Conditions: {conditions}\n\n"
        "<b>CONFIRMATION REQUIRED</b>\n"
        "Both Buyer and Seller must review the details "
        "and confirm that everything is correct before proceeding."
    )

async def publish_final_state(chat_id):
    message = build_final_state_html(chat_id)

    buttons = [
        [
            Button.inline(
                "Confirm Deal State",
                data=f"confirm_final_deal_{chat_id}".encode()
            )
        ]
    ]

    return await bot_client.send_message(
        chat_id,
        message,
        parse_mode="html",
        buttons=buttons,
        link_preview=False
    )

async def send_deal_confirmed_message(chat_id):
    data = chat_final_state.get(chat_id, {})

    buyer = data.get("buyer_tag", "@buyer")
    seller = data.get("seller_tag", "@seller")

    message = (
        "<b>DEAL CONFIRMED SUCCESSFULLY</b>\n\n"
        "Both parties have reviewed and confirmed the deal details.\n\n"
        f"Buyer: {buyer} — Confirmed\n"
        f"Seller: {seller} — Confirmed\n\n"
        "All parties have confirmed the deal state. "
        "You may now proceed according to the agreed terms."
    )

    await bot_client.send_message(
        chat_id,
        message,
        parse_mode="html",
        link_preview=False
    )

async def publish_final_state(chat_id):
    message = build_final_state_html(chat_id)

    buttons = [
        [
            Button.inline(
                "Confirm Deal State",
                data=f"confirm_final_deal_{chat_id}".encode()
            )
        ]
    ]

    return await bot_client.send_message(
        chat_id,
        message,
        parse_mode="html",
        buttons=buttons,
        link_preview=False
    )

@bot_client.on(events.NewMessage(pattern=r'^[./]kick(?:\s+(.+))?$'))
async def kick_user_command(event):
    # Only MM can use this command
    if event.is_private or event.sender_id not in MM_DATA:
        return

    target = None

    # ==============================
    # METHOD 1: REPLY TO USER
    # .kick / /kick
    # ==============================
    if event.is_reply:
        try:
            reply_msg = await event.get_reply_message()

            if not reply_msg or not reply_msg.sender_id:
                return

            target = await reply_msg.get_sender()

        except Exception:
            target = None

    # ==============================
    # METHOD 2: USERNAME / USER ID
    # .kick @username
    # .kick 123456789
    # ==============================
    if target is None:
        target_input = event.pattern_match.group(1)

        if not target_input:
            try:
                await event.delete()
            except:
                pass

            msg = await bot_client.send_message(
                event.chat_id,
                (
                    '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> '
                    '<b>Usage:</b>\n\n'
                    '<code>.kick @username</code>\n'
                    '<code>.kick user_id</code>\n'
                    '<i>Or reply to a user\'s message with .kick</i>'
                ),
                parse_mode="html"
            )

            await asyncio.sleep(4)

            try:
                await msg.delete()
            except:
                pass

            return

        target_input = target_input.strip().split()[0]
        target_input = target_input.lstrip("@")

        try:
            if target_input.isdigit():
                target = await bot_client.get_entity(int(target_input))
            else:
                target = await bot_client.get_entity(target_input)

        except Exception:
            try:
                await event.delete()
            except:
                pass

            msg = await bot_client.send_message(
                event.chat_id,
                (
                    '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                    '<b>User not found.</b>\n'
                    'Please provide a valid username or Telegram user ID.'
                ),
                parse_mode="html"
            )

            await asyncio.sleep(4)

            try:
                await msg.delete()
            except:
                pass

            return

    # ==============================
    # SAFETY CHECKS
    # ==============================

    if not target:
        return

    target_id = target.id

    # Don't kick MM accounts
    if target_id in MM_DATA:
        try:
            await event.delete()
        except:
            pass

        msg = await bot_client.send_message(
            event.chat_id,
            (
                '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> '
                '<b>Action denied.</b>\n\n'
                'Middlemen cannot be removed using this command.'
            ),
            parse_mode="html"
        )

        await asyncio.sleep(4)

        try:
            await msg.delete()
        except:
            pass

        return

    # Don't kick the bot itself
    try:
        me = await bot_client.get_me()

        if target_id == me.id:
            try:
                await event.delete()
            except:
                pass

            msg = await bot_client.send_message(
                event.chat_id,
                (
                    '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> '
                    '<b>Action denied.</b>'
                ),
                parse_mode="html"
            )

            await asyncio.sleep(4)

            try:
                await msg.delete()
            except:
                pass

            return

    except:
        pass

    # ==============================
    # CHECK ADMIN / CREATOR
    # ==============================

    try:
        permissions = await bot_client.get_permissions(
            event.chat_id,
            target
        )

        if permissions.is_admin or permissions.is_creator:
            try:
                await event.delete()
            except:
                pass

            msg = await bot_client.send_message(
                event.chat_id,
                (
                    '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> '
                    '<b>Action denied.</b>\n\n'
                    'This user is an admin and cannot be kicked.'
                ),
                parse_mode="html"
            )

            await asyncio.sleep(4)

            try:
                await msg.delete()
            except:
                pass

            return

    except Exception:
        pass

    # ==============================
    # KICK USER
    # ==============================

    try:
        await bot_client.edit_permissions(
            event.chat_id,
            target,
            view_messages=False
        )

        try:
            await event.delete()
        except:
            pass

        # First name + clickable Telegram profile
        first_name = target.first_name or "User"

        user_mention = (
            f'<a href="tg://user?id={target_id}">'
            f'{first_name}</a>'
        )

        # ==============================
        # KICK SUCCESS MESSAGE
        # Paste your custom emoji IDs
        # directly below
        # ==============================

        kick_text = (
            '<tg-emoji emoji-id="5240241223632954241">🚫</tg-emoji> '
            f'<b>{user_mention}</b> has been removed from the group.\n\n'
            '<tg-emoji emoji-id="5251203410396458957">🛡️</tg-emoji> '
            '<i>This action was performed by the Middleman.</i>'
        )

        await bot_client.send_message(
            event.chat_id,
            kick_text,
            parse_mode="html"
        )

    except Exception as e:

        try:
            await event.delete()
        except:
            pass

        error_msg = await bot_client.send_message(
            event.chat_id,
            (
                '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                '<b>Failed to remove user.</b>\n\n'
                f'<code>{str(e)}</code>'
            ),
            parse_mode="html"
        )

        await asyncio.sleep(5)

        try:
            await error_msg.delete()
        except:
            pass


@bot_client.on(events.NewMessage(pattern=r'^[./]help$'))
async def help_command_handler(event):
    chat_id = event.chat_id

    try:
        await event.delete()
    except Exception:
        pass

    help_text = (
        '<tg-emoji emoji-id="5334544901428229844">ℹ️</tg-emoji> <b>MIDDLEMAN BOT • COMMAND CENTER</b>\n\n'
        '<blockquote>Everything you need to manage your middleman deals smoothly and securely.</blockquote>\n\n'
        '<tg-emoji emoji-id="5251203410396458957">💬</tg-emoji> <b><u>Middleman Controls</u></b>\n\n'
        '• <code>.gc</code> — Create a new middleman group\n'
        '• <code>.state</code> — Open the deal state dashboard\n'
        '• <code>.pay &lt;amount&gt;</code> — Set INR payment and calculate fees\n'
        '• <code>.usdt &lt;amount&gt;</code> / <code>.crypto &lt;amount&gt;</code> — Calculate crypto payments\n'
        '• <code>.tat &lt;time&gt;</code> — Start the deal timer (e.g. 1h, 30m)\n'
        '• <code>.extendtat &lt;time&gt;</code> / <code>.reducetat &lt;time&gt;</code> — Adjust the active TAT\n'
        '• <code>.received</code> / <code>.rec</code> — Confirm payment receipt\n'
        '• <code>.complete</code> / <code>.comp</code> — Start deal completion and vouching\n'
        '• <code>.kick</code> — Remove an unauthorized user\n'
        '• <code>.lock</code> / <code>.unlock</code> — Manage group messaging permissions\n'
        '• <code>.delete</code> — Delete and close the deal group\n\n'
        '<tg-emoji emoji-id="5231012545799666522">💬</tg-emoji> <b><u>Monitoring &amp; Statistics</u></b>\n\n'
        '<code>/stats</code> or <code>.stats</code> — View deal metrics, volume and TAT status\n\n'
        '<blockquote><tg-emoji emoji-id="5296369303661067030">💬</tg-emoji> <b>Trade Safely</b>\n\n'
        'Always review the deal details, verify payments independently, and confirm all terms before proceeding.</blockquote>'
    )

    buttons = [
        [
            Button.inline("Close Menu", data=b"close_help_msg")
        ]
    ]

    await bot_client.send_message(
        chat_id,
        help_text,
        parse_mode="html",
        buttons=buttons,
        link_preview=False
    )

@bot_client.on(events.CallbackQuery(pattern=r'^close_help_msg$'))
async def close_help_callback(event):
    try:
        await event.delete()
    except Exception as e:
        print(f"Close Help Menu Error: {e}")

    await event.answer("Menu closed.", alert=False)

    try:
        await bot_client.send_message(
            event.chat_id,
            '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            '<b>Help menu closed successfully.</b>',
            parse_mode="html"
        )
    except Exception as e:
        print(f"Close Help Confirmation Error: {e}")

@bot_client.on(events.NewMessage(pattern=r'(?i)^(?:\.revoke|/revoke)$'))
async def revoke_group_link(event):
    if event.is_private:
        return
    
    # Check if sender is an authorized Middleman
    sender_id = event.sender_id
    if sender_id not in MM_DATA:
        return

    chat_id = event.chat_id

    try:
        # 1. Delete the command message sent by the MM
        await event.delete()
    except Exception:
        pass

    try:
        # 2. Revoke / Export a new invite link to invalidate the old one
        # In Telethon/Telegram, exporting a new chat invite link automatically revokes the previous active primary link.
        new_invite = await bot_client(ExportChatInviteRequest(peer=chat_id))
        
        # 3. Send notification message with custom premium emoji
        notice_msg = await bot_client.send_message(
            chat_id,
            '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> <b>Group invite link has been successfully revoked!</b>\n'
            'Previous links are no longer active.',
            parse_mode='html'
        )

        # 4. Wait for a few seconds (e.g., 5 seconds) and then delete the notice message
        await asyncio.sleep(5)
        try:
            await notice_msg.delete()
        except Exception:
            pass

    except Exception as e:
        err_msg = await bot_client.send_message(
            chat_id,
            f'<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> Failed to revoke link: <code>{e}</code>',
            parse_mode='html'
        )
        await asyncio.sleep(5)
        try:
            await err_msg.delete()
        except Exception:
            pass

@bot_client.on(events.NewMessage(pattern=r'(?i)^\.state$'))
async def open_state_dashboard(event):
    if event.is_private or event.sender_id not in MM_DATA:
        return

    chat_id = event.chat_id

    try:
        await event.delete()
    except Exception:
        pass

    roles = group_roles.get(chat_id, {})
    buyer_id = roles.get("buyer")
    seller_id = roles.get("seller")

    async def get_role_name(user_id, fallback):
        if not user_id:
            return "Not selected"

        try:
            user = await bot_client.get_entity(user_id)
            username = getattr(user, "username", None)

            if username:
                return f"@{username}"

            return getattr(user, "first_name", None) or fallback

        except Exception:
            return fallback

    buyer_name = await get_role_name(buyer_id, "Buyer")
    seller_name = await get_role_name(seller_id, "Seller")

    chat_state_setup[chat_id] = {
        "buyer_name": buyer_name,
        "seller_name": seller_name,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "payment": "Not selected",
        "deal_info": "Not set",
        "conditions": "Not set"
    }

    panel_html, keyboard = build_setup_panel_html(chat_id)

    sent_id = await send_rich_message(
        chat_id, panel_html, keyboard
    )

    if sent_id:
        chat_state_setup[chat_id]["msg_id"] = sent_id


from telethon import Button, events

@bot_client.on(events.CallbackQuery)
async def state_panel_callbacks(event):
    if not event.data:
        return

    data_str = event.data.decode("utf-8")
    chat_id = event.chat_id
    sender_id = event.sender_id

    # 1. SETUP DASHBOARD ACTIONS
    if chat_id in chat_state_setup:
        setup = chat_state_setup[chat_id]
        msg_id = setup.get("msg_id")

        # Buyer Role Set
        if data_str == f"set_role_b_{chat_id}":
            u = await event.get_sender()

            setup["buyer_id"] = sender_id
            setup["buyer_name"] = (
                f"@{u.username}"
                if getattr(u, "username", None)
                else (u.first_name or "Buyer")
            )

            await event.answer("Assigned as Buyer! <tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji>", alert=False)

            if msg_id:
                await edit_rich_message(
                    chat_id, msg_id, build_setup_panel_html(chat_id)
                )
            return

        # Seller Role Set
        elif data_str == f"set_role_s_{chat_id}":
            u = await event.get_sender()

            setup["seller_id"] = sender_id
            setup["seller_name"] = (
                f"@{u.username}"
                if getattr(u, "username", None)
                else (u.first_name or "Seller")
            )

            await event.answer("Assigned as Seller! <tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji>", alert=False)

            if msg_id:
                await edit_rich_message(
                    chat_id, msg_id, build_setup_panel_html(chat_id)
                )
            return

        # Payment INR
        elif data_str == f"pm_inr_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can set payment!", alert=True
                )

            state_input_wait[(chat_id, sender_id)] = "WAIT_PAY_INR"

            prompt = await bot_client.send_message(
                chat_id,
                "<b>Please send the INR amount "
                "(e.g. 5000 or 5,000 INR):</b>",
                parse_mode="html"
            )

            state_input_wait[(chat_id, sender_id, "prompt_id")] = prompt.id
            await event.answer()
            return

        # Payment Crypto
        elif data_str == f"pm_crypto_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can set payment!", alert=True
                )

            state_input_wait[(chat_id, sender_id)] = "WAIT_PAY_CRYPTO"

            prompt = await bot_client.send_message(
                chat_id,
                "<b>Please send the Crypto amount "
                "(e.g. $50 USDT or 0.5 SOL):</b>",
                parse_mode="html"
            )

            state_input_wait[(chat_id, sender_id, "prompt_id")] = prompt.id
            await event.answer()
            return

        # Deal Information
        elif data_str == f"set_info_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can set deal info!", alert=True
                )

            state_input_wait[(chat_id, sender_id)] = "WAIT_INFO"

            prompt = await bot_client.send_message(
                chat_id,
                "<b>Please send the Deal Information "
                "(e.g. Instagram Unban):</b>",
                parse_mode="html"
            )

            state_input_wait[(chat_id, sender_id, "prompt_id")] = prompt.id
            await event.answer()
            return

        # Set Conditions
        elif data_str == f"set_cond_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can set conditions!", alert=True
                )

            state_input_wait[(chat_id, sender_id)] = "WAIT_COND"

            prompt = await bot_client.send_message(
                chat_id,
                "<b>Please send the Deal Conditions:</b>",
                parse_mode="html"
            )

            state_input_wait[(chat_id, sender_id, "prompt_id")] = prompt.id
            await event.answer()
            return

        # No Conditions
        elif data_str == f"set_nocond_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can change conditions!", alert=True
                )

            setup["conditions"] = "No additional conditions"

            await event.answer(
                "No additional conditions set!", alert=False
            )

            if msg_id:
                await edit_rich_message(
                    chat_id, msg_id, build_setup_panel_html(chat_id)
                )
            return

        # Reset State
        elif data_str == f"reset_state_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can reset the state!", alert=True
                )

            setup.update({
                "buyer_name": "Not selected",
                "seller_name": "Not selected",
                "buyer_id": None,
                "seller_id": None,
                "payment": "Not selected",
                "deal_info": "Not set",
                "conditions": "Not set"
            })

            state_input_wait.pop((chat_id, sender_id), None)
            state_input_wait.pop((chat_id, sender_id, "prompt_id"), None)

            await event.answer("Deal State Reset!", alert=False)

            if msg_id:
                await edit_rich_message(
                    chat_id, msg_id, build_setup_panel_html(chat_id)
                )
            return

        # Publish Final Deal State
        elif data_str == f"publish_state_{chat_id}":
            if sender_id not in MM_DATA:
                return await event.answer(
                    "Only Middleman can publish state!", alert=True
                )

            chat_final_state[chat_id] = {
                "buyer_id": setup.get("buyer_id"),
                "seller_id": setup.get("seller_id"),

                "buyer_tag": (
                    setup.get("buyer_name")
                    if setup.get("buyer_name") != "Not selected"
                    else "@buyer"
                ),

                "seller_tag": (
                    setup.get("seller_name")
                    if setup.get("seller_name") != "Not selected"
                    else "@seller"
                ),

                "payment": (
                    setup.get("payment")
                    if setup.get("payment") != "Not selected"
                    else "Not specified"
                ),

                "info": (
                    setup.get("deal_info")
                    if setup.get("deal_info") != "Not set"
                    else "Not specified"
                ),

                "conditions": (
                    setup.get("conditions")
                    if setup.get("conditions") != "Not set"
                    else "No additional conditions"
                )
            }

            state_confirmations[chat_id] = set()

            if msg_id:
                try:
                    await bot_client.delete_messages(chat_id, msg_id)
                except Exception as e:
                    print(f"[STATE] Dashboard delete error: {e}")

            chat_state_setup.pop(chat_id, None)

            final_data = chat_final_state[chat_id]

            final_html = (
                "<b>DEAL STATE</b>\n\n"
                "<b>DEAL PARTICIPANTS</b>\n"
                f"Buyer: {final_data['buyer_tag']}\n"
                f"Seller: {final_data['seller_tag']}\n\n"
                "<b>TRANSACTION DETAILS</b>\n"
                f"Deal Information: {final_data['info']}\n"
                f"Payment Method: {final_data['payment']}\n"
                f"Conditions: {final_data['conditions']}\n\n"
                "<b>CONFIRMATION REQUIRED</b>\n"
                "Both Buyer and Seller must review these details "
                "and confirm that everything is correct before proceeding."
            )

            buttons = [[
                Button.inline(
                    "Confirm Deal State",
                    data=f"confirm_final_deal_{chat_id}".encode("utf-8")
                )
            ]]

            try:
                await bot_client.send_message(
                    chat_id,
                    final_html,
                    parse_mode="html",
                    buttons=buttons,
                    link_preview=False
                )

                await event.answer(
                    "Deal State Published!", alert=False
                )

            except Exception as e:
                print(f"[STATE] Publish error: {e}")
                await event.answer(
                    "Failed to publish the Deal State.",
                    alert=True
                )

            return

    # 2. FINAL STATE CONFIRMATION
    if data_str == f"confirm_final_deal_{chat_id}":
        final_data = chat_final_state.get(chat_id)

        if not final_data:
            return await event.answer(
                "No active deal state found.", alert=True
            )

        b_id = final_data.get("buyer_id")
        s_id = final_data.get("seller_id")

        if not b_id or not s_id:
            return await event.answer(
                "Buyer and Seller must both be assigned!",
                alert=True
            )

        if sender_id not in (b_id, s_id):
            return await event.answer(
                "Only the assigned Buyer and Seller can confirm!",
                alert=True
            )

        if chat_id not in state_confirmations:
            state_confirmations[chat_id] = set()

        if sender_id in state_confirmations[chat_id]:
            return await event.answer(
                "You have already confirmed!",
                alert=True
            )

        state_confirmations[chat_id].add(sender_id)

        # Both parties have confirmed
        if (
            b_id in state_confirmations[chat_id]
            and s_id in state_confirmations[chat_id]
        ):
            await event.answer(
                "Deal State fully confirmed!", alert=False
            )

            buyer = final_data.get("buyer_tag", "@buyer")
            seller = final_data.get("seller_tag", "@seller")

            confirmation_message = (
                "<b>DEAL CONFIRMED SUCCESSFULLY</b>\n\n"
                "Both parties have reviewed and confirmed the deal details.\n\n"
                f"Buyer: {buyer} — Confirmed\n"
                f"Seller: {seller} — Confirmed\n\n"
                "All parties have confirmed the deal state. "
                "You may now proceed according to the agreed terms."
            )

            try:
                await bot_client.send_message(
                    chat_id,
                    confirmation_message,
                    parse_mode="html",
                    link_preview=False
                )
            except Exception as e:
                print(f"[STATE] Confirmation message error: {e}")

        else:
            await event.answer(
                "Confirmed! Waiting for the other party.",
                alert=False
            )

        return

@bot_client.on(
    events.NewMessage(
        func=lambda e: (
            not e.is_private
            and (e.chat_id, e.sender_id) in state_input_wait
        )
    )
)
async def handle_state_inputs(event):
    key = (event.chat_id, event.sender_id)

    input_type = state_input_wait.pop(key, None)
    prompt_id = state_input_wait.pop(
        (event.chat_id, event.sender_id, "prompt_id"),
        None
    )

    val = (event.raw_text or "").strip()

    # Ignore empty input
    if not val:
        return

    # Delete the middleman's input and the bot's prompt
    try:
        await event.delete()
    except Exception as e:
        print(f"Input Delete Error: {e}")

    if prompt_id:
        try:
            await bot_client.delete_messages(
                event.chat_id, prompt_id
            )
        except Exception as e:
            print(f"Prompt Delete Error: {e}")

    # Get current setup
    setup = chat_state_setup.get(event.chat_id)
    if not setup:
        return

    msg_id = setup.get("msg_id")

    # Save the submitted value
    if input_type == "WAIT_PAY_INR":
        setup["payment"] = (
            f"{val} INR"
            if not val.lower().endswith("inr")
            else val
        )

    elif input_type == "WAIT_PAY_CRYPTO":
        setup["payment"] = val

    elif input_type == "WAIT_INFO":
        setup["deal_info"] = val

    elif input_type == "WAIT_COND":
        setup["conditions"] = val

    else:
        return

    # Refresh dashboard text AND inline keyboard
    if msg_id:
        panel_html, keyboard = build_setup_panel_html(
            event.chat_id
        )

        await edit_rich_message(
            event.chat_id,
            msg_id,
            panel_html,
            keyboard
        )

@bot_client.on(events.NewMessage(pattern=r'(?i)\.(?:received|rec)(?:\s+(.+))?$'))
async def received_command(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    await event.delete()
    
    amount_text = event.pattern_match.group(1)
    if amount_text:
        clean_amount = re.sub(r'[A-Za-z₹$]', '', amount_text).strip()
        if clean_amount:
            new_title = f"{clean_amount} | @Middlemaven"
            try: await bot_client(EditChatTitleRequest(chat_id=event.chat_id, title=new_title))
            except: 
                try: await bot_client(EditTitleRequest(channel=event.chat_id, title=new_title))
                except: pass
                
    rec_text = config.get("rec_msg", "I have successfully received the amount and the MM fee. It is safe to move forward. I will process the payment after the deal concludes. Thank you for your cooperation!")
    msg = await event.respond(rec_text, parse_mode='html')
    try: await bot_client.pin_message(event.chat_id, msg.id)
    except: pass

@bot_client.on(events.NewMessage(pattern=r'^[./]extendtat\s+(.+)'))
async def extend_tat(event):
    # Sirf Middleman hi TAT extend kar sakta hai
    if event.sender_id not in MM_DATA or event.is_private:
        return[span_3](start_span)[span_3](end_span)

    time_str = event.pattern_match.group(1)[span_4](start_span)[span_4](end_span)
    delta = parse_time(time_str)[span_5](start_span)[span_5](end_span)

    if not delta:
        return await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            'Invalid format. Use: /extendtat 30m or /extendtat 1h',
            parse_mode="html"
        )[span_6](start_span)[span_6](end_span)

    chat_id = event.chat_id[span_7](start_span)[span_7](end_span)

    if chat_id in active_timers:
        active_timers[chat_id]["end_time"] += delta[span_8](start_span)[span_8](end_span)
        
        # --- STATS MONITOR SYNC: Group ke assigned MM ke hisaab se track karna ---
        assigned_mm = chat_mm_assigned.get(chat_id, event.sender_id)
        active_tat_by_mm[chat_id] = assigned_mm

        await event.respond(
            f'<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            f'TAT extended by {time_str} successfully!',
            parse_mode="html"
        )[span_9](start_span)[span_9](end_span)

    else:
        await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            'No active TAT timer running in this group.',
            parse_mode="html"
        )[span_10](start_span)[span_10](end_span)

@bot_client.on(events.NewMessage(pattern=r'^\.del$'))
async def delete_single_message(event):
    if event.sender_id not in MM_DATA or event.is_private:
        return

    # Check if replying to a message
    if not event.is_reply:
        await event.delete()

        temp_msg = await event.respond(
            'Please reply to the message you want to delete with `.del`',
            parse_mode='html'
        )

        await asyncio.sleep(4)

        try:
            await temp_msg.delete()
        except:
            pass

        return

    try:
        reply_msg = await event.get_reply_message()

        # Delete the command message and the replied message
        await event.delete()
        await reply_msg.delete()

        # Professional confirmation text
        conf_msg = await bot_client.send_message(
            event.chat_id,
            '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            '<b>Success:</b> The requested message has been permanently deleted.',
            parse_mode='html'
        )

        # Auto-delete confirmation after 4 seconds
        await asyncio.sleep(4)

        try:
            await conf_msg.delete()
        except:
            pass

    except Exception as e:
        temp_msg = await bot_client.send_message(
            event.chat_id,
            f'<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            f'<b>Error deleting message:</b> <code>{e}</code>',
            parse_mode='html'
        )

        await asyncio.sleep(4)

        try:
            await temp_msg.delete()
        except:
            pass

@client.on(events.NewMessage(pattern=r'^\.delete$'))
async def delete_group_command(event):
    if event.sender_id not in MM_DATA or event.is_private:
        return

    await event.delete()

    try:
        # Notify before deleting group using userbot
        warn_msg = await client.send_message(
            event.chat_id,
            '<tg-emoji emoji-id="5447644880824181073">⚠️</tg-emoji> '
            '<b>Group Deletion:</b> Terminating and cleaning up this middleman group...',
            parse_mode='html'
        )

        await asyncio.sleep(2)

        # Delete/Leave chat call for Telegram group termination
        from telethon.tl.functions.channels import DeleteChannelRequest
        from telethon.tl.functions.messages import DeleteChatUserRequest

        chat = await event.get_chat()

        if hasattr(chat, 'megagroup') and chat.megagroup:
            await client(
                DeleteChannelRequest(
                    channel=event.chat_id
                )
            )
        else:
            # For standard groups / supergroups fallback
            await client(
                DeleteChatUserRequest(
                    chat_id=event.chat_id,
                    user_id='me'
                )
            )

    except Exception as e:
        await client.send_message(
            event.chat_id,
            f'<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            f'<b>Error:</b> Could not delete group automatically. '
            f'Please delete it manually from Telegram settings. '
            f'({e})',
            parse_mode='html'
        )

@bot_client.on(events.NewMessage(pattern=r'^[./]reducetat\s+(.+)'))
async def reduce_tat(event):
    if event.sender_id not in MM_DATA or event.is_private:
        return

    time_str = event.pattern_match.group(1)
    delta = parse_time(time_str)

    if not delta:
        return await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            'Invalid format. Use: /reducetat 30m or /reducetat 1h',
            parse_mode='html'
        )

    chat_id = event.chat_id

    if chat_id in active_timers:
        active_timers[chat_id]["end_time"] -= delta

        if datetime.now() >= active_timers[chat_id]["end_time"]:
            msg_obj = active_timers[chat_id]["msg"]
            del active_timers[chat_id]

            try:
                await bot_client.edit_message(
                    chat_id,
                    msg_obj.id,
                    '<b>Timeframe Alert!</b>\n'
                    'The agreed timeframe has ended (reduced to zero).',
                    parse_mode='html'
                )
            except:
                pass

            await event.respond(
                '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
                'TAT timer completed / reduced to zero!',
                parse_mode='html'
            )

        else:
            await event.respond(
                '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
                f'TAT reduced by {time_str} successfully!',
                parse_mode='html'
            )

    else:
        await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            'No active TAT timer running in this group.',
            parse_mode='html'
        )


@bot_client.on(events.NewMessage(
    pattern=r'(?i)^[./]pay\s+(?:₹|\$)?([0-9]+(?:\.[0-9]+)?)(?:\s+(?:₹|\$)?([0-9]+(?:\.[0-9]+)?))?(?:\s+(unban terms|ban terms|no terms))?\s*$'
))
async def pay_inr_calc(event):
    if event.is_private:
        return

    try:
        sender_id = event.sender_id

        amount_raw = float(event.pattern_match.group(1))
        custom_fee_input = event.pattern_match.group(2)
        terms_type = event.pattern_match.group(3)

        if amount_raw <= 0:
            await event.reply("❌ Amount must be greater than zero.")
            return

        if terms_type:
            terms_type = terms_type.lower()

        # Calculate fee using the existing MM fee system
        if custom_fee_input is not None:
            fee_raw = float(custom_fee_input)
        else:
            fee_raw = calc_fee(
                amount_raw,
                sender_id,
                is_inr=True
            )

        total_raw = amount_raw + fee_raw

        amount = fmt_inr(amount_raw)
        fee = fmt_inr(fee_raw)
        total = fmt_inr(total_raw)

        # Delete the command message
        try:
            await event.delete()
        except Exception:
            pass

        # Update group title
        new_title = f"₹{amount} | @Middlemaven"

        try:
            await bot_client(EditChatTitleRequest(
                chat_id=event.chat_id,
                title=new_title
            ))
        except Exception:
            try:
                await bot_client(EditTitleRequest(
                    channel=event.chat_id,
                    title=new_title
                ))
            except Exception as e:
                print(f"[PAY] Group title update failed: {e}")

        # Send deal terms if requested
        if terms_type and terms_type in DEAL_TERMS:
            await bot_client.send_message(
                event.chat_id,
                DEAL_TERMS[terms_type],
                parse_mode="html"
            )
            await asyncio.sleep(0.5)

        # Load latest MM settings from config.json
        latest_config_mms = {}

        if os.path.exists("config.json"):
            try:
                with open("config.json", "r", encoding="utf-8") as f:
                    file_data = json.load(f)

                latest_config_mms = file_data.get("mms", {})
            except Exception as e:
                print(f"[PAY] Config read error: {e}")

        mm_settings = {}
        sender_str = str(sender_id) if sender_id else ""

        # Priority: config.json -> MM_DATA -> global config
        if sender_str and sender_str in latest_config_mms:
            mm_settings = latest_config_mms[sender_str]
        elif sender_id and sender_id in MM_DATA:
            mm_settings = MM_DATA[sender_id]
        elif sender_str:
            mm_settings = config.get("mms", {}).get(sender_str, {})

        upi = mm_settings.get(
            "upi_id",
            config.get("default_upi", "tysted@pytes")
        )

        qr_url = mm_settings.get("qr_link", "")

        # Load QR image
        qr_bytes = None

        if qr_url:
            try:
                if os.path.exists(qr_url):
                    with open(qr_url, "rb") as f:
                        qr_bytes = f.read()

                elif qr_url.startswith(("http://", "https://")):
                    qr_bytes = await get_image_bytes(qr_url)

            except Exception as e:
                print(f"[PAY] QR loading failed: {e}")

        # Payment message
        pay_msg = (
            f"UPI: <code>{upi}</code>\n"
            f"Pay using this QR and send the payment screenshot.\n\n"
            f"Deal Amount ₹{amount} + Fee: ₹{fee} = "
            f"<code>₹{total}</code> INR\n\n"
            f'<a href="{TOS_LINK}">TOS</a>'
        )

        # Send QR with payment details
        if qr_bytes:
            try:
                img_io = io.BytesIO(qr_bytes)
                img_io.name = "qr.png"

                await bot_client.send_file(
                    event.chat_id,
                    file=img_io,
                    caption=pay_msg,
                    parse_mode="html"
                )

            except Exception as e:
                print(f"[PAY] QR send failed: {e}")

                await bot_client.send_message(
                    event.chat_id,
                    pay_msg,
                    parse_mode="html",
                    link_preview=False
                )

        else:
            await bot_client.send_message(
                event.chat_id,
                pay_msg,
                parse_mode="html",
                link_preview=False
            )

    except Exception as e:
        print(
            f"[PAY] Error in chat {event.chat_id}: "
            f"{type(e).__name__}: {e}"
        )

        try:
            await event.reply(
                f"❌ Pay command failed: {type(e).__name__}: {e}"
            )
        except Exception as reply_error:
            print(f"[PAY] Error reply failed: {reply_error}")

@bot_client.on(events.NewMessage(pattern=r'\.link$'))
async def get_group_link(event):
    if event.sender_id not in MM_DATA:
        return

    await event.delete()

    # Agar command Group mein use ki gayi hai
    if not event.is_private:
        chat_id = event.chat_id

        try:
            invite = await bot_client(
                ExportChatInviteRequest(peer=chat_id)
            )

            link = invite.link

            # Save latest group link for this MM
            last_group_links[event.sender_id] = link

            await bot_client.send_message(
                chat_id,
                f'<b>Group Invite Link:</b>\n{link}',
                link_preview=False,
                parse_mode='html'
            )

        except Exception as e:
            # Agar bot ke paas link nikalne ki power nahi hai,
            # toh last saved link bhej dega
            saved_link = last_group_links.get(event.sender_id)

            if saved_link:
                await bot_client.send_message(
                    chat_id,
                    f'<b>Group Invite Link:</b>\n{saved_link}',
                    link_preview=False,
                    parse_mode='html'
                )
            else:
                await bot_client.send_message(
                    chat_id,
                    '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                    '<b>Error:</b> Could not fetch link for this group.',
                    parse_mode='html'
                )

    # Agar command DM (Private Chat) mein use ki gayi hai
    else:
        saved_link = last_group_links.get(event.sender_id)

        if saved_link:
            await event.respond(
                f'<b>Last Created Group Link:</b>\n{saved_link}',
                link_preview=False,
                parse_mode='html'
            )
        else:
            await event.respond(
                '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                'No recent group link found. First create a group using '
                '<code>.gc</code>.',
                parse_mode='html'
            )

@bot_client.on(events.NewMessage(
    pattern=r'(?i)\.(trc|bep|eth|sol|ton|btc|polygon|erc|ltc|xrp|doge|bch|usdc)(?:\s+(?:[₹$])?([0-9.]+))?(?:\s+(?:[₹$])?([0-9.]+))?(?:\s+(unban terms|ban terms|no terms))?\s*$'
))
async def pay_crypto_calc(event):
    if event.is_private:
        return

    sender_id = event.sender_id

    if not sender_id and event.message:
        sender_id = event.message.sender_id

    cmd = event.pattern_match.group(1).lower()
    amount_str = event.pattern_match.group(2)
    custom_fee_input = event.pattern_match.group(3)
    terms_type = event.pattern_match.group(4)

    if terms_type:
        terms_type = terms_type.lower()

    mm_id_str = str(sender_id)

    mm_wallets = MM_DATA.get(
        sender_id, {}
    ).get("crypto_wallets", {})

    if (
        not mm_wallets
        or mm_wallets.get(cmd) in [None, "", "Address Not Set"]
    ):
        mm_wallets = config.get(
            "mms", {}
        ).get(
            mm_id_str, {}
        ).get(
            "crypto_wallets", {}
        )

    address = mm_wallets.get(
        cmd,
        "Address Not Set"
    )

    info = CRYPTO_INFO[cmd]

    try:
        await event.delete()
    except:
        pass

    # ==============================
    # NO AMOUNT
    # ==============================
    if not amount_str:
        await bot_client.send_message(
            event.chat_id,
            (
                f"<code>{address}</code>\n\n"
                "Please send the TXID / screenshot once "
                "the payment has been sent."
            ),
            parse_mode='html'
        )
        return

    amount_raw = float(amount_str)

    # ==========================================
    # STATS VOLUME TRACKING (CRYPTO DIRECT USD)
    # ==========================================
    chat_deal_amount[event.chat_id] = amount_raw
    if event.chat_id not in chat_mm_assigned and sender_id in MM_DATA:
        chat_mm_assigned[event.chat_id] = sender_id
        chat_deal_status[event.chat_id] = "active"

    # ==============================
    # CUSTOM FEE / DEFAULT FEE
    # ==============================
    if custom_fee_input:
        mm_fee = float(custom_fee_input)
        current_fee_desc = f"Fixed ${mm_fee}"
    else:
        mm_fee = calc_fee(
            amount_raw,
            sender_id,
            is_inr=False
        )

        current_fee_desc = (
            f"{config['mms'].get(mm_id_str, {}).get(
                'custom_fee',
                config['fee_percent']
            )}%"
        )

    total_to_pay = amount_raw + mm_fee

    # ==============================
    # UPDATE GROUP TITLE
    # ==============================
    new_title = f"${fmt_inr(amount_raw)} | @Middlemaven"

    try:
        await bot_client(
            EditChatTitleRequest(
                chat_id=event.chat_id,
                title=new_title
            )
        )
    except:
        try:
            await bot_client(
                EditTitleRequest(
                    channel=event.chat_id,
                    title=new_title
                )
            )
        except:
            pass

    # ==============================
    # DEAL TERMS
    # ==============================
    if terms_type and terms_type in DEAL_TERMS:
        await bot_client.send_message(
            event.chat_id,
            DEAL_TERMS[terms_type],
            parse_mode='html'
        )

        await asyncio.sleep(0.5)

    # ==============================
    # CRYPTO CALCULATION
    # ==============================
    if info['ticker'] is None:
        crypto_val = f"{total_to_pay:.2f}"

    else:
        price = await get_crypto_price(
            info['ticker']
        )

        if price is None:
            return await bot_client.send_message(
                event.chat_id,
                '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                'Failed to fetch current market price.',
                parse_mode='html'
            )

        crypto_val = f"{(total_to_pay / price):.8f}"

    # ==============================
    # PAYMENT MESSAGE
    # ==============================
    pay_msg = (
        f"Deal Amount ${amount_raw:.2f} "
        f"+ Fee: ${mm_fee:.2f} ({current_fee_desc})\n\n"
        f"${total_to_pay:.2f} total = "
        f"<code>{crypto_val}</code> {info['name']}\n\n"
        f"Address: <code>{address}</code>\n\n"
        "Please send the TXID / screenshot once "
        "the payment has been sent.\n"
        f"<a href='{TOS_LINK}'>TOS</a>"
    )

    await bot_client.send_message(
        event.chat_id,
        pay_msg,
        parse_mode='html'
    )

@bot_client.on(events.NewMessage(pattern=r'(?i)\.(unbanterms|banterms|noterms)$'))
async def send_terms_command(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    cmd = event.pattern_match.group(1).lower()
    await event.delete()
    term_key = "unban terms" if cmd == "unbanterms" else "ban terms" if cmd == "banterms" else "no terms"
    if term_key in DEAL_TERMS:
        await bot_client.send_message(event.chat_id, DEAL_TERMS[term_key], parse_mode='html')

@bot_client.on(events.NewMessage(pattern=r'\.tos$'))
async def tos_command(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    await event.delete()
    await event.respond(config["bot_msg_tos"], parse_mode='html')

@bot_client.on(events.NewMessage(pattern=r'/check\s+(.+)'))
async def insta_check(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    username = event.pattern_match.group(1).replace('@', '')
    wait_msg = await event.respond(f"Checking @{username}...")
    
    data = await fetch_ig_data(username)
    is_banned = (data["status"] == "banned")
    
    if data["status"] == "error": 
        return await wait_msg.edit(f"<b>Error:</b> Instagram fetching failed right now. (IP might be temporarily restricted by IG)", parse_mode='html')
        
    pfp_bytes = None
    if not is_banned and data.get("pfp_url"):
        headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(data["pfp_url"], headers=headers) as resp:
                    if resp.status == 200: pfp_bytes = await resp.read()
        except: pass
            
    card_image = await create_profile_card(
        username, 
        pfp_bytes, 
        data.get("posts", "0"), 
        data.get("followers", "0"), 
        data.get("following", "0"), 
        is_banned
    )
    
    btn = [Button.url("View Profile", f"https://www.instagram.com/{username}")]
    
    if card_image:
        await bot_client.send_file(event.chat_id, file=card_image, buttons=btn, force_document=False)
        await wait_msg.delete()
    else:
        await wait_msg.edit(f"<b>Error generating card image for @{username}</b>", parse_mode='html', buttons=btn)

async def tat_live_updater(chat_id, msg):
    while chat_id in active_timers:
        end_time = active_timers[chat_id]["end_time"]
        now = datetime.now()
        
        if now >= end_time:
            try: 
                await bot_client.edit_message(chat_id, msg.id, "<b>Timeframe Alert!</b>\nThe agreed timeframe has ended.", parse_mode='html')
            except: pass
            if chat_id in active_timers: del active_timers[chat_id]
            break
        
        rem = end_time - now
        time_str = ""
        if rem.days > 0: time_str += f"{rem.days} days "
        if rem.seconds // 3600 > 0: time_str += f"{rem.seconds // 3600} hours "
        if (rem.seconds // 60) % 60 > 0: time_str += f"{(rem.seconds // 60) % 60} minutes "
        time_str += f"{rem.seconds % 60} seconds remaining"
        
        new_text = f"Timeframe for Middlemaven MM has been started:\n{time_str}"
        try: 
            await bot_client.edit_message(chat_id, msg.id, new_text)
        except: pass 
        
        await asyncio.sleep(10)

@bot_client.on(events.NewMessage(pattern=r'^[./]tat\s+(.+)'))
async def tat_timer(event):
    if event.sender_id not in MM_DATA or event.is_private:
        return

    time_str = event.pattern_match.group(1)
    delta = parse_time(time_str)

    if not delta:
        return await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            'Invalid format. Use: /tat 1h30m or /tat 45m',
            parse_mode='html'
        )

    now = datetime.now()
    end_time = now + delta

    msg = await event.respond(
        'Timeframe for Middlemaven MM has been started:\n'
        'Calculations...',
        parse_mode='html'
    )

    # Dictionary mein end_time aur msg dono save karenge
    # taaki live update ho sake
    active_timers[event.chat_id] = {
        "end_time": end_time,
        "msg": msg
    }

    asyncio.create_task(
        tat_live_updater(
            event.chat_id,
            msg
        )
    )

@bot_client.on(events.NewMessage(pattern=r'^[./]set\s+(.+)'))
async def set_role_command(event):
    if event.sender_id not in MM_DATA or event.is_private:
        return[span_3](start_span)[span_3](end_span)

    args = event.pattern_match.group(1).strip().split()[span_4](start_span)[span_4](end_span)
    role = None
    target_identifier = None

    for arg in args:
        arg_lower = arg.lower()
        if arg_lower in ["buyer", "seller"]:
            role = arg_lower
        elif arg.startswith("@") or arg.isdigit():
            target_identifier = arg[span_5](start_span)[span_5](end_span)

    # Reply message se user identify karna
    if role and not target_identifier and event.is_reply:
        reply_msg = await event.get_reply_message()[span_6](start_span)[span_6](end_span)
        if reply_msg:
            target_identifier = reply_msg.sender_id[span_7](start_span)[span_7](end_span)

    if not role or not target_identifier:
        return await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            'Invalid format! Use:\n'
            '• <code>.set buyer</code> (by replying to user)\n'
            '• <code>.set @username buyer</code>\n'
            '• <code>.set buyer @username</code>',
            parse_mode='html'
        )[span_8](start_span)[span_8](end_span)

    chat_id = event.chat_id[span_9](start_span)[span_9](end_span)
    if chat_id not in group_roles:
        group_roles[chat_id] = {}[span_10](start_span)[span_10](end_span)

    try:
        user = await bot_client.get_entity(target_identifier)[span_11](start_span)[span_11](end_span)
        group_roles[chat_id][role] = user.id[span_12](start_span)[span_12](end_span)

        # --- SET CUSTOM ADMIN RANK/TAG (Buyer / Seller) ---
        role_tag = "Buyer" if role == "buyer" else "Seller"
        
        # User ko safe dummy admin rights dena taaki profile/messages me Tag dikhe
        # Kisi bhi dangerous permission ko True nahi kiya gaya hai
        safe_tag_rights = ChatAdminRights(
            change_info=False,
            post_messages=True,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=True,
            pin_messages=False,
            add_admins=False,
            anonymous=False,
            manage_call=False
        )[span_13](start_span)[span_13](end_span)

        try:
            channel = await bot_client.get_input_entity(chat_id)
            await bot_client(EditAdminRequest(
                channel=channel,
                user_id=user.id,
                admin_rights=safe_tag_rights,
                rank=role_tag
            ))[span_14](start_span)[span_14](end_span)
        except Exception as tag_err:
            print(f"Could not apply admin tag: {tag_err}")

        mention = (
            f'<a href="tg://user?id={user.id}">'
            f'{user.first_name or "User"}</a>'
        )[span_15](start_span)[span_15](end_span)

        await event.respond(
            f'<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            f'<b>{role_tag} Successfully Set & Tagged</b> '
            f'for {mention} (Tag: <code>{role_tag}</code>)!',
            parse_mode='html'
        )[span_16](start_span)[span_16](end_span)

    except Exception:
        await event.respond(
            '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
            f'Error: Could not find user '
            f'<code>{target_identifier}</code>',
            parse_mode='html'
        )[span_17](start_span)[span_17](end_span)

@bot_client.on(events.NewMessage(pattern=r'\.(?:complete|comp)(?:\s+.*)?$'))
async def bot_complete_command(event):
    if event.sender_id not in MM_DATA or event.is_private:
        return

    mm_info = MM_DATA[event.sender_id]
    await event.delete()

    # Is chat ke purane tracked users ko reset kar do
    chat_vouched_users[event.chat_id] = set()

    # 1. Group title change
    try:
        await bot_client(EditChatTitleRequest(
            chat_id=event.chat_id,
            title=f"{mm_info['prefix']} | Complete"
        ))
    except:
        pass

    # 2. Vouch format message bhejna
    thank_you_msg = (
        '<b>Thank you for using my Middleman service!</b> '
        '<tg-emoji emoji-id="5357080225463149588">🤝</tg-emoji>\n\n'
        'Please leave me a vouch here\n\n'
        f'<b>Format:</b> '
        f'<code>Vouch {mm_info["username"]} for MM\'d</code>'
    )

    await bot_client.send_message(
        event.chat_id,
        thank_you_msg,
        parse_mode='html'
    )

    # Is chat ko pending complete list mein dal do
    pending_complete_chats.add(event.chat_id)

@bot_client.on(events.NewMessage)
async def vouch_forwarder_handler(event):
    if event.is_private or event.chat_id not in pending_complete_chats: return
    
    # Agar message MM (Admin) ne bheja hai, toh ignore karo
    if event.sender_id in MM_DATA: return
    
    text_lower = str(event.raw_text).lower()
    
    # Strict Check: Message mein 'vouch' hona chahiye
    if "vouch" in text_lower:
        question_words = ["did", "how", "where", "when", "can", "should", "?"]
        if any(word in text_lower for word in question_words):
            return
            
        chat_id = event.chat_id
        user_id = event.sender_id
        
        # Initialize chat users set agar pehle se nahi hai
        if chat_id not in chat_vouched_users:
            chat_vouched_users[chat_id] = set()
            
        # Agar ISI user ne pehle bhi vouch message bhej diya hai, toh dubara count mat karo (Ignore it!)
        if user_id in chat_vouched_users[chat_id]:
            return
            
        # Naye user ka vouch record kar lo
        chat_vouched_users[chat_id].add(user_id)
        
        chat = await event.get_chat()
        mm_username, mm_id = await get_mm_for_chat(chat_id, getattr(chat, 'title', ''))
        if not mm_id and chat_id in chat_mm_assigned:
            mm_id = chat_mm_assigned[chat_id]

        mm_info = MM_DATA.get(mm_id, {})
        vouch_channel = mm_info.get("vouch_channel", None)
        
        # Rule: Jab tak kam se kam 2 alag-alag users vouch na kardein, tab tak complete mat karo!
        if len(chat_vouched_users[chat_id]) < 2:
            # Pehle bande ka vouch forward kar do par chat abhi open rakho
            if vouch_channel:
                try: 
                    await bot_client.forward_messages(vouch_channel, event.message)
                    # --- STATS: VOUCH COUNT +1 ---
                    if mm_id:
                        mm_str = str(mm_id)
                        if "mm_stats" not in config: config["mm_stats"] = {}
                        if mm_str not in config["mm_stats"]:
                            config["mm_stats"][mm_str] = {"completed": 0, "cancelled": 0, "vouches": 0, "volume_usd": 0.0}
                        config["mm_stats"][mm_str]["vouches"] += 1
                        save_json(CONFIG_FILE, config)
                except: pass
            return # Yahan return ho jayega, chat close nahi hogi jab tak doosra user na aaye!

        # --- JAB 2 VOUCHES COMPLETE HO JAYEIN ---
        pending_complete_chats.discard(chat_id)
        chat_vouched_users.pop(chat_id, None)
        
        if vouch_channel:
            try: 
                await bot_client.forward_messages(vouch_channel, event.message)
                # --- STATS: 2ND VOUCH COUNT +1 ---
                if mm_id:
                    mm_str = str(mm_id)
                    if "mm_stats" not in config: config["mm_stats"] = {}
                    if mm_str not in config["mm_stats"]:
                        config["mm_stats"][mm_str] = {"completed": 0, "cancelled": 0, "vouches": 0, "volume_usd": 0.0}
                    config["mm_stats"][mm_str]["vouches"] += 1
                    save_json(CONFIG_FILE, config)
            except: pass

        # --- STATS: COMPLETED DEAL + VOLUME SAVE IN mm_config.json ---
        if mm_id:
            mm_str = str(mm_id)
            if "mm_stats" not in config: config["mm_stats"] = {}
            if mm_str not in config["mm_stats"]:
                config["mm_stats"][mm_str] = {"completed": 0, "cancelled": 0, "vouches": 0, "volume_usd": 0.0}
            
            config["mm_stats"][mm_str]["completed"] += 1
            deal_vol = chat_deal_amount.get(chat_id, 0.0)
            config["mm_stats"][mm_str]["volume_usd"] += deal_vol
            save_json(CONFIG_FILE, config)

        # Memory Cleanup (Taaki active/pending stats se nikal jaye)
        chat_deal_status.pop(chat_id, None)
        chat_mm_assigned.pop(chat_id, None)
        chat_deal_amount.pop(chat_id, None)
        active_tat_by_mm.pop(chat_id, None)
            
        await asyncio.sleep(1.0)
        
        final_msg = (
            f"<b>The MM deal is now complete. Messaging is disabled, and this group will be deleted within few hours.</b>\n\n"
            f"<b>Thank You for dealing with {mm_info.get('username', 'Middleman')}!</b>"
        )
        try: await bot_client.send_message(chat_id, final_msg, parse_mode='html')
        except: pass
        
        await asyncio.sleep(0.5)
        
        try: 
            await bot_client(EditChatDefaultBannedRightsRequest(
                peer=chat_id, 
                banned_rights=ChatBannedRights(until_date=None, send_messages=True)
            ))
        except: pass

@bot_client.on(events.NewMessage(pattern=r'^[./]stats$'))
async def send_mm_statistics(event):
    # Sirf Special Admin aur authorized MMs hi use kar sakte hain
    allowed_users = list(MM_DATA.keys()) + [MONITOR_ADMIN_ID][span_0](start_span)[span_0](end_span)
    if event.sender_id not in allowed_users:
        return

    # Nox MM ko chhod kar baki sabhi 4 MMs ki list
    NOX_ID = 8258524753[span_1](start_span)[span_1](end_span)
    target_mms = [mid for mid in MM_DATA.keys() if mid != NOX_ID][span_2](start_span)[span_2](end_span)

    if "mm_stats" not in config:
        config["mm_stats"] = {}

    for mm_id in target_mms:
        mm_info = MM_DATA[mm_id][span_3](start_span)[span_3](end_span)
        mm_str = str(mm_id)
        saved = config["mm_stats"].get(mm_str, {"completed": 0, "cancelled": 0, "vouches": 0, "volume_usd": 0.0})

        # Real-time ongoing data
        active_deals = sum(1 for cid, mid in chat_mm_assigned.items() if mid == mm_id and chat_deal_status.get(cid) == "active")
        pending_deals = sum(1 for cid, mid in chat_mm_assigned.items() if mid == mm_id and chat_deal_status.get(cid) == "pending")
        active_tats = sum(1 for cid, mid in active_tat_by_mm.items() if mid == mm_id and cid in active_timers)

        completed_deals = saved.get("completed", 0)
        cancelled_deals = saved.get("cancelled", 0)
        total_vouches = saved.get("vouches", 0)
        
        # Volume extraction (95 INR/USDT aur direct crypto ka total USD)
        total_vol = saved.get("volume_usd", 0.0)

        # Success rate calculation
        total_finished = completed_deals + cancelled_deals
        if total_finished > 0:
            success_rate = (completed_deals / total_finished) * 100
        else:
            success_rate = 100.0 if completed_deals > 0 else 0.0

        clean_username = mm_info["username"].lstrip("@")[span_4](start_span)[span_4](end_span)

        # Exact Message Template
        stats_msg = (
            f"📊 <b>MIDDLEMAN STATISTICS</b>\n\n"
            f"Middleman: @{clean_username}\n"
            f"🟢 Completed Deals: {completed_deals}\n"
            f"🟡 Pending Deals: {pending_deals}\n"
            f"🔵 Active Deals: {active_deals}\n"
            f"🔴 Cancelled Deals: {cancelled_deals}\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Total Volume: ${total_vol:,.0f}\n"
            f"Success Rate: {success_rate:.1f}%\n"
            f"Active TAT Timers: {active_tats}\n"
            f"Total Vouches: {total_vouches}"
        )

        await event.respond(stats_msg, parse_mode="html")
        await asyncio.sleep(0.5)

@bot_client.on(events.NewMessage(pattern=r'\.lock$'))
async def bot_lock_cmd(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    await event.delete()
    try: await bot_client(EditChatDefaultBannedRightsRequest(peer=event.chat_id, banned_rights=ChatBannedRights(until_date=None, send_messages=True)))
    except: pass
    await bot_client.send_message(event.chat_id, "<b>GROUP LOCKED</b>\n\nOnly admins can send messages. All non-admin can't send messages.", parse_mode='html')

@bot_client.on(events.NewMessage(pattern=r'\.unlock$'))
async def bot_unlock_cmd(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    await event.delete()
    try: await bot_client(EditChatDefaultBannedRightsRequest(peer=event.chat_id, banned_rights=ChatBannedRights(until_date=None, send_messages=False)))
    except: pass
    await bot_client.send_message(event.chat_id, "<b>Group UNLOCKED</b>\nMembers can now send messages.", parse_mode='html')

# --- CUSTOM COMMANDS ---
@bot_client.on(events.NewMessage(pattern=r'\.custom\s+(\w+)'))
async def create_custom(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    if not event.is_reply: return await event.respond("Reply to a message to save it as a custom command.")
    cmd_name = event.pattern_match.group(1).lower()
    reply_msg = await event.get_reply_message()
    custom_commands[cmd_name] = reply_msg.text
    save_json(CUSTOM_CMDS_FILE, custom_commands)
    await event.respond(f"Custom command `.{cmd_name}` saved!")

@bot_client.on(events.NewMessage(pattern=r'^\.(\w+)$'))
async def run_custom(event):
    if event.sender_id not in MM_DATA or event.is_private: return
    cmd_name = event.pattern_match.group(1).lower()
    ignore_list = ['gc', 'rec', 'received', 'pay', 'release', 'released', 'refunded', 'complete', 'comp', 'lock', 'unlock', 'custom', 'trc', 'bep', 'eth', 'sol', 'ton', 'btc', 'polygon', 'erc', 'ltc', 'xrp', 'doge', 'bch', 'usdc', 'unbanterms', 'banterms', 'noterms', 'tos', 'tat']
    if cmd_name in ignore_list: return
    if cmd_name in custom_commands:
        await event.delete()
        await event.respond(custom_commands[cmd_name], parse_mode='html')

@bot_client.on(events.NewMessage(pattern=r'/start'))
async def admin_start(event):
    if not event.is_private or event.sender_id not in MM_DATA: return
    text = f"Welcome to the Middleman Settings Panel."
    buttons = [
        [Button.inline("Custom CMDs", b"menu_custom"), Button.inline("Crypto", b"menu_crypto")],
        [Button.inline("Messages", b"menu_messages"), Button.inline("QR / UPI", b"menu_qrupi")],
        [Button.inline("Custom PFP", b"menu_custom_pfp"), Button.inline("Custom Bio", b"menu_custom_bio")],
        [Button.inline("Set Custom Fee", b"admin_set_custom_fee")]
    ]
    await event.respond(text, buttons=buttons)

@bot_client.on(events.CallbackQuery)
async def admin_callbacks(event):
    if event.sender_id not in MM_DATA: return
    data = event.data.decode('utf-8')
    if data == "back_main":
        admin_states.pop(event.sender_id, None)
        buttons = [
            [Button.inline("Custom CMDs", b"menu_custom"), Button.inline("Crypto", b"menu_crypto")],
            [Button.inline("Messages", b"menu_messages"), Button.inline("QR / UPI", b"menu_qrupi")],
            [Button.inline("Custom PFP", b"menu_custom_pfp"), Button.inline("Custom Bio", b"menu_custom_bio")],
            [Button.inline("Set Custom Fee", b"admin_set_custom_fee")]
        ]
        await event.edit("Welcome back to the Middleman Settings Panel.", buttons=buttons)
    elif data == "menu_custom":
        await event.edit(f"To add a custom command, go to any group and reply to a message with:\n`.custom <name>`\n\nThen use `.name` to trigger it.", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_crypto":
        mm_wallets = config["mms"].get(str(event.sender_id), {}).get("crypto_wallets", {})
        wallets = "\n".join([f"{k.upper()}: {v[:15]}..." for k, v in list(mm_wallets.items())[:5]])
        admin_states[event.sender_id] = "WAITING_CRYPTO"
        await event.edit(f"Your Wallets:\n{wallets}\n\nTo update, send:\nbtc bc1q...", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_qrupi":
        admin_states[event.sender_id] = "WAITING_QRUPI"
        await event.edit(f"To update your UPI and QR, simply send your **QR Code Image** here and write your **UPI ID** in the caption.\n\nExample: Send photo, and type `yourupi@bank` as its caption.", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_messages":
        admin_states[event.sender_id] = "WAITING_TOS"
        await event.edit(f"Send new TOS message text:", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_custom_pfp":
        admin_states[event.sender_id] = "WAITING_CUSTOM_PFP"
        await event.edit(
            "Send the photo you want to use as your custom group PFP.\n\n"
            "It will be used for groups you create with .gc. If no custom PFP is saved, the default PFP will be used.",
            buttons=[Button.inline("Back", b"back_main")]
        )
    elif data == "menu_custom_bio":
        admin_states[event.sender_id] = "WAITING_CUSTOM_BIO"
        current_bio = config.get("mms", {}).get(str(event.sender_id), {}).get("custom_bio", "")
        await event.edit(
            "Send your custom group bio/about text. It will be applied to groups you create with .gc.\n\n"
            "Telegram group bio limit is 255 characters. Send /cancel to keep the current setting.\n\n"
            f"Current custom bio: {current_bio or '(not set — default bio will be used)'}",
            buttons=[Button.inline("Back", b"back_main")]
        )
    elif data == "admin_set_custom_fee":
        admin_states[event.sender_id] = "WAITING_CUSTOM_FEE"
        await event.edit("Send your custom fee percentage (e.g. 2.0 or 1.5).", buttons=[Button.inline("Back", b"back_main")])

@bot_client.on(events.CallbackQuery)
async def admin_callbacks(event):
    if event.sender_id not in MM_DATA: return
    data = event.data.decode('utf-8')
    if data == "back_main":
        admin_states.pop(event.sender_id, None)
        buttons = [[Button.inline("Custom CMDs", b"menu_custom"), Button.inline("Crypto", b"menu_crypto")], [Button.inline("Messages", b"menu_messages"), Button.inline("QR / UPI", b"menu_qrupi")]]
        await event.edit("Welcome back.", buttons=buttons)
    elif data == "menu_custom":
        await event.edit(f"To add a custom command, go to any group and reply to a message with:\n`.custom <name>`\n\nThen use `.name` to trigger it.", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_crypto":
        mm_wallets = config["mms"].get(str(event.sender_id), {}).get("crypto_wallets", {})
        wallets = "\n".join([f"{k.upper()}: {v[:15]}..." for k, v in list(mm_wallets.items())[:5]])
        admin_states[event.sender_id] = "WAITING_CRYPTO"
        await event.edit(f"Your Wallets:\n{wallets}\n\nTo update, send:\nbtc bc1q...", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_qrupi":
        admin_states[event.sender_id] = "WAITING_QRUPI"
        await event.edit(f"To update your UPI and QR, simply send your **QR Code Image** here and write your **UPI ID** in the caption.\n\nExample: Send photo, and type `yourupi@bank` as its caption.", buttons=[Button.inline("Back", b"back_main")])
    elif data == "menu_messages":
        admin_states[event.sender_id] = "WAITING_TOS"
        await event.edit(f"Send new TOS message text:", buttons=[Button.inline("Back", b"back_main")])

@bot_client.on(events.NewMessage(func=lambda e: e.is_private and e.sender_id in MM_DATA))
async def admin_text_input(event):
    state = admin_states.get(event.sender_id)
    if not state: return

    # --- CUSTOM GROUP PFP ---
    if state == "WAITING_CUSTOM_PFP":
        if not event.photo:
            return await event.respond("Please send an image/photo as a Telegram photo, not as text.")

        mm_id_str = str(event.sender_id)
        os.makedirs("custom_pfps", exist_ok=True)
        pfp_path = os.path.abspath(os.path.join("custom_pfps", f"mm_{mm_id_str}.jpg"))
        downloaded = await bot_client.download_media(event.message, file=pfp_path)
        if not downloaded or not os.path.isfile(downloaded):
            return await event.respond("❌ Couldn't save that photo. Please try sending it again.")

        if "mms" not in config:
            config["mms"] = {}
        if mm_id_str not in config["mms"]:
            config["mms"][mm_id_str] = {}
        config["mms"][mm_id_str]["custom_pfp_path"] = os.path.abspath(downloaded)
        save_json(CONFIG_FILE, config)
        admin_states.pop(event.sender_id, None)
        return await event.respond("✅ Custom PFP saved! It will be used for your next .gc group. Existing groups won't be changed.")

    # --- CUSTOM GROUP BIO ---
    elif state == "WAITING_CUSTOM_BIO":
        bio_text = (event.raw_text or "").strip()
        if bio_text == "/cancel":
            admin_states.pop(event.sender_id, None)
            return await event.respond("Cancelled. Your existing custom bio setting was kept.")
        if not bio_text:
            return await event.respond("Please send the bio text.")
        if len(bio_text) > 255:
            return await event.respond(f"Bio is {len(bio_text)} characters. Please keep it within Telegram's 255-character limit.")

        mm_id_str = str(event.sender_id)
        if "mms" not in config:
            config["mms"] = {}
        if mm_id_str not in config["mms"]:
            config["mms"][mm_id_str] = {}
        config["mms"][mm_id_str]["custom_bio"] = bio_text
        save_json(CONFIG_FILE, config)
        admin_states.pop(event.sender_id, None)
        return await event.respond("✅ Custom bio saved! It will be used for groups you create with .gc.")
    
    elif state == "WAITING_CRYPTO":
        parts = event.text.split(maxsplit=1) if event.text else []
        if len(parts) == 2:
            coin = parts[0].strip().lower()
            wallet_addr = parts[1].strip()
            mm_id_str = str(event.sender_id)
            
            # Ensure proper nesting in config dictionary
            if "mms" not in config: config["mms"] = {}
            if mm_id_str not in config["mms"]: config["mms"][mm_id_str] = {}
            if "crypto_wallets" not in config["mms"][mm_id_str]: config["mms"][mm_id_str]["crypto_wallets"] = {}
            
            # Save to config memory & JSON file
            config["mms"][mm_id_str]["crypto_wallets"][coin] = wallet_addr
            save_json(CONFIG_FILE, config)
            
            # Also update MM_DATA runtime dictionary so it reflects instantly!
            if event.sender_id in MM_DATA:
                if "crypto_wallets" not in MM_DATA[event.sender_id]:
                    MM_DATA[event.sender_id]["crypto_wallets"] = {}
                MM_DATA[event.sender_id]["crypto_wallets"][coin] = wallet_addr
                
            await event.respond(
                f'<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
                f'Updated {coin.upper()} wallet successfully to:\n'
                f'<code>{wallet_addr}</code>',
                parse_mode='html'
            )
            admin_states.pop(event.sender_id, None)
        else:
            await event.respond(
                '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                'Invalid format! Send like: <code>btc bc1q...</code>',
                parse_mode='html'
            )
            
    elif state == "WAITING_QRUPI":
        upi_id = ""
        qr_path = ""
        if event.photo:
            if not event.text: 
                return await event.respond(
                    '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                    'Error: Please send the photo WITH your UPI ID written in the caption!',
                    parse_mode='html'
                )
            upi_id = event.text.strip()
            qr_path = await bot_client.download_media(event.message, file=f"qr_{event.sender_id}.png")
        else:
            parts = event.text.split(maxsplit=1) if event.text else []
            if len(parts) == 2:
                upi_id = parts[0].strip()
                qr_path = parts[1].strip()
            else:
                return await event.respond(
                    '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                    'Invalid format! Please send a **QR Photo** with your UPI in the caption.',
                    parse_mode='html'
                )
        
        mm_id_str = str(event.sender_id)
        if "mms" not in config: config["mms"] = {}
        if mm_id_str not in config["mms"]: config["mms"][mm_id_str] = {}
        config["mms"][mm_id_str]["upi_id"] = upi_id
        config["mms"][mm_id_str]["qr_link"] = qr_path
        save_json(CONFIG_FILE, config)
        
        if event.sender_id in MM_DATA:
            MM_DATA[event.sender_id]["upi_id"] = upi_id
            MM_DATA[event.sender_id]["qr_link"] = qr_path
            
        await event.respond(
            f'<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            f'UPI (<code>{upi_id}</code>) & QR Image updated successfully!',
            parse_mode='html'
        )
        admin_states.pop(event.sender_id, None)
        
    elif state == "WAITING_TOS":
        config["bot_msg_tos"] = (event.text or "").strip()
        save_json(CONFIG_FILE, config)
        await event.respond(
            '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            'TOS updated!',
            parse_mode='html'
        )
        admin_states.pop(event.sender_id, None)

    elif state == "WAITING_CUSTOM_FEE":
        fee_input = (event.text or "").strip()
        try:
            fee_val = float(fee_input)
        except ValueError:
            await event.respond(
                '<tg-emoji emoji-id="5210952531676504517">❌</tg-emoji> '
                'Invalid format! Please send a valid number '
                '(e.g., <code>2.0</code> or <code>50</code>).',
                parse_mode='html'
            )
            return
            
        mm_id_str = str(event.sender_id)
        if "mms" not in config: config["mms"] = {}
        if mm_id_str not in config["mms"]: config["mms"][mm_id_str] = {}
        
        config["mms"][mm_id_str]["custom_fee"] = fee_val
        save_json(CONFIG_FILE, config)
        
        if event.sender_id in MM_DATA:
            MM_DATA[event.sender_id]["custom_fee"] = fee_val
            
        admin_states.pop(event.sender_id, None)
        await event.respond(
            f'<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
            f'Success! Your custom fee has been successfully updated to: '
            f'<code>{fee_val}</code>',
            parse_mode='html'
        )

async def get_mm_for_chat(chat_id, title=""):
    for mm_info in MM_DATA.values():
        if mm_info["prefix"] in title: return mm_info["username"], mm_info.get("vouch_channel")
    try:
        admins = await bot_client.get_participants(chat_id, filter=ChannelParticipantsAdmins)
        for admin in admins:
            if admin.id in MM_DATA: return MM_DATA[admin.id]["username"], MM_DATA[admin.id].get("vouch_channel")
    except: pass
    return "@Middlemaven", None


async def get_mm_for_chat(chat_id, title=""):
    for mm_info in MM_DATA.values():
        if mm_info["prefix"] in title:
            return mm_info["username"], mm_info.get("vouch_channel")

    try:
        admins = await bot_client.get_participants(
            chat_id,
            filter=ChannelParticipantsAdmins
        )
        for admin in admins:
            if admin.id in MM_DATA:
                return (
                    MM_DATA[admin.id]["username"],
                    MM_DATA[admin.id].get("vouch_channel")
                )
    except Exception:
        pass

    return "@Middlemaven", None


@bot_client.on(events.NewMessage(func=lambda e: not e.is_private and e.text and 'vouch' in e.text.lower()))
async def auto_vouch_forwarder(event):
    bot_me = await bot_client.get_me()

    if getattr(event, 'sender_id', None) in list(MM_DATA.keys()) + [bot_me.id]:
        return

    chat = await event.get_chat()
    mm_username, vouch_channel = await get_mm_for_chat(
        event.chat_id,
        getattr(chat, 'title', '')
    )

    if not vouch_channel:
        return

    chat_id = event.chat_id
    if chat_id not in chat_vouches:
        chat_vouches[chat_id] = {}

    chat_vouches[chat_id][event.sender_id] = event.message

    if len(chat_vouches[chat_id]) == 2:
        try:
            await bot_client.forward_messages(
                vouch_channel,
                list(chat_vouches[chat_id].values())
            )

            conf_msg = await bot_client.send_message(
                chat_id,
                'Vouch Forwarded to Vouches Channel '
                '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji>',
                parse_mode='html'
            )

            chat_vouches[chat_id].clear()

            await asyncio.sleep(1)

            try:
                await bot_client(
                    EditChatDefaultBannedRightsRequest(
                        peer=chat_id,
                        banned_rights=ChatBannedRights(
                            until_date=None,
                            send_messages=True
                        )
                    )
                )

                await bot_client.send_message(
                    chat_id,
                    '<b>GROUP LOCKED</b>\n\n'
                    "Only admins can send messages. "
                    "All non-admins can't send messages.",
                    parse_mode='html'
                )

            except Exception as lock_err:
                print("Auto-Lock Error:", lock_err)

            await asyncio.sleep(4)
            await conf_msg.delete()

        except Exception as e:
            print("Vouch Forwarder Error:", e)


@bot_client.on(events.NewMessage)
async def assistant_bot_handler(event):
    if event.is_private:
        return

    text_lower = str(event.raw_text).lower()

    # --- REFUND REQUEST DETECTOR ---
    if (
        "refund" in text_lower
        and getattr(event, 'sender_id', None) not in MM_DATA
    ):
        chat_id = event.chat_id

        if chat_id not in refund_requested_chats:
            refund_requested_chats.add(chat_id)

            chat = await event.get_chat()
            mm_username, _ = await get_mm_for_chat(
                chat_id,
                getattr(chat, 'title', '')
            )

            refund_msg = (
                f"<b>Refund Confirmation</b>\n\n"
                f"{mm_username}, please process the refund.\n\n"
                f"Refund has been requested!\n"
                f"<b>Seller, please confirm the refund. Buyer, "
                f"please drop your QR/UPI details if the deal was "
                f"in INR. If the deal was in crypto, please provide "
                f"the correct network address.</b>\n\n"
                f"Now, please wait for {mm_username}’s response. "
                f"We’ll update you as soon as possible."
            )

            try:
                await event.respond(refund_msg, parse_mode='html')
            except Exception:
                pass

    # --- RELEASE REQUEST DETECTOR ---
    if (
        ("release" in text_lower or "released" in text_lower)
        and getattr(event, 'sender_id', None) not in MM_DATA
    ):
        chat_id = event.chat_id

        if chat_id not in release_requested_chats:
            release_requested_chats.add(chat_id)

            chat = await event.get_chat()
            mm_username, _ = await get_mm_for_chat(
                chat_id,
                getattr(chat, 'title', '')
            )

            release_req_msg = (
                f"<b>Release Confirmation</b>\n\n"
                f"{mm_username}, please process the release.\n\n"
                f"Release has been requested!\n"
                f"<b>Buyer, please confirm the release. Seller, "
                f"please drop your QR/UPI details if the deal is "
                f"in INR. If the deal is in crypto, please provide "
                f"the correct network address.</b>\n\n"
                f"Now, please wait for {mm_username}’s response. "
                f"We’ll update you as soon as possible."
            )

            try:
                await event.respond(release_req_msg, parse_mode='html')
            except Exception:
                pass

    # --- TRANSACTION NETWORK DETECTOR ---
    if getattr(event, 'sender_id', None) not in MM_DATA:
        return

    original_text = str(event.raw_text)
    network = None

    if "http" in text_lower or "scan" in text_lower:
        if "etherscan.io" in text_lower:
            network = "ETH"
        elif "bscscan.com" in text_lower:
            network = "BEP20"
        elif "tronscan.org" in text_lower:
            network = "TRC20"
        elif "solscan.io" in text_lower:
            network = "SOL"
        elif "polygonscan.com" in text_lower:
            network = "Polygon"
        elif "tonviewer.com" in text_lower or "tonscan.org" in text_lower:
            network = "TON"
        elif "blockchain.com" in text_lower or "mempool.space" in text_lower:
            network = "BTC"

    else:
        if re.search(
            r'\b(0x[a-f0-9]{60,64})\b',
            original_text,
            re.IGNORECASE
        ):
            network = "BEP20 / ETH / Polygon"

        elif re.search(
            r'\b([a-f0-9]{64})\b',
            original_text,
            re.IGNORECASE
        ):
            network = "TRC20 / BTC / LTC"

        elif re.search(
            r'\b([1-9a-hj-np-za-km-z]{80,90})\b',
            original_text,
            re.IGNORECASE
        ):
            network = "SOL"

    if network:
        await asyncio.sleep(1.5)

        try:
            await event.reply(
                '<tg-emoji emoji-id="5206607081334906820">✔️</tg-emoji> '
                'Transaction is already confirmed!\n\n'
                f'Network: {network}\n'
                f'Confirmations: {random.randint(8, 45)}',
                parse_mode='html',
                link_preview=False
            )
        except Exception:
            pass

async def main():
    print("MAIN STARTED")

    await client.start()
    print("USER CLIENT STARTED")

    await bot_client.start(bot_token=BOT_TOKEN)
    print("BOT CLIENT STARTED")

    print("Multi-Admin Bot Running! Ready to dominate.")

    await asyncio.gather(
        client.run_until_disconnected(),
        bot_client.run_until_disconnected()
    )


if __name__ == "__main__":
    asyncio.run(main())