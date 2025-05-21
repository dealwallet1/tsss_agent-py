
import sys
import asyncio

# # On Windows, switch to the ProactorEventLoop so subprocess.exec APIs work
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from tsss_agent.tsss_agent import graph

load_dotenv()
AGENT_NAME = os.environ.get("AGENT_NAME")

app = FastAPI()

copilotkitAgent = CopilotKitRemoteEndpoint(
    agents=[
        LangGraphAgent(
            name=AGENT_NAME,
            description="CS agent.",
            graph=graph,
        )
    ],
)

add_fastapi_endpoint(app, copilotkitAgent, "/cpk/lg/cs_agent")


def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "4053"))
    uvicorn.run(
        "agent_server:app",
        host="localhost",
        port=port,
        reload=True,
    )


if __name__ == "__main__":
    main()
