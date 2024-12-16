import asyncio
import anthropic
import pytest

# Configure the client to use our proxy instead of the actual Anthropic API
client = anthropic.AsyncClient(
    api_key="dummy-key",  # The proxy will replace this with the actual key
    base_url="http://localhost:3000"
)


@pytest.mark.asyncio
async def test_normal_message():
    """Test a normal (non-streaming) message response"""
    response = await client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "say exactly 'Hello, world!'"
            }
        ]
    )

    print(response)

    assert response.content[0].text == "Hello, world!"


@pytest.mark.asyncio
# @pytest.mark.parametrize('_', range(100))
async def test_streaming_message(_):
    """Test a streaming message response"""
    stream = await client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "say exactly 'Hello, world!'"
            }
        ],
        stream=True
    )

    message_started = False
    collected_content = []

    async for event in stream:
        print("Event:", event.type)  # Debug print

        if event.type == "message_start":
            message_started = True
        elif event.type == "content_block_delta":
            collected_content.append(event.delta.text)
        elif event.type == "message_stop":
            break

    print("Total events:", len(collected_content))

    assert message_started, "Message should start with message_start event"
    full_response = "".join(collected_content)
    print("Full response:", full_response)
    assert full_response == "Hello, world!"


if __name__ == "__main__":
    asyncio.run(test_normal_message())
    asyncio.run(test_streaming_message())
