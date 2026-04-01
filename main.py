import asyncio
import random
import time

from aiolimiter import AsyncLimiter
from itertools import cycle
from rich.console import Console
from rich.panel import Panel

from mail_tm.client import MailTMClient
from utils.helpers import random_string, save_result
from utils.proxies import parse_proxy

console = Console()

BANNER = r"""
 █████╗ ██╗   ██╗████████╗ ██████╗ 
██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗
███████║██║   ██║   ██║   ██║   ██║
██╔══██║██║   ██║   ██║   ██║   ██║
██║  ██║╚██████╔╝   ██║   ╚██████╔╝
╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ 

        AUTO-REG MAIL.TM
"""

FOOTER = "author:\nGithub: anti.society.projectx\nLolz: 11zeroxxx11"


async def main():
    console.print(Panel(BANNER, style="bold cyan"))
    console.print(f"[bold]{FOOTER}[/bold]\n")

    proxies = parse_proxy(r"proxies.txt")
    client = MailTMClient(proxies)
    domains = await client.get_domains()
    proxy_pool = cycle(proxies)

    limiters = {proxy: AsyncLimiter(1, 2) for proxy in proxies}
    global_limiter = AsyncLimiter(5, 1)
    s = time.time()

    async def worker(retries=3):
        for attempt in range(retries):
            proxy = next(proxy_pool)
            limiter = limiters[proxy]

            username = random_string(random.randint(10, 16))
            password = random_string(random.randint(12, 24))
            email = f"{username}@{random.choice(domains)}"

            try:
                await asyncio.sleep(random.uniform(0.4, 1.0))

                async with global_limiter:
                    async with limiter:
                        await client.create_account(email, password, proxy)
                        save_result(email, password)

            except Exception as e:
                if "429" in str(e):
                    wait = (attempt + 1) * random.uniform(2, 5)
                    console.print(f"[yellow]429 → sleep {wait:.2f}s[/yellow]")
                    await asyncio.sleep(wait)
                else:
                    await asyncio.sleep(random.uniform(0.5, 1.5))

    tasks = [asyncio.create_task(worker()) for _ in range(20)]

    await asyncio.gather(*tasks, return_exceptions=True)

asyncio.run(main())
