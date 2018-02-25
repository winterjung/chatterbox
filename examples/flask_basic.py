from flask import Flask, request, jsonify
from chatterbox import Chatter, Text, Keyboard, Photo, MessageButton, Message


app = Flask(__name__)
chatter = Chatter()


@chatter.base(name='홈')
def home_keyboard():
    home_buttons = ['자기소개', '사이트로 이동하기']
    return Keyboard(home_buttons)


@chatter.rule(action='자기소개', src='홈', dest='소개')
def intro(data):
    message = '안녕하세요! 무엇을 도와드릴까요?'
    buttons = ['오늘의 날씨', '취소']
    return Text(message) + Keyboard(buttons)


@chatter.rule(action='오늘의 날씨', src='소개', dest='홈')
def weather(data):
    text = Text('오늘은 하루종일 맑겠습니다.')
    sunny_image_url = 'https://www.python.org/static/img/python-logo.png'
    photo = Photo(url=sunny_image_url, width=600, height=401)
    keyboard = chatter.home()
    return text + photo + keyboard


@chatter.rule(action='사이트로 이동하기', src='홈', dest='홈')
def web(data):
    text = Text('자세한 정보를 보고싶으면 사이트로 이동해주세요!')
    msg_button = MessageButton(label='이동하기',
                               url='https://github.com/jungwinter/chatterbox')
    keyboard = chatter.home()
    return Message(text=text, message_button=msg_button) + keyboard


@chatter.rule(action='취소', src='*', dest='홈')
def cancel(data):
    message = '취소하셨습니다.'
    return Text(message) + chatter.home()


@app.route('/keyboard', methods=['GET'])
def keyboard():
    return jsonify(chatter.home())


@app.route('/message', methods=['POST'])
def message():
    return jsonify(chatter.route(request.json))


@app.route('/friend', methods=['POST'])
def add_friend():
    return jsonify({'message': 'SUCCESS'})


@app.route('/friend/<key>', methods=['DELETE'])
def block_friend(key):
    return jsonify({'message': 'SUCCESS'})


@app.route('/chat_room/<key>', methods=['DELETE'])
def exit_friend(key):
    return jsonify({'message': 'SUCCESS'})


if __name__ == '__main__':
    app.run(debug=True)
