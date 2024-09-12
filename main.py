import requests
import urllib.parse
from fake_useragent import UserAgent
import json
import os
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tải các biến môi trường từ tệp
load_dotenv()
# Nhận mã thông báo bot Telegram và ID trò chuyện từ các biến môi trường
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Khởi tạo bot Telegram
app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def send_telegram_message(message):
    await app.bot.send_message(chat_id=CHAT_ID, text=message)

def extract_username(authorization):
    try:
        parsed_data = urllib.parse.parse_qs(authorization)
        user_data_json = parsed_data.get('user', [''])[0]
        user_data = json.loads(urllib.parse.unquote(user_data_json))
        username = user_data.get('username', 'unknown')
        return username
    except (json.JSONDecodeError, KeyError):
        return 'unknown'

def load_authorizations_with_usernames(file_path):
    with open(file_path, 'r') as file:
        authorizations = file.readlines()
    auth_with_usernames = [{'authorization': auth.strip(), 'username': extract_username(auth)} for auth in authorizations]
    return auth_with_usernames

async def claim_tasks(authorization, account_number, username):
    ua = UserAgent()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Authorization': authorization.strip(),
        'Origin': 'https://telegram.agent301.org',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    url_get_tasks = 'https://api.agent301.org/getTasks'

    # Gửi yêu cầu POST để lấy nhiệm vụ
    logger.info(f"Sending request to get tasks for account #{account_number} ({username})")
    response = requests.post(url_get_tasks, headers=headers)
    logger.debug(f"Request headers: {headers}")
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response body: {response.text}")

    if response.status_code == 200:
        json_response = response.json()
        if json_response.get("ok"):
            tasks = json_response.get("result", {}).get("data", [])
            message = f"#Tài khoản {username} | Đang thực hiện nhiệm vụ tự động...\n"
            print(message)
            await send_telegram_message(message)
            for task in tasks:
                task_type = task.get("type")
                title = task.get("title")
                reward = task.get("reward", 0)
                is_claimed = task.get("is_claimed")
                count = task.get("count", 0)
                max_count = task.get("max_count", 0)
                if not is_claimed and (task_type in ["video", "transaction", "story"]) and count < max_count:
                    while count < max_count:
                        print(f"#Nhiệm vụ {task_type} - {title} Tiến triển: {count}/{max_count}")
                        if await claim_task(headers, task_type, title):
                            count += 1
                        else:
                            break
                elif task_type in ["folder", "pigs_open", "pigs_join", "owls_open", "owls_join", "memefi", "invite_3_friends", "subscribe", "boost", "x", "youtube", "major", "booms", "bird", "onexbit", "galacoin_open", "galacoin_join", "tu_airdrop", "click_app", "empiregame_join", "timegame"]:
                    if not is_claimed:
                        await claim_task(headers, task_type, title)
            print("\nTẤT CẢ NHIỆM VỤ HOÀN THÀNH!")
        else:
            error_message = "KHÔNG THỂ NHẬN NHIỆM VỤ. LẶP LẠI VÁCH."
            print(error_message)
            await send_telegram_message(error_message)
    else:
        http_error_message = f"# Lỗi HTTP: {response.status_code}"
        print(http_error_message)
        await send_telegram_message(http_error_message)

async def claim_task(headers, task_type, title):
    url_complete_task = 'https://api.agent301.org/completeTask'
    claim_data = {"type": task_type}
    logger.info(f"Sending request to complete task: {task_type} - {title}")
    response = requests.post(url_complete_task, headers=headers, json=claim_data)
    logger.debug(f"Request headers: {headers}")
    logger.debug(f"Request payload: {claim_data}")
    logger.debug(f"Response status code: {response.status_code}")
    logger.debug(f"Response body: {response.text}")

    if response.status_code == 200 and response.json().get("ok"):
        result = response.json().get("result", {})
        task_reward = result.get("reward", 0)
        balance = result.get("balance", 0)
        task_message = f"#NHIỆM VỤ {task_type} - {title} - PHẦN THƯỞNG {task_reward} AP - Số dư: {balance} AP"
        print(task_message)
        return True
    else:
        task_fail_message = f"#NHIỆM VỤ {task_type} - {title} -YÊU CẦU GAGAL!"
        print(task_fail_message)
        await send_telegram_message(task_fail_message)
        return False

async def main():
    auth_data = load_authorizations_with_usernames('query.txt')

    while True:
        for account_number, data in enumerate(auth_data, start=1):
            authorization = data['authorization']
            username = data['username']
            account_message = f"\n------------------------------------\n  ## Tài khoản #{account_number}-{username} ##\n------------------------------------"
            print(account_message)
            await send_telegram_message(account_message)

            await claim_tasks(authorization, account_number, username)

        loop_message = "TỰ ĐỘNG SAU 6 GIỜ..."
        print(loop_message)
        await send_telegram_message(loop_message)
        await asyncio.sleep(21600)  # Chờ 6 giờ (21600 giây)

if __name__ == "__main__":
    asyncio.run(main())
