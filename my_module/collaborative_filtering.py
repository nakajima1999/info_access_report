# 協調フィルタリング
from my_module import data_extra
from sklearn.metrics.pairwise import cosine_similarity
####################################################################################
# 学習データのユーザごとの評価平均の辞書を返す関数
####################################################################################
# 引数:dic_train_user_rating(ユーザごとの評価辞書(key: ユーザID, value: dict{key: レシピID, value: 評価}))
# 戻り値:dic_avg_rating(key:ユーザID, value:ユーザの評価平均)
def get_dic_avg_rating(dic_train_user_rating):
    dic_avg_rating = {}
    for user in dic_train_user_rating:
        dic_user_rating = dic_train_user_rating[user]
        avg_rating = sum(dic_user_rating.values()) / len(dic_user_rating)
        dic_avg_rating[user] = avg_rating
    return dic_avg_rating

####################################################################################
# ユーザ同士の類似度を返す関数(コサイン類似度)
####################################################################################
# 引数1:dic_user1(ユーザ1の評価辞書(key:レシピID, value:評価))
# 引数2:dic_user2(ユーザ2の評価辞書(key:レシピID, value:評価))
# 戻り値:cos_sim(コサイン類似度)
def get_cos_sim(dic_user1, dic_user2):
    set_both_recipe = data_extra.get_set_both_recipe(dic_user1, dic_user2)  # 両者とも作ったレシピの集合
    if len(set_both_recipe) == 0: 
        cos_sim = 0  # 両者とも作ったレシピがない場合，類似度は0
    else:
        # 両者とも作った(評価した)レシピに対する評価ベクトル
        vector1, vector2 = data_extra.get_vec_both_recipe(dic_user1, dic_user2, set_both_recipe)
        cos_sim = cosine_similarity([vector1], [vector2])[0,0]
    return cos_sim

####################################################################################
# テストユーザと学習データの全ユーザとのコサイン類似度を格納した辞書を返す関数
####################################################################################
# 引数1:dic_train_user_rating(学習データのユーザごとの評価辞書(key:ユーザID, value:dict{key: レシピID, value: 評価}))
# 引数2:dic_target_before(テストユーザがこれまでに作ったレシピについての評価辞書(key:レシピID, value:評価))
# 引数3:target(テストユーザのユーザID)
# 戻り値:dic_cos_sim(key:ユーザID, value:コサイン類似度)
def get_dic_cos_sim(dic_train_user_rating, dic_target_before, target):
    dic_cos_sim = {}
    for user in dic_train_user_rating:
        if user != target:
            dic_user_rating = dic_train_user_rating[user]  # 評価辞書
            cos_sim = get_cos_sim(dic_user_rating, dic_target_before)  # コサイン類似度
            dic_cos_sim[user] = cos_sim
    return dic_cos_sim

####################################################################################
# テストユーザと嗜好が似ているユーザのリストを返す関数
####################################################################################
# 引数1:dic_similairty(学習データとのコサイン類似度の辞書(key:ユーザID, value:類似度))
# 引数2:top_n(上位何人の嗜好が似ているユーザを取得するか)
# 戻り値:similairty_users(嗜好が似ているユーザIDのリスト)
def get_similairty_users(dic_similairty, top_n):
    dic_similairty_sorted = sorted(dic_similairty.items(), key=lambda x:x[1], reverse=True)  # 類似度の大きい順にソート
    similairty_users = [i[0] for i in dic_similairty_sorted]  # ユーザIDのみを取得
    similairty_users = similairty_users[:top_n]  # 上位N件を取得    
    return similairty_users

####################################################################################
# 嗜好が似ているユーザが評価したレシピの集合を取得
####################################################################################
# 引数1:dic_train_user_rating(学習データのユーザの評価辞書(key:ユーザID, value: dict{key:レシピID, value:評価}))
# 引数2:similairty_users(嗜好が似ているユーザIDのリスト)
# 引数3:recipes_target_before(テストユーザが評価済のレシピID)
# 戻り値:recommend_recipes(嗜好が似ているユーザが評価したレシピIDの集合)
def get_recommend_recipes(dic_train_user_rating, similairty_users, recipes_target_before):
    recommend_recipes = set()
    for user in similairty_users:
        dic_user_rating = dic_train_user_rating[user]  # 評価辞書
        for recipe in dic_user_rating:
            if recipe not in recipes_target_before:  # テストユーザが未評価のレシピの場合
                recommend_recipes.add(recipe)  # 嗜好が似ているユーザが評価したレシピを追加
    return recommend_recipes

####################################################################################
# 他ユーザの評価の加重平均(Weighted Sum of Others’ Ratings)を返す関数
####################################################################################
# 引数1:target_avg_rating(テストユーザの評価平均)
# 引数2:dic_similairty(テストユーザとの類似度の辞書(key:ユーザID, value:類似度))
# 引数3:dic_recipe_rating(対象レシピに対するユーザの評価辞書(key:ユーザID, value:予測評価値))
# 引数4:dic_avg_rating(学習データのユーザごとの評価平均の辞書(key:ユーザID, value:評価平均))
# 引数5:target(テストユーザのユーザID)
# 戻り値:weighted_sum(対象レシピに対するテストユーザの予測評価値)
def get_weighted_sum(target_avg_rating, dic_similairty, dic_recipe_rating, dic_avg_rating, target):
    denominator = 0  # 分母
    molecule = 0  # 分子
    for user in dic_recipe_rating:
        if user != target:
            similairty = dic_similairty[user]  # 類似度(重み)
            avg_rating = dic_avg_rating[user]  # このユーザの評価平均
            recipe_rating = dic_recipe_rating[user]  # このレシピに対するこのユーザの評価
            denominator += abs(similairty)  # 分母(重み)
            molecule += (recipe_rating - avg_rating) * similairty  # 分子((評価 - 評価平均) * 重み)
    # 他人の評価の加重平均(対象レシピに対するテストユーザの予測評価値)
    if denominator == 0:  # 分母が0の場合
        weighted_sum = target_avg_rating
    else:
        weighted_sum = target_avg_rating + molecule / denominator
    return weighted_sum

####################################################################################
# レシピごとの他人の評価の加重平均の辞書を返す関数
#################################################################################### 
# 引数1:rec_recipes(嗜好が似ているユーザが評価したレシピの集合)
# 引数2:target_avg_rating(テストユーザの評価平均)
# 引数3:dic_similairty(テストユーザとの類似度の辞書(key:ユーザID, value:類似度))
# 引数4:dic_train_recipe_rating(学習データのレシピごとのユーザの評価辞書(key: レシピID, value: dict{key: ユーザID, value: 評価}))
# 引数5:dic_avg_rating(学習データのユーザごとの評価平均の辞書(key:ユーザID, value:評価平均))
# 引数6:target(テストユーザのユーザID)
# 戻り値:dic_weighted_sum(key:レシピID, value:他人の評価の加重平均(対象レシピに対するテストユーザの予測評価値))
def get_dic_weighted_sum(rec_recipes, target_avg_rating, dic_similairty, dic_train_recipe_rating, dic_avg_rating, target):
    dic_weighted_sum = {}
    for recipe in rec_recipes:
        dic_recipe_rating = dic_train_recipe_rating[recipe]  # このレシピに対する評価辞書(key: ユーザID, value: 評価)
        weighted_sum = get_weighted_sum(target_avg_rating, dic_similairty, dic_recipe_rating, dic_avg_rating, target)  # 他人の評価の加重平均
        dic_weighted_sum[recipe] = weighted_sum 
    return dic_weighted_sum