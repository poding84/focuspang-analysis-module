

class StateUtil:
    def list_all_state(curr_state = None):
        if curr_state == None:
            return [State()] + StateUtil.list_all_state(State("HARD", 0, 0, 0))
        if curr_state == State("EASY", 1, 2, 1):
            return [curr_state]
        
        return [curr_state] + StateUtil.list_all_state(curr_state.next_state())

HARD = "HARD"
NORMAL = "NORMAL"
EASY = "EASY"

class State:
    difficulty: str # HARD, NORMAL, EASY
    label_base: int # 0, 1 정답여부
    label_emotion: int # 0, 1, 2 학습 의지
    label_comprehension: int # 0, 1 이해도 여부

    def next_state(self):
        if (self.difficulty == "HARD"):
            return State("NORMAL", self.label_base, self.label_emotion, self.label_comprehension)
        elif (self.difficulty == "NORMAL"):
            return State("EASY", self.label_base, self.label_emotion, self.label_comprehension)
        else:
            return State("HARD", self.label_base + 1, self.label_emotion, self.label_comprehension)

    def __init__(self, difficulty = None, label_base = -1, label_emotion = -1, label_comprehension = -1):
        # If no constructor variable => initial state
        self.difficulty = difficulty
        self.label_base = label_base % 2
        
        label_emotion = label_emotion + (label_base // 2)
        self.label_emotion = label_emotion % 3
        
        self.label_comprehension = label_comprehension + (label_emotion // 3)

    def __eq__(self, other):
        if other == None:
            return False
        return (
            (self.difficulty == other.difficulty)
            and (self.label_base == other.label_base)
            and (self.label_emotion == other.label_emotion)
            and (self.label_comprehension == other.label_comprehension)
        )

    def __hash__(self) -> int:
        return self.get_state_value()

    def __str__(self) -> str:
        if self.get_difficulty_num() < 0:
            return "9999"
        else: return str(self.get_difficulty_num()) + str(self.label_base) + str(self.label_emotion) + str(self.label_comprehension)

    def get_difficulty_num(self):
        if (self.difficulty == HARD): return 0
        elif (self.difficulty == NORMAL): return 1
        elif (self.difficulty == EASY): return 2
        return -1

    def get_difficulty_int(self):
        return self.get_difficulty_num() + 1

    def get_comprehension_int(self):
        return int(self.label_comprehension) + 1

    def get_emotion_int(self):
        return int(self.label_emotion) + 1
    
    def get_base_int(self):
        return int(self.label_base) + 1

    def get_state_value(self):
        # difficulty / base / emotion / comprehension
        return int(self.get_difficulty_int() * 1000 + self.get_base_int() * 100 + self.get_emotion_int() * 10 + self.get_comprehension_int())

class Question:
    question_id: str
    question_idx: int

    def __init__(self, question_id, question_idx) -> None:
        self.question_id = question_id
        self.question_idx = question_idx

class QuestionResultSet:
    questions: dict

    def __init__(self) -> None:
        self.questions = {}

    def insert_question(self, q: Question, s: State):
        self.questions[q] = s
    
    def get_state_transition_list(self):
        l = list(self.questions.items())
        l.sort(key=lambda a: a[0].question_idx)
        l = [(None, State())] + l
        res = []
        for i in range(1, len(l)):
            res.append((l[i-1][1], l[i][1]))
        
        return res

class Client:
    client_id: str
    bis_score: int
    question_result: QuestionResultSet

    def __init__(self, client_id, bis) -> None:
        self.client_id = client_id
        self.bis_score = bis
        self.question_result = QuestionResultSet()