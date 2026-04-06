import asyncio
from main import lifespan, app, analyze_content

async def run():
    async with lifespan(app):
        try:
            res = analyze_content("President Biden announced a new infrastructure bill today in Washington. It is massive and very real.")
            print("SUCCESS")
            print(res)
        except Exception as e:
            import traceback
            traceback.print_exc()

asyncio.run(run())
