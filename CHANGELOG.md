# Changelog
[Chatterbox] 프로젝트의 모든 변경 사항이 이 파일에 기록됩니다.

- `New`: 새로운 구현 사항
- `Fix`: 잘못된 부분 수정
- `Change`: 작동 방식 변경

## [0.2.2] - 2018-03-16
### Fix
- `chatterbox.memory.SqliteMemory`를 생성할 때 db 경로가 `tempdir`의 `chatterbox.db`로 고정되어 있어 두개 이상의 chatterbox 앱을 구동시킬 때 같은 db를 공유해 나중에 실행된 앱이 먼저 생성된 앱의 db를 삭제하는 문제가 발생하는 현상을 해결했습니다.

## [0.2.1] - 2018-02-27
### Fix
- 카카오톡 플러스친구 자동응답 API테스트에서 `keyboard` 테스트가 실패하는 현상을 수정했습니다. 이제 `Keyboard`를 `json.dump()` 메서드에 넘길 시 `'keyboard'` key가 제외된 value만 dump됩니다.
    - `flask.jsonify()`: [flask에서 json.dumps 사용]
    - `django.http.response.JsonResponse`: [django에서 json.dumps 사용]

## [0.2.0] - 2018-02-25
### Change
- `Response`, `Message`, `Keyboard` 등의 객체 멤버에 점(.)으로 접근 가능해졌습니다. [Example]

### Fix
- `tox.ini`를 수정하여 제대로 된 CI 테스트가 동작합니다.

## 0.1.0 - 2018-02-24
### New
:tada:

[Chatterbox]: https://github.com/jungwinter/chatterbox
[0.2.0]: https://github.com/JungWinter/chatterbox/compare/v0.1.0...v0.2.0
[Example]: https://github.com/JungWinter/chatterbox/blob/v0.2.0/tests/test_response.py#L98-L115
[0.2.1]: https://github.com/JungWinter/chatterbox/compare/v0.2.0...v0.2.1
[0.2.1]: https://github.com/JungWinter/chatterbox/compare/v0.2.1...v0.2.2
[flask에서 json.dumps 사용]: https://github.com/pallets/flask/blob/master/flask/json/__init__.py#L275
[django에서 json.dumps 사용]: https://docs.djangoproject.com/en/dev/_modules/django/http/response/#JsonResponse
