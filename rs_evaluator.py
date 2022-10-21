"""Recommender systems evaulator runs multiple recommender evaluation measures on provided data.

Note this is source code here is derived and adapted from COSC2933"""
import itertools
from surprise import accuracy
from collections import defaultdict
from surprise.model_selection import train_test_split, LeaveOneOut
from surprise import KNNBaseline


class EData:
    def __init__(self, data, rankings):
        # Generate entire training set for evaluating properties
        self.full_trainset = data.build_full_trainset()
        self.full_anti_testset = self.full_trainset.build_anti_testset()

        # Set rankings
        self.rankings = rankings

        # Generate a train (75) / test (25) split for measuring accuracy
        self.trainset, self.testset = train_test_split(
            data, test_size=0.25, random_state=1)

        # Create leave-one-out train/test split for eval of top-N recs
        # and we create an anti-test-set for generating predictions
        LOOCV = LeaveOneOut(n_splits=1, random_state=1)
        for train, test in LOOCV.split(data):
            self.LOOCVTrain = train
            self.LOOCVTest = test
        self.LOOCVAntiTestSet = self.LOOCVTrain.build_anti_testset()

        # Now compute sim matrix between users to measure diversity
        self.simAlgo = KNNBaseline(
            sim_options={'name': 'cosine', 'user_based': True}
        )
        self.simAlgo.fit(self.full_trainset)

    def get_full_trainset(self):
        return self.full_trainset

    def get_full_anti_testset(self):
        return self.full_anti_testset

    def get_trainset(self):
        return self.trainset

    def get_testset(self):
        return self.testset

    def get_LOOCV_testset(self):
        return self.LOOCVTest

    def get_LOOCV_trainset(self):
        return self.LOOCVTrain

    def get_LOOCV_anti_testset(self):
        return self.LOOCVAntiTestSet

    def get_rankings(self):
        return self.rankings

    def get_sims(self):
        return self.simAlgo


class Algorithm:

    def __init__(self, name, algorithm):
        self.name = name
        self.algo = algorithm

    def evaluate(self, eval_data):
        metrics = {}

        # Compute accuracy
        print("Evaluating accuracy...")
        self.algo.fit(eval_data.get_trainset())
        preds = self.algo.test(eval_data.get_testset())
        metrics['RMSE'] = Metrics.RMSE(preds)
        metrics['MAE'] = Metrics.MAE(preds)

        # Eval top-10 via leave-one-out
        print("Evaluating top-10 with LOOCV..")
        self.algo.fit(eval_data.get_LOOCV_trainset())
        lo_preds = self.algo.test(eval_data.get_LOOCV_testset())

        # Generate preds for ratings not in training
        all_preds = self.algo.test(eval_data.get_LOOCV_anti_testset())

        # Get top 10 recs per user
        topN_preds = Metrics.get_topN(all_preds, 10)

        print('Evaluating rank metrics...')
        # Hit-rate - how often a repo that the user liked was recommended
        metrics['HR'] = Metrics.hit_rate(topN_preds, lo_preds)

        # Cumulative-hit-rate
        metrics['CHR'] = Metrics.cumulative_hit_rate(topN_preds, lo_preds)

        metrics["ARHR"] = Metrics.avg_reciprocal_hit_rate(topN_preds, lo_preds)

        print('Computing recs with complete dataset...')
        self.algo.fit(eval_data.get_full_trainset())
        all_preds = self.algo.test(eval_data.get_full_anti_testset())
        topN_preds = Metrics.get_topN(all_preds, 10)

        metrics['Coverage'] = Metrics.user_coverage(
            topN_preds, eval_data.get_full_trainset().n_users)
        metrics['Diversity'] = Metrics.diversity(
            topN_preds, eval_data.get_sims())
        metrics['Novelty'] = Metrics.novelty(
            topN_preds, eval_data.get_rankings())

        print('Done.')

        return metrics


class Evaluator:
    algorithms = []

    def __init__(self, data, rankings):
        self.data = EData(data, rankings)

    def add_algorithm(self, name, algorithm):
        self.algorithms.append(Algorithm(name, algorithm))

    def evaluate(self):
        results = {}
        for algo in self.algorithms:
            print(f'Evaluating {algo.name}...')
            results[algo.name] = algo.evaluate(self.data)

        # Display results
        print("{:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
            "Algorithm", "RMSE", "MAE", "HR", "CHR", "ARHR", "Coverage", "Diversity", "Novelty"))

        for name, metrics in results.items():
            print("{:<10} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f} {:<10.4f}".format(
                name, metrics["RMSE"], metrics["MAE"], metrics["HR"], metrics["CHR"],  metrics["ARHR"], metrics["Coverage"], metrics["Diversity"], metrics["Novelty"]))


class Metrics:

    def MAE(predictions):
        return accuracy.mae(predictions, verbose=False)

    def RMSE(predictions):
        return accuracy.rmse(predictions, verbose=False)

    def get_topN(predictions, n=10):
        top_n = defaultdict(list)
        for uid, iid, actual, estimated, _ in predictions:
            if (estimated >= 1.0):  # >1 is min rating
                top_n[int(uid)].append((int(iid), estimated))

        for uid, ratings in top_n.items():
            ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[int(uid)] = ratings[:n]

        return top_n

    def hit_rate(top_n_preds, left_out_preds):
        """Determine the hit-rate (how good) of top-N list"""
        hits = 0
        total = 0
        for lo_pred in left_out_preds:
            lo_uid = lo_pred[0]
            lo_iid = lo_pred[1]

            # Check if in top 10
            is_hit = False
            for tn_iid, tn_pred in top_n_preds[int(lo_uid)]:
                if (int(lo_iid) == int(tn_iid)):
                    is_hit = True
                    break
            if is_hit:
                hits += 1
            total += 1

        precision = hits / total
        return precision

    def cumulative_hit_rate(topN_preds, left_out_preds):
        hits = 0
        total = 0
        for lo_uid, lo_iid, actual, estimated, _ in left_out_preds:
            if (actual >= 1.0):  # Only look at things the user starred
                is_hit = False
                for tn_iid, tn_pred in topN_preds[int(lo_uid)]:
                    if (int(lo_iid) == tn_iid):
                        is_hit = True
                        break
                if is_hit:
                    hits += 1
                total += 1
        precision = hits/total
        return precision

    def avg_reciprocal_hit_rate(topN_preds, left_out_preds):
        S = 0
        total = 0
        for lo_uid, lo_iid, actual, estimated, _ in left_out_preds:
            hit_rank = 0
            rank = 0
            for tn_iid, tn_pred in topN_preds[int(lo_uid)]:
                rank += 1
                if (int(lo_iid) == tn_iid):
                    hit_rank = rank
                    break
            if hit_rank > 0:
                S += 1.0 / hit_rank
            total += 1
        return S / total

    def user_coverage(topN_preds, num_users):
        # Calc the percentage of users that have at least 1 good rec
        hits = 0
        for tn_uid in topN_preds.keys():
            is_hit = False
            for tn_iid, tn_pred in topN_preds[tn_uid]:
                if tn_pred >= 2.0:  # Todo is 1 correct number to use??
                    is_hit = True
                    break
            if is_hit:
                hits += 1
        return hits / num_users

    # TODO: NOVELTY AND DIVERSITY ARE NOT WORKING -- most likely due to topN_preds not working??

    def diversity(topN_preds, sim_algorithm):
        n = 0
        total = 0
        mat = sim_algorithm.compute_similarities()
        for uid in topN_preds.keys():
            pairs = itertools.combinations(topN_preds[uid], 2)
            for pair in pairs:
                repo1 = pair[0][0]
                repo2 = pair[1][0]
                if sim_algorithm.trainset.knows_item(repo1) and sim_algorithm.trainset.knows_item(repo2):
                    inner_id1 = sim_algorithm.trainset.to_inner_iid(
                        repo1)  # used to be str(repo1)
                    inner_id2 = sim_algorithm.trainset.to_inner_iid(repo2)
                sim = mat[inner_id1][inner_id2]
                total += sim
                n += 1
        return 1 - (total / n)

    def novelty(topN_preds, rankings):
        n = 0
        total = 0
        for uid in topN_preds.keys():
            for rating in topN_preds[uid]:
                iid = rating[0]
                rank = rankings[iid]
                total += rank
                n += 1
        return total / n
