import json

from aio_pika import Message
from aio_pika.abc import AbstractChannel

from core.consts import UPDATE_EMAIL_QUEUE


async def update_profile_email_task(old_email: str, new_email: str, rabbit_channel: AbstractChannel):
    body = {
        "old_email": old_email,
        "new_email": new_email,
    }
    json_body = json.dumps(body)
    await rabbit_channel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key=UPDATE_EMAIL_QUEUE,
    )
