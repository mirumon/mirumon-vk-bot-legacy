from typing import Dict, List, Union, cast

import requests
import vk
from fastapi import FastAPI, HTTPException
from starlette.responses import PlainTextResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from app import config, resources
from app.schemas.computer import Commands, Computer
from app.schemas.messages import Message, MessageType, Registration

app = FastAPI(title="Mirumon VK Bot", version=config.BOT_VERSION, debug=config.DEBUG)
session = vk.Session()
api = vk.API(session, v=config.API_VERSION)


def get_computers_list() -> List[Computer]:
    response = requests.get(f"{config.SERVER_URL}/computers")
    if response.status_code != HTTP_200_OK:
        raise RuntimeError("Server bad response")
    return [Computer(**current) for current in response.json()]


def group_computers_by_domain(computers: List[Computer]) -> Dict[str, List[Computer]]:
    computer_group: Dict[str, List[Computer]] = {}
    for computer in computers:
        if computer.domain in computer_group:
            computer_group[computer.domain].append(computer)
        else:
            computer_group[computer.domain] = [computer]
    return computer_group


def process_registration(event: Registration) -> bool:
    return event.group_id == config.GROUP_ID


@app.post("/callback", response_class=PlainTextResponse)
def vk_callback(event: Union[Message, Registration]) -> str:
    if event.type == MessageType.confirmation:
        if process_registration(cast(Registration, event)):
            return config.CONFIRMATION_TOKEN

    if event.type != MessageType.message_new:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=resources.EVENT_ERROR_TEXT
        )

    event = cast(Message, event)
    user_id = event.object.from_id

    if event.object.text != Commands.computer_list:
        return MessageType.message_result

    try:
        computers = get_computers_list()
    except RuntimeError:
        api.messages.send(
            access_token=config.TOKEN,
            user_id=user_id,
            random_id="",
            message=resources.COMPUTERS_LIST_FAILED_TEXT,
        )
        return MessageType.message_result
    if computers:
        computers_group = group_computers_by_domain(computers)
        text = resources.COMPUTERS_LIST_TEMPLATE.render(computers_group=computers_group)
    else:
        text = resources.COMPUTERS_LIST_EMPTY_TEXT
    api.messages.send(
        access_token=config.TOKEN, user_id=user_id, random_id="", message=text
    )
    return MessageType.message_result
