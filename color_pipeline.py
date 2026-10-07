import numpy as np


class TwoStageColorPipeline:

    def __init__(self, stage1_model, stage2_model):

        self.stage1_model = stage1_model
        self.stage2_model = stage2_model

        self.feature_names = [
            "G_median",
            "L_median",
            "LAB_B_median",
            "V_median",
            "R_median",
            "NG_median",
        ]

        self.classes_ = np.array([
            "c1",
            "c2",
            "c3"
        ])


    def predict(self, X):

        X = np.asarray(X)

        # -----------------------------------------
        # STAGE 1
        # c1 vs non_c1
        # -----------------------------------------

        stage1_pred = self.stage1_model.predict(X)

        final_prediction = np.empty(
            len(X),
            dtype=object
        )

        # Actual Stage 1 class names:
        # 'c1'
        # 'non_c1'

        c1_mask = stage1_pred == "c1"

        non_c1_mask = stage1_pred == "non_c1"

        # C1 directly becomes final C1
        final_prediction[c1_mask] = "c1"

        # -----------------------------------------
        # STAGE 2
        # c2 vs c3
        # -----------------------------------------

        if np.any(non_c1_mask):

            stage2_pred = self.stage2_model.predict(
                X[non_c1_mask]
            )

            # Actual Stage 2 class names:
            # 'c2'
            # 'c3'

            final_prediction[non_c1_mask] = stage2_pred

        return final_prediction


    def predict_proba(self, X):

        X = np.asarray(X)

        # -----------------------------------------
        # STAGE 1 PROBABILITIES
        # -----------------------------------------

        p1 = self.stage1_model.predict_proba(X)

        stage1_classes = list(
            self.stage1_model.classes_
        )

        c1_index = stage1_classes.index("c1")

        non_c1_index = stage1_classes.index("non_c1")

        p_c1 = p1[:, c1_index]

        p_non_c1 = p1[:, non_c1_index]


        # -----------------------------------------
        # STAGE 2 PROBABILITIES
        # -----------------------------------------

        p2 = self.stage2_model.predict_proba(X)

        stage2_classes = list(
            self.stage2_model.classes_
        )

        c2_index = stage2_classes.index("c2")

        c3_index = stage2_classes.index("c3")

        p_c2_given_non_c1 = p2[:, c2_index]

        p_c3_given_non_c1 = p2[:, c3_index]


        # -----------------------------------------
        # COMBINE
        # -----------------------------------------

        p_c2 = (
            p_non_c1 *
            p_c2_given_non_c1
        )

        p_c3 = (
            p_non_c1 *
            p_c3_given_non_c1
        )


        return np.column_stack([
            p_c1,
            p_c2,
            p_c3
        ])