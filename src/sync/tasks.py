import json

from aio_pika import Message
from aio_pika.abc import AbstractChannel
from pydantic.v1 import UUID4

from core.consts import UPDATE_EMAIL_QUEUE, DELETE_RELATED_INTERACTIONS_QUEUE


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


async def delete_related_interactions_task(
    user_id: UUID4,
    rabbit_channel: AbstractChannel,
) -> None:
    body = {
        "user_id": str(user_id),
    }
    json_body = json.dumps(body)
    await rabbit_channel.default_exchange.publish(
        Message(body=json_body.encode()),
        routing_key=DELETE_RELATED_INTERACTIONS_QUEUE,
    )
