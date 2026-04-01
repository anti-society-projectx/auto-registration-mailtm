import httpx


class MailTMClient:
    def __init__(self, proxies: list[str]):
        self.base_url = "https://api.mail.tm"
        self.clients = {
            proxy: httpx.AsyncClient(
                base_url=self.base_url,
                timeout=10.0,
                proxy=proxy,
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
                }
            )
            for proxy in proxies
        }

    async def close(self):
        for client in self.clients.values():
            await client.aclose()

    async def get_domains(self):
        domains: list[str] = []
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as client:
            resp = await client.get("/domains", params={"page": 1})
            resp.raise_for_status()

            data = resp.json()

            for domain in data.get("hydra:member", []):
                if domain.get("isActive"):
                    domains.append(domain.get("domain"))

        return domains

    async def create_account(self, username: str, password: str, proxy: str):
        client = self.clients[proxy]

        payload = {"address": username, "password": password}

        resp = await client.post("/accounts", json=payload)
        resp.raise_for_status()

        return f"{username}:{password}"
