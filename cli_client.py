import asyncio
import httpx
import json
import sys

async def main():
    url = "http://localhost:8000/chat/stream"
    print("Welcome to MedTech Chat CLI. Type 'exit' to quit.")

    while True:
        try:
            query = input("\nYou: ")
        except EOFError:
            break

        if query.lower() in ["exit", "quit"]:
            break

        if not query.strip():
            continue

        print("AI: ", end="", flush=True)

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json={"query": query}, timeout=60.0) as response:
                    if response.status_code != 200:
                        print(f"[Error: Server returned {response.status_code}]")
                        continue

                    async for line in response.aiter_lines():
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                            if "sources" in data and data["sources"]:
                                titles = [s.get('filename', 'Unknown') for s in data['sources']]
                                print(f"\n[Sources: {', '.join(titles)}]\n", end="", flush=True)
                            elif "token" in data and data["token"]:
                                print(data["token"], end="", flush=True)
                            elif "error" in data and data["error"]:
                                print(f"\n[Error: {data['error']}]")
                        except json.JSONDecodeError:
                            pass
        except httpx.ConnectError:
             print(f"\n[Error: Could not connect to server at {url}. Is it running?]")
        except Exception as e:
            print(f"\n[Error: {e}]")

        print() # Newline at end

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting...")
