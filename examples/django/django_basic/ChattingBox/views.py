from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chatterbox import Chatter
from chatterbox.response import Text, Keyboard, Photo, MessageButton, Message
import json

# Create your views here.
chatter = Chatter()

@chatter.base(name='홈')
def hom_keyboard():
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

def keyboard(request):
    return JsonResponse(chatter.home())

@csrf_exempt
def message(request):
    json_message = json.loads(request.body.decode('utf-8'))
    return JsonResponse(chatter.route(json_message))

@csrf_exempt
def add_friend(request):
    return JsonResponse({'message': 'SUCCESS'})

@csrf_exempt
def block_friend(request, key):
    return JsonResponse({'message': 'SUCCESS'})

@csrf_exempt
def exit_friend(request, key):
    return JsonResponse({'message': 'SUCCESS'})