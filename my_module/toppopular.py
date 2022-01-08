# TopPopular
####################################################################################
# レシピごとの評価数(レビュー数)の辞書を返す関数
####################################################################################
# 引数:dic_train_recipe_rating(学習データのレシピごとのユーザの評価辞書(key: レシピID, value: dict{key: ユーザID, value: 評価}))
# 戻り値:dic_recipe_count(key:レシピID, value:評価数)
def get_dic_recipe_count(dic_train_recipe_rating):
    dic_recipe_count = {}
    for recipe in dic_train_recipe_rating:
        dic_recipe_count[recipe] = len(dic_train_recipe_rating[recipe])
    return dic_recipe_count

####################################################################################
# レシピごとの評価平均の辞書を返す関数
####################################################################################
# 引数1:dic_train_recipe_rating(学習データのレシピごとのユーザの評価辞書(key: レシピID, value: dict{key: ユーザID, value: 評価}))
# 戻り値:dic_recipe_avg(key:レシピID, value:レシピの評価平均)
def get_dic_recipe_avg(dic_train_recipe_rating):
    dic_recipe_avg = {}
    for recipe in dic_train_recipe_rating:
        dic_recipe_avg[recipe] = sum(dic_train_recipe_rating[recipe].values()) / len(dic_train_recipe_rating[recipe])
    return dic_recipe_avg

####################################################################################
# ランダムサンプリングしたレシピについてのレシピごとの評価数の辞書を返す関数
####################################################################################
# 引数1:dic_recipe_count(レシピごとの評価数の辞書(key:レシピID, value:評価数))
# 引数2:random_sample_recepis(ランダムサンプリングしたレシピ集合)
# 戻り値:dic_random_count(key:レシピID, value:評価数)
def get_dic_random_count(dic_recipe_count, random_sample_recepis):
    dic_random_count = {}
    for recipe in random_sample_recepis:
        if recipe in dic_recipe_count:
            dic_random_count[recipe] = dic_recipe_count[recipe]
        else:  # 学習データ中にないレシピの場合
            dic_random_count[recipe] = 0
    return dic_random_count