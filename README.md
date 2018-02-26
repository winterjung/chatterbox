# Chatterbox
[![license]](/LICENSE)
[![travis]](https://travis-ci.org/JungWinter/chatterbox)
[![appveyor]](https://ci.appveyor.com/project/JungWinter/chatterbox)
[![codecov]](https://codecov.io/gh/JungWinter/chatterbox)

---

<b>[Chatterbox]</b>는 [카카오톡 플러스친구 자동응답 API]를 활용하여 챗봇을 만들 때 사용되는 파이썬 라이브러리입니다.

## :memo: Installation

```shell
$ pip install chatterbox.py
```

## :rocket: Example
더 다양한 예제는 [examples]를 참고해주세요.

```python
from flask import Flask, request, jsonify
from chatterbox import Chatter
from chatterbox.response import Text, Keyboard, MessageButton


app = Flask(__name__)
chatter = Chatter()


@chatter.base(name='홈')
def home_keyboard():
    home_buttons = ['자기소개', '사이트로 이동하기']
    return Keyboard(home_buttons)


@chatter.rule(action='자기소개', src='홈', dest='홈')
def intro(data):
    message = 'chatterbox를 통해 더 쉽게 카카오톡 봇을 만들 수 있습니다!'
    return Text(message) + chatter.home()


@chatter.rule(action='사이트로 이동하기', src='홈', dest='홈')
def web(data):
    text = Text('자세한 정보를 보고싶으면 사이트로 이동해주세요!')
    msg_button = MessageButton(label='이동하기',
                               url='https://github.com/jungwinter/chatterbox')
    keyboard = chatter.home()
    return text + msg_button + keyboard


@app.route('/keyboard', methods=['GET'])
def keyboard():
    return jsonify(chatter.home())


@app.route('/message', methods=['POST'])
def message():
    return jsonify(chatter.route(request.json))


if __name__ == '__main__':
    app.run(debug=True)
```

## :gem: Usage
### Chatter
[FSM(finite-state machine)]을 사용해 유저들의 state를 내부에 저장하고, 요청에 맞는 response를 반환합니다.

#### `Chatter.route(data: dict) -> dict`
[카카오톡 자동응답 api 명세]에 맞는 json 데이터를 인자로 받습니다. `user_key`로 가져온 state와 `content`값을 action으로 적절한 rule을 찾아 등록된 함수를 실행한 후 api 명세에 맞는 response를 반환합니다. rule에 관해선 아래에 서술되어 있습니다.

##### 예제
```py
@app.route('/message', methods=['POST'])
def message():
    response = chatter.route(request.json)
    return jsonify(response)
```

input 데이터로 다음과 같은 형식의 dict 객체를 인자로 받습니다.

```json
{
  "user_key": "encryptedUserKey",
  "type": "text",
  "content": "자기소개"
}
```

output 데이터로 다음과 같은 형식의 Response 객체(dict로 동작함)를 반환합니다.

```json
{
  "message": {
    "text": "안녕하세요! 무엇을 도와드릴까요?"
  },
  "keyboard": {
    "buttons": [
      "오늘의 날씨",
      "취소"
    ],
    "type": "buttons"
  }
}
```

### Response
`chatterbox.response`에서 [카카오톡 response object 명세]를 만족하는 클래스를 가져올 수 있습니다.

#### Text(text)
다음과 같은 dict like 객체를 반환합니다. 멤버 변수로 `text`, `message`를 갖습니다.

```python
Text(text='안녕!')
```

```json
{
  "message": {
    "text": "안녕!"
  }
}
```

#### Photo(url, width, height)
다음과 같은 dict like 객체를 반환합니다. 멤버 변수로 `url`, `width`, `height`, `message`를 갖습니다.

```python
Photo(url='https://image/url.png',
      width=500,
      height=400)
```

```json
{
  "message": {
    "photo": {
      "url": "https://image/url.png",
      "width": 500,
      "height": 400
    }
  }
}
```

#### MessageButton(label, url)
다음과 같은 dict like 객체를 반환합니다. 멤버 변수로 `label`, `url`, `message`를 갖습니다.

```python
MessageButton(label='이동하기',
              url='https://github.com/jungwinter/chatterbox')
```

```json
{
  "message": {
    "message_button": {
      "label": "이동하기",
      "url": "https://github.com/jungwinter/chatterbox"
    }
  }
}
```

#### Keyboard(buttons, type)
자세한 명세는 [Keyboard object 문서]에서 확인할 수 있습니다. 멤버 변수로 `type`, `buttons`, `keyboard`를 갖습니다.

##### 주관식 입력
```python
Keyboard(type='text')
```

```json
{
  "keyboard": {
    "type": "text"
  }
}
```
##### 버튼 입력
```python
Keyboard(['버튼1', '버튼2'])  # type='buttons'는 생략할 수 있음
```

```json
{
  "keyboard": {
    "buttons": [
      "버튼1",
      "버튼2"
    ],
    "type": "buttons"
  }
}
```

#### 조합

```python
def intro():
    text = Text('안녕!')
    photo = Photo('https://image/url.png', 500, 400)
    keyboard = Keyboard(['날씨', '시간'])
    return text + photo + keyboard
```

위 코드는 아래와 같은 dict 객체를 반환합니다.

```json
{
  "message": {
    "text": "안녕!",
    "photo": {
        "url": "https://image/url.png",
        "width": 500,
        "height": 400
    }
  },
  "keyboard": {
    "buttons": [
      "날씨",
      "시간"
    ],
    "type": "buttons"
  }
}
```

##### 관계
```
Response
├── Message
│   ├── Text
│   ├── Photo
│   └── MessageButton
└── Keyboard
    ├── ButtonType
    └── TextType

Message + Message = Message
Message + Keyboard = Response
Response + Message = Response
```

### Base
#### `Chatter.add_base(name, func)`
`name`으로 유저가 시작할 state 이름을 지정할 수 있습니다.

> `func`은 인자가 없어야하며 `Keyboard`를 반환해야합니다.

##### 예제
```python
def func():
    return Keyboard(['버튼1', '버튼2'])
chatter.add_base(name='홈', func=func)
```

#### `@Chatter.base(name)`
`Chatter.add_base()`의 wrapper입니다. 데코레이터로 사용할 수 있습니다.

##### 예제
```python
@chatter.base(name='홈')
def func():
    return Keyboard(['버튼1', '버튼2'])
```

#### `Chatter.home()`
`Chatter.add_base()`를 통해 등록된 함수 `func`을 실행해 `Keyboard`를 반환합니다.

##### 예제
```python
>>> chatter.home()
{
  "keyboard": {
    "buttons": [
      "버튼1",
      "버튼2"
    ],
    "type": "buttons"
  }
}
```

### Rule
#### `Chatter.add_rule(action, src, dest, func)`
유저의 현재 state가 `src`이고 input으로 받은 데이터에서 content가 `action`일 때, `func` 함수를 실행하고 유저의 state를 `dest`로 변경합니다. state를 활용하여 1 depth 이상의 자동응답 시나리오를 구성할 수 있습니다.

> `func` 함수는 반드시 `data`를 인자로 받아야하며 `Response`를 반환해야합니다.

##### 예제
```python
def intro(data):
    message = 'chatterbox를 통해 더 쉽게 카카오톡 봇을 만들 수 있습니다!'
    return Text(message) + chatter.home()

chatter.add_rule(action='자기소개', src='홈', dest='홈', func=intro)
```

#### `@Chatter.rule(action, src, dest)`
`Chatter.add_rule()`의 wrapper입니다. 데코레이터로 사용할 수 있습니다.

##### 예제

```python
@chatter.rule(action='자기소개', src='홈', dest='홈')
def intro(data):
    message = 'chatterbox를 통해 더 쉽게 카카오톡 봇을 만들 수 있습니다!'
    return Text(message) + chatter.home()
```

#### 주관식 답변 처리하기
`Keyboard(type='text')`를 반환해 유저의 주관식 답변을 받는 경우 `action='*'`을 사용해 처리할 수 있습니다. 자세한 방법은 [examples/flask_advance.py]를 참고해주세요.

#### fallback 처리하기
`src='*'`를 사용해 유저가 어떤 state에 있더라도 특정 dest로 이동시킬 수 있습니다.

##### 예제
```python
@chatter.rule(action='취소', src='*', dest='홈')
def cancel(data):
    message = '취소하셨습니다.'
    return Text(message) + chatter.home()
```

## :pray: Contribution
[CONTRIBUTING.md]을 참고해주세요.


[Chatterbox]: https://github.com/JungWinter/chatterbox
[license]: https://img.shields.io/badge/license-MIT-blue.svg
[travis]: https://travis-ci.org/JungWinter/chatterbox.svg
[appveyor]: https://ci.appveyor.com/api/projects/status/ispy5kkm050m0ka5?svg=true
[codecov]: https://codecov.io/gh/JungWinter/chatterbox/branch/master/graph/badge.svg
[카카오톡 플러스친구 자동응답 API]: https://github.com/plusfriend/auto_reply
[examples]: https://github.com/JungWinter/chatterbox/blob/master/examples
[FSM(finite-state machine)]: https://ko.wikipedia.org/wiki/유한_상태_기계
[카카오톡 자동응답 api 명세]: https://github.com/plusfriend/auto_reply#specification-1
[카카오톡 response object 명세]: https://github.com/plusfriend/auto_reply/blob/master/README.md#6-object
[Keyboard object 문서]: https://github.com/plusfriend/auto_reply/blob/master/README.md#61-keyboard
[examples/flask_advance.py]: https://github.com/JungWinter/chatterbox/blob/master/examples/flask_advance.py
[CONTRIBUTING.md]: https://github.com/JungWinter/chatterbox/blob/master/.github/CONTRIBUTING.md
