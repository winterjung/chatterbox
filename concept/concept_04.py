'''
title: Concept 04
date: 2018-01-18
description:
    handle function에서 request.json을 더 예쁘게 받아오는 법
    chatterbox.response에서 1번 방안 2번 방안 모두 구현해 두는걸로
    Keyboard의 default를 buttons type으로 고정. 인자를 List만 받아도 되게끔
    shared value에 대한 고민. app을 gunicorn으로 띄우면 redis를 사용할 수 밖에 없음
'''
from chatterbox import Chatter
from chatterbox.response import Text, Button, Photo, Keyboard


chatter = Chatter()


home_buttons = [
    "오늘의 식단",
    "내일의 식단",
    "부가 기능",
]

# 1번
home_keyboard = Keyboard(home_buttons)
chatter.add_home(home_keyboard)

# 2번
chatter.add_home_keyboard(home_buttons)

# 3번 (개인적으로 이게 제일 pythonic하게 보임)
# @property를 이용해 setter에서 Keyboard로 생성해 set하기
chatter.home_keyboard = home_buttons


def handle_menu(data):
    content = data["content"]
    message = get_menu(content[:2])
    buttons = ["아침 식단", "점심 식단", "저녁 식단", "취소"]

    return Text(message) + Keyboard(buttons)


def handle_time_menu(data):
    # 로깅까지 구현하는건 chatterbox의 범위를 벗어남
    # chatter.logging(data)

    content = data["content"]
    message = get_time_menu(content[:2])
    # 혹은 Keyboard(home_buttons)
    return Text(message) + chatter.home_keyboard


def util_button(user_key):
    buttons = ["식단 평가", "오늘 식단은 어땠다", "학식 사진으로 보기"]

    if is_registered(user_key):
        buttons += ["랭킹 확인", "활동 내역"]
    else:
        buttons += ["닉네임 등록"]
    buttons += ["취소"]
    return buttons


def entry_util(data):
    user_key = data["user_key"]

    if is_registered(user_key):
        user_name = get_user_name(user_key)
        message = f"안녕하세요 {user_name}님!"
    else:
        message = "닉네임을 등록해보세요!"

    buttons = util_button(user_key)
    return Text(message) + Keyboard(buttons)


def get_url(content):
    mapping = {
        "식단 평가": "https://a.com",
        "오늘 식단은 어땠다": "https://b.com",
        "학식 사진으로 보기": "https://c.com",
    }
    return mapping[content]


def go_to_web(data):
    # 이런 식의 unpack은 어떨까
    # user_key, _, content = data
    user_key = data["user_key"]
    content = data["content"]
    message = f"{content} 기능을 사용하시려면 아래 버튼을 눌러주세요"
    buttons = util_button(user_key)
    url = get_url(content)
    return (Text(message) +
            Button(label="웹으로 이동", url=url) +
            Keyboard(buttons))


# State 관계 정의
# State를 관리할 때 제일 중요한건 user_key의 이전 State를 기록하고 갱신하는 것
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
                 to_state="홈",
                 func=...)
chatter.add_rule(action="부가 기능",
                 from_state="홈",
                 to_state="부가기능",
                 func=entry_util)

# MessageButton을 반환하는 경우
chatter.add_rule(action=["식단 평가", "오늘 식단은 어땠다", "학식 사진으로 보기"],
                 from_state="부가기능",
                 to_state="부가기능",
                 func=go_to_web)


# text 입력을 받는 경우
# 입력을 받을 경우 이전 state를 어떻게 참조해야할까?
# -> from과 to 사이에 위치한 임시 state 사용
# to_state를 input state로 설정한다음 내부적으로 action이름을 가진 state로 설정
# 이러면 "닉네임 등록"이 들어올 때 처리할 function과 text input을 처리할 function
# 2개의 handle function이 필요함. yield로 처리할 수 없을까?
# -> 가능할 것 같다.
# text input에서 text input으로 이어질 수 있을까?
# -> 가능하다. context내 반복 input이면 하나의 handle function 내부에서 yield하고
#    context가 달라질 땐 다른 state라고 판단하면 된다.
# state가 "부가기능", "닉네임 등록" 중 인 상태에서 text input으로 "닉네임 등록"이 들어오면?
# -> chatterbox 내부에서 hidden_state로 text input중임을 기억해야함
#    StopIteration이 발생했을 때 to_state로 이동하게끔

# 1번
def handle_nickname_input(data):
    message = "닉네임을 입력해 주세요."

    # 1.1번
    data = yield Text(message) + Keyboard(type="text")
    content = data["content"]

    while not is_valid_nickname(content):
        message = "제대로 입력해주세요."
        data = yield Text(message) + Keyboard(type="text")
        content = data["content"]

    # 1.2번
    while True:
        data = yield Text(message) + Keyboard(type="text")
        content = data["content"]
        if is_valid_nickname(content):
            break
        message = "제대로 입력해주세요."

    user_key = data["user_key"]
    register(user_key, content)
    message = "성공적으로 등록되었습니다."
    buttons = util_button(user_key)

    return Text(message) + Keyboard(buttons)


chatter.add_rule(action="닉네임 등록",
                 from_state="부가기능",
                 to_state="부가기능",
                 func=handle_nickname_input)


# 2번
# 함수가 2개로 분리되어 더 명확해 보이긴 하나 동일한 state를 유지한 채
# text input을 다시 받는 경우를 처리하기 힘듦
def input_nickname(data):
    message = "닉네임을 입력해 주세요."
    return Text(message) + Keyboard(type="text")


def handle_nickname_input(data):
    user_key = data["user_key"]
    content = data["content"]
    if is_valid_nickname(content):
        # 이걸 어떻게 처리해야할까?
        message = "제대로 입력해주세요."
        # 이 플래그가 False면 hidden state가 변하지 않음
        # 다음 번 text input을 다시 handle function에서 처리 가능
        # 1번
        # user_key에 대해서만 False여야 하는데 이를 어떻게 구현할까
        chatter.is_enable_transition(user_key, False)

        # 2번
        # 단순 getter라 user_key에 따른 대응이 어려움
        chatter.enable_transition = False
        # 다음과 같은 방법을 써야하는데 우아하지 않음
        chatter.enable_transition[user_key] = False
        chatter.enable_transition = (user_key, False)
        return Text(message) + Keyboard(type="text")

    if chatter.is_enable_transition(user_key):
        chatter.is_enable_transition(user_key, True)

    register(user_key, content)
    message = "성공적으로 등록되었습니다."
    buttons = util_button(user_key)

    return Text(message) + Keyboard(buttons)


chatter.add_rule(action="닉네임 등록",
                 from_state="부가기능",
                 to_state="닉네임 입력",
                 func=input_nickname)
chatter.add_rule(action="*",
                 from_state="닉네임 입력",
                 to_state="부가기능",
                 func=handle_nickname_input)

# 이미 닉네임 등록이 되어있으면 보여질 액션
chatter.add_rule(action="랭킹 확인", from_state="부가기능", to_state="부가기능")
chatter.add_rule(action="활동 내역", from_state="부가기능", to_state="부가기능")


def go_to_home(data):
    message = "취소하셨습니다."
    return Text(message) + Keyboard(home_buttons)


# Default Fallback
chatter.add_rule(action="취소", from_state="*", to_state="홈", func=go_to_home)
