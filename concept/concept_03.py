'''
title: Concept 03
date: 2018-01-17
description:
    https://stackoverflow.com/questions/17862185/how-to-inject-variable-into-scope-with-a-decorator-in-python
    위 링크에 나온 것처럼 사용자가 정의한 handle function안에서 user_key, content가 담겨있는
    request.json 정보를 가져올까 했으나 thread safe 하지 않아 보류.
'''
from chatterbox import Chatter, Keyboard


chatter = Chatter()

home_buttons = [
    "오늘의 식단",
    "내일의 식단",
    "부가 기능",
]

home_keyboard = Keyboard(type="buttons", buttons=home_buttons)
chatter.add_home(home_keyboard)


def handle_menu(data):
    user_key = data["user_key"]
    type = data["type"]
    content = data["content"]
    logging.info(f"user_key: {user_key}, type: {type}, content: {content}")

    message = get_menu(content[:2])
    menu_buttons = ["아침 식단", "점심 식단", "저녁 식단"]

    return Message(text=message) + Keyboard(type="buttons", buttons=menu_buttons)


def handle_time_menu(data):
    chatter.logging(data)

    content = data["content"]
    message = get_time_menu(content[:2])
    return Message(text=message) + chatter.home_keyboard


# 1번 방안
from chatterbox.response import Text, Button, Photo, Keyboard

return (Text(text="안녕하세요") +
        Button(label="안녕하세요", url="...") +
        Photo(url="...", width=640, height=480) +
        Keyboard(type="buttons", buttons=["하나", "둘"]))

# 2번 방안
from chatterbox.response import Message
Message(text="안녕하세요",
        button={
            "label": "안녕하세요",
            "url": "...",
        },
        photo={
            "url": "...",
            "width": 640,
            "height": 480,
        },
        keyboard={
            "type": "buttons",
            "buttons": ["하나", "둘"],
        })

# State 관계 정의
chatter.add_rule(action=["오늘의 식단, 내일의 식단"],
                 from_state="홈",
                 to_state="식단",
                 func=handle_menu)
chatter.add_rule(action=["아침 식단, 점심 식단", "저녁 식단"],
                 from_state="식단",
                 to_state="홈",
                 func=handle_time_menu)
chatter.add_rule(action="전체 식단 보기",
                 from_state="식단",
                 to_state="홈")
chatter.add_rule(action="부가 기능",
                 from_state="홈",
                 to_state="부가기능")

# MessageButton을 반환하는 경우
chatter.add_rule(action=["식단 평가", "오늘 식단은 어땠다", "학식 사진으로 보기"],
                 from_state="부가기능",
                 to_state="부가기능")

# text 입력을 받는 경우
chatter.add_rule(action="닉네임 등록", from_state="부가기능", to_state="부가기능")

# 이미 닉네임 등록이 되어있으면 보여질 액션
chatter.add_rule(action="랭킹 확인", from_state="부가기능", to_state="부가기능")
chatter.add_rule(action="활동 내역", from_state="부가기능", to_state="부가기능")

# Default Fallback
chatter.add_rule(action="취소", from_state="*", to_state="홈")
