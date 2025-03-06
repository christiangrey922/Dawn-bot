from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from colorama import *
from datetime import datetime
from fake_useragent import FakeUserAgent
import asyncio, json, os, pytz, uuid

wib = pytz.timezone('Asia/Jakarta')

class Dawn:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Host": "www.aeropres.in",
            "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": FakeUserAgent().random
        }
        self.extension_id = "fpdkjdnhkakefebpekbdhillbhonfjjp"
        self.proxies = []
        self.proxy_index = 0

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Dawn - BOT |  {Fore.YELLOW + Style.BRIGHT}Thanks for using our bot - Tool được phát trển bởi Xám Tool (https://t.me/xamdepin)
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_auto_proxies(self):
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt"
        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url) as response:
                    response.raise_for_status()
                    content = await response.text()
                    with open('auto_proxy.txt', 'w') as f:
                        f.write(content)

                    self.proxies = content.splitlines()
                    if not self.proxies:
                        self.log(f"{Fore.RED + Style.BRIGHT}No proxies found in the downloaded list!{Style.RESET_ALL}")
                        return
                    
                    self.log(f"{Fore.GREEN + Style.BRIGHT}Proxies successfully downloaded.{Style.RESET_ALL}")
                    self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
                    self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
                    await asyncio.sleep(3)
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            return []
        
    async def load_manual_proxy(self):
        try:
            if not os.path.exists('proxy.txt'):
                print(f"{Fore.RED + Style.BRIGHT}Proxy file 'proxy.txt' not found!{Style.RESET_ALL}")
                return

            with open('proxy.txt', "r") as f:
                proxies = f.read().splitlines()

            self.proxies = proxies
            self.log(f"{Fore.YELLOW + Style.BRIGHT}Loaded {len(self.proxies)} proxies.{Style.RESET_ALL}")
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed to load manual proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        
        return f"http://{proxies}" # Change with yours proxy schemes if your proxy not have schemes [http:// or socks5://]

    def get_next_proxy(self):
        if not self.proxies:
            self.log(f"{Fore.RED + Style.BRIGHT}No proxies available!{Style.RESET_ALL}")
            return None

        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.check_proxy_schemes(proxy)

    def load_accounts(self):
        try:
            if not os.path.exists('accounts.json'):
                self.log(f"{Fore.RED}File 'accounts.json' tidak ditemukan.{Style.RESET_ALL}")
                return

            with open('accounts.json', 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
            
    def generate_app_id(self):
        prefix = "677eb"
        app_id = prefix + uuid.uuid4().hex[len(prefix):]
        return app_id
    
    def hide_email(self, email):
        local, domain = email.split('@', 1)
        hide_local = local[:3] + '*' * 3 + local[-3:]
        return f"{hide_local}@{domain}"
    
    def hide_token(self, token):
        hide_token = token[:3] + '*' * 3 + token[-3:]
        return hide_token
        
    async def user_data(self, app_id: str, email: str, token: str, proxy=None, retries=5):
        url = f"https://www.aeropres.in/api/atom/v1/userreferral/getpoint?appid={app_id}"
        headers = {
            **self.headers,
            "Authorization": f"Berear {token}",
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 400:
                            self.log(
                                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT} {self.hide_email(email)} {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Token Is Expired {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}"
                            )
                            return
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_email(email)} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(2)
                else:
                    return None
        
    async def send_keepalive(self, app_id: str, email: str, token: str, proxy=None, retries=5):
        url = f"https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive?appid={app_id}"
        data = json.dumps({"username":email, "extensionid":self.extension_id, "numberoftabs":0, "_v":"1.1.2"})
        headers = {
            **self.headers,
            "Authorization": f"Berear {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    print(
                        f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {self.hide_email(email)} {Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT}GET ERROR.{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Retrying... {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(2)
                else:
                    return None
            
    async def question(self):
        while True:
            try:
                print("Hello everyone, This is Dawn-Account-Manager Tool, developed by Xam Tool")
                print("1. Run With Auto Proxy | Proxy share (Free)")
                print("2. Run With Manual Proxy | Dùng proxy cá nhân")
                print("3. Run Without Proxy | Không dùng proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Auto Proxy" if choose == 1 else 
                        "With Manual Proxy" if choose == 2 else 
                        "Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Selected.{Style.RESET_ALL}")
                    await asyncio.sleep(1)
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
        
    async def process_accounts(self, app_id: str, email: str, token: str, use_proxy: bool):
        hide_email = self.hide_email(email)
        ping_count = 1
        proxy = None

        if use_proxy:
            proxy = self.get_next_proxy()

        user = None
        while user is None:
            user = await self.user_data(app_id, email, token, proxy)
            if not user:
                self.log(
                    f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {hide_email} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}With Proxy {proxy}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                )
                await asyncio.sleep(1)

                if not use_proxy:
                    return
            
                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Try With The Next Proxy,{Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT} Wait... {Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )
                
                proxy = self.get_next_proxy()
                continue

            referral_point = user.get("referralPoint", {})
            reward_point = user.get("rewardPoint", {})
            commission_value = referral_point.get("commission", 0)
            total_reward_points = sum(
                value for key, value in reward_point.items()
                if "points" in key.lower() and isinstance(value, (int, float))
            )

            total_points = commission_value + total_reward_points
            self.log(
                f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {hide_email} {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}] [ Earning{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} Total {total_points:.0f} Points {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}               "
            )
            await asyncio.sleep(1)

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT}Try to Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

            while True:
                keepalive = await self.send_keepalive(app_id, email, token, proxy)
                if keepalive:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {hide_email} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT} PING {ping_count} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Status{Style.RESET_ALL}"
                        f"{Fore.GREEN + Style.BRIGHT} Keep Alive Recorded {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}With Proxy {proxy}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
                    ping_count += 1
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {hide_email} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.BLUE + Style.BRIGHT} PING {ping_count} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Status{Style.RESET_ALL}"
                        f"{Fore.YELLOW + Style.BRIGHT} Keep Alive Not Recorded {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}With Proxy {proxy}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} ]{Style.RESET_ALL}"
                    )
                    if use_proxy:
                        proxy = self.get_next_proxy()

                print(
                    f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}Wait For 3 Minutes For Next Ping...{Style.RESET_ALL}",
                    end="\r",
                    flush=True
                )
                await asyncio.sleep(180)

                user = await self.user_data(app_id, email, token, proxy)
                if user:
                    referral_point = user.get("referralPoint", {})
                    reward_point = user.get("rewardPoint", {})
                    commission_value = referral_point.get("commission", 0)
                    total_reward_points = sum(
                        value for key, value in reward_point.items()
                        if "points" in key.lower() and isinstance(value, (int, float))
                    )

                    total_points = commission_value + total_reward_points
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {hide_email} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}] [ Earning{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} Total {total_points:.0f} Points {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                "
                    )
                else:
                    self.log(
                        f"{Fore.MAGENTA + Style.BRIGHT}[ Account{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {hide_email} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Earning Data Is None {Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT}]{Style.RESET_ALL}                "
                    )
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED}No accounts loaded from 'accounts.json'.{Style.RESET_ALL}")
                return
            
            use_proxy_choice = await self.question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )
            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            if use_proxy and use_proxy_choice == 1:
                await self.load_auto_proxies()
            elif use_proxy and use_proxy_choice == 2:
                await self.load_manual_proxy()

            while True:
                tasks = []
                for account in accounts:
                    app_id = self.generate_app_id()
                    email = account['Email']
                    token = account['Token']

                    if app_id and email and token:
                        tasks.append(self.process_accounts(app_id, email, token, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(3)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Dawn()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Dawn - BOT{Style.RESET_ALL}",                                       
        )
