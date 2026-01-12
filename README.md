# Async Discord Token Checker

A high-performance asynchronous tool for validating Discord tokens using `aiohttp` and `asyncio`.

### Features
* **Async I/O:** Checks thousands of tokens in seconds without blocking.
* **Concurrency Control:** Uses Semaphores to respect API Rate Limits.
* **Data Extraction:** Retrieves username and phone status for valid tokens.
* **Clean Logging:** Detailed output using `loguru`.

### Tech Stack
* Python 3.10+
* aiohttp (Asynchronous HTTP Client)
* asyncio