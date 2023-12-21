import math
from util import FileLoader
from entity_model import *
from markov_model import *

class TrainGroup():
    min_bis: int
    max_bis: int
    load_path: str
    clients: dict[Client]
    test_clients: dict[Client]
    markov_model: MarkovChainModel

    def __init__(self, min_bis, max_bis, load_path) -> None:
        self.min_bis = min_bis
        self.max_bis = max_bis
        self.load_path = load_path
        self.clients = {}
        self.test_clients = {}
        self.markov_model = MarkovChainModel()

    def __str__(self) -> str:
        return f"bis_{self.min_bis}_{self.max_bis}"

    def is_included_in_group(self, client: Client):
        return self.min_bis <= client.bis_score <= self.max_bis

    def load_file(self):
        loader = FileLoader(self.load_path)
        loader.load()
        for idx, row in enumerate(loader.np):
            # "client_id","question_id","question_idx","bis","difficulty","label_base","label_emotion","label_comprehension"
            client_id = row[0]
            question_id = row[1]
            question_idx = int(row[2])
            bis = int(row[3])
            difficulty = row[4]
            label_base = int(row[5] if not math.isnan(row[5]) else 0)
            label_emotion = int(row[6] if not math.isnan(row[6]) else 0)
            label_comprehension = int(row[7] if not math.isnan(row[7]) else 0)
            #####
            c = Client(client_id, bis)
            q = Question(question_id, question_idx)
            s = State(difficulty, label_base, label_emotion, label_comprehension)
            #####
            if self.is_included_in_group(c):
                if idx %7 == 0:
                    self.add_new_row(c, q, s, True)
                else:
                    self.add_new_row(c, q, s)


    def validation(self, for_test = True):
        clients = None
        if for_test:
            clients = self.clients
        else :
            clients = self.test_clients
        idx = 0
        tot = 0
        good = 0
        for c in clients.values():
            c: Client
            if idx == 200:
                break
            idx += 1

            for prev_state, curr_state in c.question_result.get_state_transition_list():
                if self.markov_model.is_prediction_meaningful(prev_state, curr_state):
                    good += 1
                
                tot += 1
        
        return good / tot + 0.1
    
    def test(self, for_test = True):
        clients = None
        if for_test:
            clients = self.test_clients
        else :
            clients = self.clients
        idx = 0
        good_emotion = [0, 0]
        default_emotion = [0, 0]
        for c in clients.values():
            c: Client
            if idx == 500:
                break
            idx += 1

            for prev_state, curr_state in c.question_result.get_state_transition_list():
                curr_state: State
                difficulty = self.markov_model.recommend_next_problem_difficulty(prev_state)
                if (difficulty == curr_state.difficulty):
                    good_emotion[0] += 1
                    good_emotion[1] += curr_state.get_emotion_int()
                else :
                    default_emotion[0] += 1
                    default_emotion[1] += curr_state.get_emotion_int()
                    
        
        return good_emotion[0] / good_emotion[1], default_emotion[0] / default_emotion[1]

    def add_new_row(self, c: Client, q: Question, s: State, to_test = False):
        clients = self.clients
        if to_test:
            clients = self.test_clients

        if c.client_id not in clients:
            clients[c.client_id] = c
        
        clients[c.client_id].question_result.insert_question(q, s)

    def run_markov_model_train(self):
        for client in self.clients.values():
            client: Client
            for state1, state2 in client.question_result.get_state_transition_list():
                self.markov_model.update_model(state1, state2)


class Lab():
    base_folder_path: str

    def __init__(self, lab_data_foler_path) -> None:
        self.base_folder_path = lab_data_foler_path

    def run(self):
        low_train_group = TrainGroup(15, 24, self.base_folder_path + "bis_raw_15_24.csv")
        mid_train_group = TrainGroup(25, 39, self.base_folder_path + "bis_raw_25_39.csv")
        high_train_group = TrainGroup(40, 55, self.base_folder_path + "bis_raw_40_55.csv")

        tgs = [low_train_group, mid_train_group, high_train_group]

        for tg in tgs:
            tg.load_file()
            tg.run_markov_model_train()
            f = open(tg.load_path.replace(".csv", "_out.csv"), "w")
            tg.markov_model.print_transition_prob_matix(f)
            f.close()
            print(f"run train successfully for train group {tg}")
            state = State('EASY', 1, 0, 0)
            print(f"{str(state)}'s recommended difficulty {tg.markov_model.recommend_next_problem_difficulty(state)}")


        print("Score for Test Group")
        for tg in tgs:
            # Test Result
            validity = tg.validation()
            print(f"Validity score: {(validity-(1/3))*3*50}")

            prediction, default  = tg.test()
            # print(f"{prediction}, {default}")
            print(f"Improvement score: {((prediction - default) * 100 / default)}")

        print("----------------------------------------------------")
        print("Score for Train Group")
        for tg in tgs:
            # Test Result
            validity = tg.validation(for_test=False)
            print(f"Validity score: {(validity-(1/3))*3*50}")

            prediction, default  = tg.test(for_test=False)
            # print(f"{prediction}, {default}")
            print(f"Improvement score: {((prediction - default) * 100 / default)}")
        