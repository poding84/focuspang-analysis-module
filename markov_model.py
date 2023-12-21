from io import TextIOWrapper
from entity_model import State, StateUtil, EASY, NORMAL, HARD
import collections

class MarkovChainModel:
    transition_matrix: dict

    def __init__(self) -> None:
        self.transition_matrix = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))

    def update_model(self, state1: State, state2: State):
        self.transition_matrix[state1][state2] += 1
    
    def get_transition_probability(self, state1: State, state2: State):
        tot = 0
        for v in self.transition_matrix[state1].values():
            tot += v
        return self.transition_matrix[state1][state2]/tot if tot != 0 else 0
    

    def print_transition_prob_matix(self, f: TextIOWrapper):
        rows = StateUtil.list_all_state()
        cols = StateUtil.list_all_state()
        
        for col in cols:
            print("s" + str(col), end=', ', file=f)
        print(file=f)
        
        for row in rows:
            print("s" + str(row), end=', ', file=f)
            for col in cols[1:]:
                print(f"{self.get_transition_probability(row, col):.3f}", end=', ', file=f)
            print(file=f)
    
    def recommend_next_problem_difficulty(self, curr_state: State):
        easy = 0
        normal = 0
        hard = 0
        states: list[State] = StateUtil.list_all_state()[1:]
        for state in states:
            score = 0
            if (curr_state.label_emotion < state.label_emotion):
                score += state.label_emotion - curr_state.label_emotion
            if (curr_state.label_comprehension < state.label_comprehension):
                score += 1

            if state.difficulty == EASY:
                easy += self.get_transition_probability(curr_state, state) * score
            elif state.difficulty == NORMAL:
                normal += self.get_transition_probability(curr_state, state) * score
            else:
                hard += self.get_transition_probability(curr_state, state) * (score + 1)
        
        if hard >= normal and hard >= easy:
            return HARD
        elif normal > hard and normal >= easy:
            return NORMAL
        else :
            return EASY
    
    def predict_emotion(self, curr_state:State, difficulty: str):
        inc_emotion_prob = 0
        equ_emotion_prob = 0
        dec_emotion_prob = 0

        states: list[State] = StateUtil.list_all_state()[1:]
        for state in states:
            if state.difficulty == difficulty:
                if state.label_emotion == curr_state.label_emotion:
                    equ_emotion_prob += self.get_transition_probability(curr_state, state)
                elif state.label_emotion < curr_state.label_emotion:
                    inc_emotion_prob += self.get_transition_probability(curr_state, state)
                else :
                    dec_emotion_prob += self.get_transition_probability(curr_state, state)

        l = [inc_emotion_prob, equ_emotion_prob, dec_emotion_prob]
        if max(l) == inc_emotion_prob:
            return 1
        elif max(l) == equ_emotion_prob:
            return 0
        else :
            return -1

    def is_prediction_meaningful(self, curr_state: State, next_state:State):
        p = self.predict_emotion(curr_state, next_state.difficulty)

        if curr_state.label_emotion < next_state.label_emotion and p == 1: return True

        if curr_state.label_emotion == next_state.label_emotion and p == 0: return True
        
        if curr_state.label_emotion > next_state.label_emotion and p == -1: return True

        return False