import asyncio
import sys

from agent import GeminiMCPAgent


async def main():
    config_path = "config.json"

    # CLI 인자로 config 경로 지정 가능
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    agent = GeminiMCPAgent(config_path=config_path)

    try:
        await agent.connect()
        await agent.chat_loop()
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
