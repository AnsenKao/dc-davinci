from model import get_model_response
import asyncio
import os


async def main(text):
    model_reply = await get_model_response(text)
    print(model_reply)


# Run the main function
if __name__ == "__main__":
    print(f"using env: {os.environ['ASSISTANT_API']}")
    print(f"using env: {os.environ['ASSISTANT_ID']}")
    while 1:
        text = input("Your text prompt here: ")
        asyncio.run(main(text))
