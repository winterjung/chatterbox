from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chatterbox import Chatter, Text, Keyboard
import json

# Create your views here.
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
def block_friend(request,key):
    return JsonResponse({'message': 'SUCCESS'})


@csrf_exempt
def exit_friend(request, key):
    return JsonResponse({'message': 'SUCCESS'})
