'''
title: Concept 02
date: 2018-01-16
description:
    카카오톡 플러스친구 자동응답 API 명세: https://github.com/plusfriend/auto_reply
    기존엔 Flask app의 wrapper 형태로 구상했으나 구현이나 확장성에 어려움이 있을 것이라 생각되어
    프레임워크가 아닌 라이브러리 형태로 전환을 고려 중
    실질적으로 web app 역할을 하는 것이 아닌 router의 역할로 구상하려함
    일단 Flask와 붙여보고 있지만 Django등 다른 웹 프레임워크와 호환되게끔 구성하고자함
'''
from flask import Flask, request, jsonify
from chatterbox import Chatter, Keyboard


app = Flask(__name__)

chatter = Chatter()

# Home Keyboard 정의
home_buttons = [
    "오늘의 식단",
    "내일의 식단",
    "부가 기능",
]

# home_keyboard = Keyboard(type="text")
home_keyboard = Keyboard(type="buttons", buttons=home_buttons)

# 외부 환경에 따라 제공하는 Keyboard 가 달라질 때 where 키워드 인자를 가진 home Keyboard가 우선권을 가짐
# where 키워드 인자가 None이 아니면 default 키워드 인자는 False
# chatter.add_home(home_keyboard, where=lambda: random.random() > 0.5)
chatter.add_home(home_keyboard)

# State 관계 정의
chatter.add_rule(action=["오늘의 식단, 내일의 식단"],
                 from_state="홈",
                 to_state="식단")
chatter.add_rule(action=["아침 식단, 점심 식단", "저녁 식단"],
                 from_state="식단",
                 to_state="홈")
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


@app.route("/keyboard", methods=["GET"])
def keyboard():
    return jsonify(chatter.home())


@app.route("/message", methods=["POST"])
def message():
    return jsonify(chatter.route(request.json))


# Chatter 내부적으로 유저의 State를 기억하고 있음
# exit 혹은 block API가 호출될 때 Chatter에 올라간 유저를 업데이트 해야할까?
@app.route("/friend", methods=["POST"])
def add_friend():
    pass


@app.route("/friend/<key>", methods=["DELETE"])
def block_friend(key):
    pass


@app.route("/chat_room/<key>", methods=["DELETE"])
def exit_friend(key):
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0")
