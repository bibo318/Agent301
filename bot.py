import requests
import urllib.parse
from fake_useragent import UserAgent
import time
import json
from colorama import Fore, init
from art import text2art
import os
from datetime import datetime

init(autoreset=True)

def print_banner():
    banner = text2art("bibo318", font='standard')
    print(Fore.LIGHTCYAN_EX + banner)
    print(Fore.LIGHTYELLOW_EX + "Đừng quên ngồi uống cà phê!")
    print()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def extract_username(authorization):
    try:
        parsed_data = urllib.parse.parse_qs(authorization)
        user_data_json = parsed_data.get('user', [''])[0]

        user_data = json.loads(urllib.parse.unquote(user_data_json))

        username = user_data.get('username', 'Not found')
        return username
    except (json.JSONDecodeError, KeyError):
        return 'Not found'

def load_authorizations_with_usernames(file_path):
    with open(file_path, 'r') as file:
        authorizations = file.readlines()

    auth_with_usernames = [{'authorization': auth.strip(), 'username': extract_username(auth)} for auth in
                           authorizations]
    return auth_with_usernames

def claim_tasks(authorization, username):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'authorization': authorization.strip(),
        'origin': 'https://telegram.agent301.org',
        'accept-language': 'en-US,en;q=0.9'
    }

    url_get_tasks = 'https://api.agent301.org/getMe'
    try:
        response = requests.post(url_get_tasks, headers=headers)
        response.raise_for_status()
        json_response = response.json()

        if json_response.get("ok"):
            result = json_response.get("result", {})
            balance = result.get("balance", 0)
            print(f"{Fore.LIGHTCYAN_EX}Name: {Fore.LIGHTGREEN_EX}{username} {Fore.LIGHTCYAN_EX}Số dư: {Fore.LIGHTGREEN_EX}{balance} AP")
            print(f"{Fore.LIGHTYELLOW_EX}Xử lý các tác vụ tự động...\n")

            # Print claim time
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{Fore.LIGHTCYAN_EX}Thời gian yêu cầu: {Fore.LIGHTGREEN_EX}{current_time}")

            tasks = result.get("tasks", [])
            print(f"\n{Fore.LIGHTYELLOW_EX}------------------------------------")
            print(Fore.LIGHTCYAN_EX + "• Yêu cầu nhiệm vụ •\n")  # Tiêu đề cho nhiệm vụ
            print(f"\n{Fore.LIGHTYELLOW_EX}------------------------------------")

            for task in tasks:
                task_type = task.get("type")
                title = task.get("title")
                reward = task.get("reward", 0)
                is_claimed = task.get("is_claimed")
                count = task.get("count", 0)
                max_count = task.get("max_count")

                if max_count is None and not is_claimed:
                    print(f"{Fore.LIGHTBLUE_EX}Yêu cầu nhiệm vụ: {title}")
                    claim_task(headers, task_type, title)

                elif task_type == "video" and count < max_count:
                    while count < max_count:
                        print(f"{Fore.LIGHTBLUE_EX}Đang xác nhận nhiệm vụ: {title} Tiến trình: {count}/{max_count}")
                        if claim_task(headers, task_type, title):
                            count += 1
                        else:
                            break

                elif not is_claimed and count >= max_count:
                    print(f"{Fore.LIGHTBLUE_EX} • Đang xác nhận nhiệm vụ • {title}")
                    claim_task(headers, task_type, title)

            print(f"{Fore.LIGHTRED_EX} ✔ Tất cả các nhiệm vụ được yêu cầu")
            return balance

        else:
            print(f"{Fore.LIGHTRED_EX}Không thể yêu cầu nhiệm vụ. Thử lại.")
    except requests.RequestException as e:
        print(f"{Fore.LIGHTRED_EX}Yêu cầu không thành công: {e}")
    return 0

def claim_task(headers, task_type, title):
    url_complete_task = 'https://api.agent301.org/completeTask'
    claim_data = {"type": task_type}
    try:
        response = requests.post(url_complete_task, headers=headers, json=claim_data)
        response.raise_for_status()
        if response.json().get("ok"):
            result = response.json().get("result", {})
            task_reward = result.get("reward", 0)
            balance = result.get("balance", 0)
            print(f"{Fore.LIGHTYELLOW_EX}Nhiệm vụ {task_type} -{title} -Phần thưởng AP {Fore.LIGHTGREEN_EX}{task_reward} -Số dư hiện tại: {Fore.LIGHTGREEN_EX}{balance} AP")
            return True
        else:
            print(f"{Fore.LIGHTRED_EX}Nhiệm vụ {task_type} -{title} -Không thể hoàn thành!")
            return False
    except requests.RequestException as e:
        print(f"{Fore.LIGHTRED_EX}Yêu cầu không thành công: {e}")
        return False

def claim_wheel(authorization, username):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'authorization': authorization.strip(),
        'origin': 'https://telegram.agent301.org',
        'accept-language': 'en-US,en;q=0.9'
    }

    url_get_tasks = 'https://api.agent301.org/getMe'
    try:
        response = requests.post(url_get_tasks, headers=headers)
        response.raise_for_status()
        json_response = response.json()

        reward_mapping = {
            'tc4': '4 TON',
            'c1000': '1,000 AP',
            't1': '1 ticket',
            'nt1': '1 NOT',
            'nt5': '5 NOT',
            't3': '3 tickets',
            'tc1': '0.01 TON',
            'c10000': '10,000 AP'
        }

        if json_response.get("ok"):
            result = json_response.get("result", {})
            tickets = result.get("tickets", 0)
            print(f"{Fore.LIGHTCYAN_EX}Tài khoản {Fore.LIGHTGREEN_EX}{username} {Fore.LIGHTCYAN_EX}Số dư vé: {Fore.LIGHTGREEN_EX}{tickets}")

            if tickets > 0:
                print(f"\n{Fore.LIGHTYELLOW_EX}------------------------------------")
                print(Fore.LIGHTCYAN_EX + "• Quay bánh xe may mắn •\n") # Tiêu đề cho bánh xe quay
                print(f"\n{Fore.LIGHTYELLOW_EX}------------------------------------")
            else:
                print(f"{Fore.LIGHTRED_EX}No tickets\n")
                return

            while tickets > 0:
                responsew = requests.post('https://api.agent301.org/wheel/spin', headers=headers)
                if responsew.status_code == 200:
                    try:
                        json_responsew = responsew.json()
                        resultw = json_responsew.get("result", {})
                        reward_code = resultw.get("reward", '')
                        reward = reward_mapping.get(reward_code, reward_code)
                        print(f'{Fore.LIGHTYELLOW_EX}Thắng: {Fore.LIGHTGREEN_EX}{reward}')
                    except json.JSONDecodeError:
                        print(f"{Fore.LIGHTRED_EX}Lỗi: Phản hồi của máy chủ không phải là JSON hợp lệ.")
                        print(f"{Fore.LIGHTRED_EX}Phản hồi của máy chủ: {responsew.text}")
                        break
                else:
                    print(f"{Fore.LIGHTRED_EX}Lỗi quay bánh xe: {responsew.status_code}")
                    print(f"{Fore.LIGHTRED_EX}Phản hồi của máy chủ: {responsew.text}")
                    break

                response = requests.post(url_get_tasks, headers=headers)
                if response.status_code == 200:
                    json_response = response.json()
                    if json_response.get("ok"):
                        result = json_response.get("result", {})
                        tickets = result.get("tickets", 0)
                    else:
                        print(f"{Fore.LIGHTRED_EX}Không thể cập nhật số lượng vé. Vui lòng thử lại.")
                        break
                else:
                    print(f"{Fore.LIGHTRED_EX}Lỗi khi cập nhật số lượng vé: {response.status_code}")
                    break

            print(f"{Fore.LIGHTRED_EX} ✔ Quay xong!") # Đã thêm tin nhắn
        else:
            print(f"{Fore.LIGHTRED_EX}Không thể nhận được nhiệm vụ. Vui lòng thử lại.")
    except requests.RequestException as e:
        print(f"{Fore.LIGHTRED_EX}Yêu cầu không thành công: {e}")

def countdown_timer(seconds):
    rgb_colors = [Fore.RED, Fore.GREEN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
    color_index = 0

    while seconds:
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        timer = f'{hours:02}:{mins:02}:{secs:02}'
        
        # Countdown in RGB colors
        print(Fore.LIGHTGREEN_EX + 'Chờ: ' + rgb_colors[color_index % len(rgb_colors)] + f'{timer}', end='\r')

        time.sleep(1)
        seconds -= 1
        color_index += 1

    print(Fore.LIGHTGREEN_EX + 'Chờ: 00:00:00')

def main():
    print_banner()
    print(Fore.LIGHTCYAN_EX + "Chọn một tùy chọn:")
    print(Fore.LIGHTGREEN_EX + "1. Yêu cầu nhiệm vụ")
    print(Fore.LIGHTGREEN_EX + "2. Quay bánh xe")
    print(Fore.LIGHTGREEN_EX + "3. Yêu cầu tất cả")
    choice = input(Fore.LIGHTMAGENTA_EX + "Nhập lựa chọn của bạn: ")

    auth_data = load_authorizations_with_usernames('query.txt')
    total_balance = 0

    while True:
        for account_number, data in enumerate(auth_data, start=1):
            authorization = data['authorization']
            username = data['username']

            print(f"\n{Fore.LIGHTYELLOW_EX}------------------------------------")
            print(f"{Fore.LIGHTYELLOW_EX}Tài khoản {Fore.LIGHTWHITE_EX}#{account_number}")
            print(f"{Fore.LIGHTYELLOW_EX}------------------------------------")

            if choice == '1':
                total_balance += claim_tasks(authorization, username)
            elif choice == '2':
                claim_wheel(authorization, username)
            elif choice == '3':
                total_balance += claim_tasks(authorization, username)
                claim_wheel(authorization, username)

        print(f"{Fore.LIGHTWHITE_EX}Hoàn thành!")
        print(f"{Fore.LIGHTYELLOW_EX}Tổng số dư: {Fore.LIGHTWHITE_EX}{total_balance} AP")
        countdown_timer(28800)  # Đợi 8 giờ

if __name__ == "__main__":
    main()
