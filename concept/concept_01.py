from chatterbox import Chatter


chatter = Chatter()

chatter.add_rule(action=["오늘의 식단, 내일의 식단"], from_state="홈", to_state="식단")
chatter.add_rule(action=["아침 식단, 점심 식단", "저녁 식단"],
                 from_state="식단",
                 to_state="홈")
chatter.add_rule(action="전체 식단 보기", from_state="식단", to_state="홈")
chatter.add_rule(action="부가 기능", from_state="홈", to_state="부가기능")
chatter.add_rule(action=["식단 평가", "오늘 식단은 어땠다", "학식 사진으로 보기"],
                 from_state="부가기능",
                 to_state="부가기능")
chatter.add_rule(action="닉네임 등록", from_state="부가기능", to_state="부가기능")
chatter.add_rule(action="랭킹 확인", from_state="부가기능", to_state="부가기능")
chatter.add_rule(action="활동 내역", from_state="부가기능", to_state="부가기능")
chatter.add_rule(action="취소", from_state="*", to_state="홈")

if __name__ == "__main__":
    chatter.run()
