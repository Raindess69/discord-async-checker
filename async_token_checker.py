import asyncio
import aiohttp
from sys import stderr
from loguru import logger

# Настройка логера
logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{message}</level>")

class DiscordTokenChecker:
    def __init__(self, filename: str):
        self.filename = filename
        self.valid_tokens = []
        self.locked_tokens = []
        self.api_url = "https://discord.com/api/v9/users/@me"

    def load_tokens(self):
        """Загрузка токенов из файла"""
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logger.error(f"Файл {self.filename} не найден!")
            return []

    async def check_token(self, session: aiohttp.ClientSession, token: str):
        """Асинхронная проверка одного токена"""
        headers = {
            "Authorization": token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            async with session.get(self.api_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    username = f"{data['username']}#{data['discriminator']}"
                    phone = data.get('phone', 'No Phone')
                    logger.success(f"Valid: {username} | Phone: {phone}")
                    self.valid_tokens.append(token)
                elif response.status == 401 or response.status == 403:
                    logger.warning(f"Invalid/Locked: {token[:25]}...")
                    self.locked_tokens.append(token)
                elif response.status == 429:
                    logger.error("Rate Limit! Слишком быстро.")
                else:
                    logger.info(f"Unknown Status {response.status}: {token[:25]}...")
        except Exception as e:
            logger.error(f"Ошибка соединения: {e}")

    async def run(self):
        tokens = self.load_tokens()
        if not tokens:
            return

        logger.info(f"Загружено токенов: {len(tokens)}. Начинаем асинхронную проверку...")

        # Семафор ограничивает количество одновременных запросов (чтобы Дискорд не забанил IP)
        semaphore = asyncio.Semaphore(50) 

        async with aiohttp.ClientSession() as session:
            tasks = []
            for token in tokens:
                async def bound_check(t):
                    async with semaphore:
                        await self.check_token(session, t)
                tasks.append(bound_check(token))
            
            # Запускаем все проверки одновременно
            await asyncio.gather(*tasks)

        self.save_results()

    def save_results(self):
        """Сохранение результатов"""
        with open('valid.txt', 'w') as f:
            f.write('\n'.join(self.valid_tokens))
        logger.info(f"Проверка завершена. Валид: {len(self.valid_tokens)}, Невалид: {len(self.locked_tokens)}")

if __name__ == "__main__":
    checker = DiscordTokenChecker("tokens.txt")
    asyncio.run(checker.run())