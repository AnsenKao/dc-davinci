# model/model.py

import json
import httpx
from openai import AsyncOpenAI
from config import Settings

settings = Settings()

ASSISTANT_API = settings.assistant_api
API_KEY = settings.api_key
ASSISTANT_ID = settings.assistant_id


async def get_model_response(user_prompt):
    http_client = httpx.AsyncClient(verify=False)
    client = AsyncOpenAI(
        base_url=ASSISTANT_API, api_key=API_KEY, http_client=http_client
    )

    thread = await client.beta.threads.create()

    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_prompt,
    )

    stream = await client.beta.threads.runs.create(
        assistant_id=ASSISTANT_ID,
        thread_id=thread.id,
        stream=True,
    )
    requires_action_run_id = ""
    complete_response = ""
    async for event in stream:
        if event.event == "thread.message.delta":
            # 解析並組合回應
            delta_content = event.data.delta.content
            for block in delta_content:
                if block.type == "text":
                    complete_response += block.text.value
        elif event.event == "thread.run.requires_action":
            requires_action_run_id = event.data.id

    if requires_action_run_id != "":
        run = await client.beta.threads.runs.retrieve(
            requires_action_run_id, thread_id=thread.id
        )
        outputs = []
        for call in run.required_action.submit_tool_outputs.tool_calls:
            print(
                f"call plugin {call.function.name} with args: {call.function.arguments}"
            )
            resp = await client._client.post(
                ASSISTANT_API + "/pluginapi",
                params={
                    "tid": thread.id,
                    "aid": ASSISTANT_ID,
                    "pid": call.function.name,
                },
                headers={"Authorization": "Bearer " + API_KEY},
                json=json.loads(call.function.arguments),
                timeout=30,
            )
            result = resp.text[:8000]
            print(f"plugin {call.function.name} result {result}")
            outputs.append({"tool_call_id": call.id, "output": result})
        stream = await client.beta.threads.runs.submit_tool_outputs(
            run_id=run.id,
            stream=True,
            thread_id=thread.id,
            tool_outputs=outputs,
        )
        async for event in stream:
            if event.event == "thread.message.delta":
                # 解析並組合回應
                delta_content = event.data.delta.content
                for block in delta_content:
                    if block.type == "text":
                        complete_response += block.text.value
                # print(event)
            elif event.event == "thread.run.completed":
                print("Run completed")
                break

    await client.beta.threads.delete(thread_id=thread.id)
    return complete_response
