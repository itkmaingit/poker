import random
from enum import IntEnum
from itertools import product


class HandColor(IntEnum):
    GRAY = -1
    PURPLE = 0
    WHITE = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5
    NAVY = 6


class Hand:
    def __init__(self, value, color=HandColor.GRAY):
        self.value = value
        self.suited = value.endswith("s")
        self.offsuit = value.endswith("o")
        self.pair = value[0] == value[1] and not self.suited and not self.offsuit
        self.color = color

        # コンボ数の計算
        if self.pair:
            self.combo_count = 6
        elif self.suited:
            self.combo_count = 4
        else:
            self.combo_count = 12

    def __repr__(self):
        return f"{self.value}"


class HandRange:
    def __init__(self):
        self.hands = {}
        ranks = "AKQJT98765432"
        rank_index = {rank: i for i, rank in enumerate(ranks)}

        # ハンド生成（ポケットペア・スーテッド・オフスート）
        for r1, r2 in product(ranks, repeat=2):
            if r1 == r2:  # ポケットペア
                hand = r1 + r2
                self.hands[hand] = Hand(hand)
            elif rank_index[r1] < rank_index[r2]:
                self.hands[r1 + r2 + "s"] = Hand(r1 + r2 + "s")
                self.hands[r1 + r2 + "o"] = Hand(r1 + r2 + "o")

        # 各ハンドに色を割り当て
        color_mapping = {
            HandColor.NAVY: {"AA", "KK", "AKs", "AKo", "QQ"},
            HandColor.RED: {
                "AQs",
                "AJs",
                "ATs",
                "KQs",
                "AQo",
                "JJ",
                "TT",
                "99",
            },
            HandColor.YELLOW: {"KJs", "QJs", "JTs", "88", "77", "AJo", "KQo"},
            HandColor.GREEN: {
                "A9s",
                "A8s",
                "A7s",
                "A6s",
                "A5s",
                "A4s",
                "A3s",
                "A2s",
                "KTs",
                "K9s",
                "QTs",
                "T9s",
                "KJo",
                "ATo",
                "66",
                "55",
            },
            HandColor.BLUE: {
                "Q9s",
                "J9s",
                "T8s",
                "98s",
                "QJo",
                "JTo",
                "KTo",
                "A9o",
                "44",
                "33",
                "22",
            },
            HandColor.WHITE: {
                "K8s",
                "K7s",
                "K6s",
                "K5s",
                "K4s",
                "K3s",
                "K2s",
                "Q8s",
                "Q7s",
                "Q6s",
                "J8s",
                "J7s",
                "97s",
                "87s",
                "76s",
                "65s",
                "A8o",
                "A7o",
                "K9o",
                "Q9o",
                "J9o",
                "T9o",
                "QTo",
            },
            HandColor.PURPLE: {
                "Q5s",
                "Q4s",
                "Q3s",
                "Q2s",
                "J6s",
                "T7s",
                "96s",
                "86s",
                "75s",
                "64s",
                "54s",
                "98o",
                "A6o",
            },
        }

        # 色を適用
        for color, hands in color_mapping.items():
            for hand in hands:
                if hand in self.hands:
                    self.hands[hand].color = color

    def query(
        self,
        include=None,
        exclude=None,
        color=None,
        suited=None,
        offsuit=None,
        pair=None,
    ):
        """
        動的クエリでハンドをフィルタリング
        """
        result = []
        for hand, obj in self.hands.items():
            if include and include not in hand:
                continue
            if exclude and exclude in hand:
                continue
            if color and obj.color not in color:
                continue
            if suited and not obj.suited:
                continue
            if offsuit and not obj.offsuit:
                continue
            if pair and not obj.pair:
                continue
            result.append(obj)
        return result

    def generate_query(self):
        color_range = list(range(HandColor.WHITE, HandColor.NAVY + 1))
        rng = random.random()
        if 0 <= rng < 1 / 13:
            label = "レイトポジションからのBBコール"
            colors = {HandColor.BLUE, HandColor.GREEN}
        elif 1 / 13 <= rng < 2 / 13:
            label = "CO からのBBコール"
            colors = {HandColor.WHITE, HandColor.BLUE}
        elif 2 / 13 <= rng < 3 / 13:
            label = "BTN からのBBコール"
            colors = {HandColor.PURPLE, HandColor.WHITE}
        elif 3 / 13 <= rng < 8 / 13:
            label = None
            colors = {
                random.choice(
                    [
                        HandColor.WHITE,
                        HandColor.BLUE,
                        HandColor.GREEN,
                        HandColor.YELLOW,
                        HandColor.RED,
                    ]
                )
            }
        else:
            label = None
            start_index = random.randint(HandColor.WHITE, HandColor.RED)
            colors = set(color_range[start_index - 1 :])

        # クエリ用の色のラベル
        color_labels = {
            HandColor.PURPLE: "紫(0)",
            HandColor.WHITE: "白(1)",
            HandColor.BLUE: "青(2)",
            HandColor.GREEN: "緑(3)",
            HandColor.YELLOW: "黄(4)",
            HandColor.RED: "赤(5)",
            HandColor.NAVY: "紺(6)",
        }
        # ハンドに含まれる1つのランダムなカードを選ぶ
        include = random.choice("AKQJT98765432")
        if label is None:
            # 選ばれた色範囲に基づいて選択される色をラベルに変換
            color_range = [color_labels[color] for color in colors]
            query_label = (
                f"{', '.join(color_range)}のレンジで {include} が含まれるハンドは？"
            )
        else:
            query_label = label + f"の時、{include}が含まれるハンドは？"

        return colors, include, query_label


def practice_mode():
    hand_range = HandRange()
    print("=== ハンド練習モード ===")
    print("Enter を押して次の問題へ、 'q' で終了")
    print()

    # ANSIカラーコードマッピング
    color_codes = {
        HandColor.PURPLE: "\033[1;7;35m",  # 紫 + 背景反転
        HandColor.WHITE: "\033[1;7;37m",  # 白 + 背景反転
        HandColor.BLUE: "\033[1;7;34m",  # 青 + 背景反転
        HandColor.GREEN: "\033[1;7;32m",  # 緑 + 背景反転
        HandColor.YELLOW: "\033[1;7;33m",  # 黄 + 背景反転
        HandColor.RED: "\033[1;7;31m",  # 赤 + 背景反転
        HandColor.NAVY: "\033[1;7;34m",  # 紺 + 背景反転
    }

    # リセット
    reset_style = "\033[0m"

    while True:
        (colors, include, label) = hand_range.generate_query()

        print(label)

        user_input = input("\nEnter を押して確認（'q' で終了）: ").strip().lower()
        print()

        if user_input == "q":
            print("終了します。")
            break

        results = hand_range.query(
            include=include,
            color=colors,
        )

        range_hands = hand_range.query(
            color=colors,
        )

        total_combos = 0
        for hand in range_hands:
            total_combos+=hand.combo_count

        combos = 0
        for hand in results:
            combos+=hand.combo_count
        print("\n=== 検索結果 ===")
        # 検索結果に色をつけて表示（背景色反転）
        colored_results = []
        for result in results:
            # 各ハンドの色を取得し、対応する色コードを適用
            color_code = color_codes[result.color]
            colored_results.append(f"{color_code}{result}{reset_style}")

        # 色付けされた結果を表示
        print(
            ", ".join(colored_results)
            if colored_results
            else "該当するハンドはありません。"
        )
        print()
        print(f"コンボ数: {combos} / {total_combos} = {round(100*combos/total_combos)} %")
        print("================")
        print()


# 実行
practice_mode()