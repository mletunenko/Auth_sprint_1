import asyncio
import json

import aio_pika
import aiohttp

from core.config import settings
from core.consts import CREATE_USER_QUEUE, DELETE_USER_QUEUE


async def process_create_message(message: aio_pika.IncomingMessage):
    try:
        message_data = json.loads(message.body.decode())
        create_user_url = f"http://{settings.auth.host}:{settings.auth.port}{settings.auth.users_path}"
        async with aiohttp.ClientSession() as session:
            await session.post(create_user_url, json=message_data)
        await message.ack()

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.nack(requeue=False)


async def process_delete_message(message: aio_pika.IncomingMessage):
    try:
        message_data = json.loads(message.body.decode())
        get_user_url = (
            f"http://{settings.auth.host}:{settings.auth.port}{settings.auth.users_path}"
            f"?email={message_data["email"]}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(get_user_url) as response:
                data = await response.json()
                if not data:
                    raise Exception(f"Пользователь с почтой {message_data["email"]} не найден")
        user_id = data[0]["id"]
        delete_user_url = f"http://{settings.auth.host}:{settings.auth.port}{settings.auth.users_path}" f"/{user_id}"
        async with aiohttp.ClientSession() as session:
            await session.delete(delete_user_url)
        await message.ack()

    except Exception as e:
        print(f"Error processing message: {e}")
        await message.nack(requeue=False)


async def consume():
    connection = await aio_pika.connect_robust(
        host=settings.rabbit.host,
        login=settings.rabbit.login,
        password=settings.rabbit.password,
    )

    async with connection:
        channel = await connection.channel()
        create_user_queue = await channel.declare_queue(CREATE_USER_QUEUE, durable=True)
        delete_user_queue = await channel.declare_queue(DELETE_USER_QUEUE, durable=True)
        await create_user_queue.consume(process_create_message, no_ack=False)
        await delete_user_queue.consume(process_delete_message, no_ack=False)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(consume())
