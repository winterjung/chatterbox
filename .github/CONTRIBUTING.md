# :memo: How to contribute?
PR과 Issue를 올려주실 때 Template를 참고해주세요. 커밋 메시지는 짧게 적어주셔도 되나 통일성을 위해 영어로 부탁드립니다.

## :gem: Steps to contribute
* 관련된 내용을 [chatterbox issue]에 올려주세요.
* 저장소를 Fork 해주세요.
* Fork한 저장소를 개발 환경에 Clone 해주세요.
* 적절한 이름으로 새로운 branch를 만들어주세요.
* 기능 구현, 버그 수정, 알고리즘 변경 등등
* 테스트해주세요.
    * 단일 버전 파이썬 환경이라면 `pytest`를 통해 테스트 할 수 있습니다.
    * pyenv와 tox를 통해 3.4 이상의 환경을 모두 테스트 해 볼 수 있습니다.
    * `pylint --rcfile=.pylintrc --output-format=colorized chatterbox`를 통해 lint 테스트를 할 수 있습니다.
* 테스트가 통과하면 commit 후 push 해주세요.
* issue 링크와 설명을 추가해 PR을 날려주세요.
* 감사합니다! :sparkles:

[chatterbox issue]: https://github.com/JungWinter/chatterbox/issues
