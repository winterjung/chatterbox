from flask import Flask, request, jsonify
from chatterbox import Chatter, Text, Keyboard


app = Flask(__name__)
"""
- sqlite memory를 사용하면 gunicorn 등을 사용해 멀티 프로세스로 앱을 구동시킬 때
  Chatter끼리 데이터를 공유할 수 있습니다.
- frequency를 명시해 일정 횟수마다 timeout된 데이터를 정리할 수 있습니다.
- fallback을 설정하면 사용자의 현재 state와 action에 맞는 규칙이 없더라도 action만을
  따져서 일치하는 규칙을 실행합니다.
"""
chatter = Chatter(memory='sqlite',
                  frequency=20,
                  fallback=True)


@chatter.base(name='홈')
def home_keyboard():
    home_buttons = ['숫자 맞추기']
    return Keyboard(home_buttons)


@chatter.rule(action='숫자 맞추기', src='홈', dest='맞추는중')
def guess(data):
    message = '숫자 맞추기를 시작합니다.'
    return Text(message) + Keyboard(type='text')


"""
dest를 명시하지 않고 규칙을 추가하면 함수 안에서 dest가 명시된 다른
규칙을 호출해야합니다.

e.g. decide 안에서 correct와 try_again을 조립함
"""
@chatter.rule(action='*', src='맞추는중')
def decide(data):
    answer = data['content']

    if answer == '42':
        response = correct(data)
    else:
        response = try_again(data)
    return response


@chatter.rule(dest='홈')
def correct(data):
    text = Text('맞았습니다!')
    return text + chatter.home()


@chatter.rule(dest='맞추는중')
def try_again(data):
    text = Text('틀렸습니다. 다시 시도해주세요.')
    keyboard = Keyboard(type='text')
    return text + keyboard


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
