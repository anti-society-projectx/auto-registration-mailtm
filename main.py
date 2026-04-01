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


async def run_registration(total_accounts: int):
    proxies = parse_proxy("proxies.txt")
    client = MailTMClient(proxies)
    domains = await client.get_domains()
    proxy_pool = cycle(proxies)

    limiters = {proxy: AsyncLimiter(1, 2) for proxy in proxies}
    global_limiter = AsyncLimiter(5, 1)

    success = 0
    failed = 0

    lock = asyncio.Lock()

    async def worker():
        nonlocal success, failed

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

                    async with lock:
                        success += 1

        except Exception as e:
            async with lock:
                failed += 1

            if "429" in str(e):
                wait = random.uniform(2, 5)
                console.print(f"[yellow]429 → sleep {wait:.2f}s[/yellow]")
                await asyncio.sleep(wait)

    tasks = [asyncio.create_task(worker()) for _ in range(total_accounts)]
    await asyncio.gather(*tasks, return_exceptions=True)

    return success, failed


def menu():
    while True:
        console.clear()
        console.print(Panel(BANNER, style="bold cyan"))
        console.print(f"[bold]{FOOTER}[/bold]\n")

        console.print("[1] Запуск")
        console.print("[2] Выйти\n")

        choice = input("Выбор: ")

        if choice == "1":
            try:
                amount = int(input("Введите количество аккаунтов: "))
            except ValueError:
                console.print("[red]Неверный ввод[/red]")
                time.sleep(1.5)
                continue

            console.print(f"\n[cyan]Запуск регистрации {amount} аккаунтов...[/cyan]\n")

            success, failed = asyncio.run(run_registration(amount))

            console.print("\n[bold green]Готово![/bold green]")
            console.print(f"[green]Успешно:[/green] {success}")
            console.print(f"[red]Неудачно:[/red] {failed}")
            console.print(f"[cyan]Всего:[/cyan] {amount}\n")

            console.print("[1] Главное меню")
            console.print("[2] Выйти\n")

            after = input("Выбор: ")
            if after == "2":
                break

        elif choice == "2":
            break

        else:
            console.print("[red]Неверный выбор[/red]")
            time.sleep(1.5)


if __name__ == "__main__":
    menu()