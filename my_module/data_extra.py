# データ抽出や整形
import pandas as pd
import random
from collections import defaultdict
####################################################################################
# DataFrameから2種類の評価辞書を返す関数
####################################################################################
# 引数:df(インタラクションデータのDataFrame)
# 戻り値1:dic_user_rating(ユーザごとの評価辞書(key: ユーザID, value: dict{key: レシピID, value: 評価}))
# 戻り値2:dic_recipe_rating(レシピごとの評価辞書(key: レシピID, value: dict{key: ユーザID, value: 評価}))
def get_dic_rating(df):
    df_uid = df['u']  # ユーザID
    df_rid = df['i']  # レシピID
    df_rating = df['rating']  # 評価
    dic_user_rating = defaultdict(dict)
    dic_recipe_rating = defaultdict(dict)
    for uid, rid, rating in zip(df_uid, df_rid, df_rating):
        dic_user_rating[uid][rid] = rating
        dic_recipe_rating[rid][uid] = rating
    return dic_user_rating, dic_recipe_rating

####################################################################################
# テストユーザの評価が4以上のレシピについての評価辞書と新たなテストユーザを返す関数
####################################################################################
# 引数1:set_active_user(テストユーザのユーザIDの集合)
# 引数2:dic_test_user_rating(テストデータのユーザごとの評価辞書)
# 戻り値1:dic_active_high_rating(テストユーザの評価が4以上のレシピについての評価辞書)
# 戻り値2:set_active_user_new(4以上の評価がないユーザを除去した後のテストユーザのユーザIDの集合)
def get_dic_active_high_rating(set_active_user, dic_test_user_rating):
    dic_active_high_rating = {}
    set_active_user_new = set()
    for user in set_active_user:
        dic_high_rating = {}
        for recipe in dic_test_user_rating[user]:
            rating = dic_test_user_rating[user][recipe]
            if rating >= 4:
                dic_high_rating[recipe] = rating
        
        if len(dic_high_rating) > 0:  # 4以上の評価が1つ以上あるユーザのみ追加
            dic_active_high_rating[user] = dic_high_rating
            set_active_user_new.add(user)
    
    return dic_active_high_rating, set_active_user_new

####################################################################################
# 2人の評価辞書から両者とも作った(評価した)レシピの集合を返す関数
####################################################################################
# 引数1:dic_user1(ユーザ1の評価辞書(key:レシピID, value:評価))
# 引数2:dic_user2(ユーザ2の評価辞書(key:レシピID, value:評価))
# 戻り値:set_both_recipe(両者とも作った(評価した)レシピの集合)
def get_set_both_recipe(dic_user1, dic_user2):
    set_user1 = set(dic_user1.keys())  # ユーザ1が作ったレシピID
    set_user2 = set(dic_user2.keys())  # ユーザ2が作ったレシピID
    set_both_recipe = set_user1 & set_user2  # ユーザ1とユーザ2が作ったレシピIDの積集合
    return set_both_recipe

####################################################################################
# 両者とも作った(評価した)レシピに対する評価ベクトルを返す関数
####################################################################################
# 引数1:dic_user1(ユーザ1の評価辞書(key:レシピID, value:評価))
# 引数2:dic_user2(ユーザ2の評価辞書(key:レシピID, value:評価))
# 引数3:set_both_recipe(両者とも作った(評価した)レシピの集合)
# 戻り値1:vec_user1(両者とも作った(評価した)レシピに対するユーザ1の評価のリスト)
# 戻り値2:vec_user2(両者とも作った(評価した)レシピに対するユーザ2の評価のリスト)
# * vec_user1, vec_user2は同じ長さ(対応する順番に格納)
def get_vec_both_recipe(dic_user1, dic_user2, set_both_recipe):
    vec_user1 = []
    vec_user2 = []
    for recipe in set_both_recipe:
        rating1 = dic_user1[recipe]  # ユーザ1の評価
        rating2 = dic_user2[recipe]  # ユーザ2の評価
        vec_user1.append(rating1)
        vec_user2.append(rating2)
    return vec_user1, vec_user2

####################################################################################
# レシピ集合からランダムにレシピIDを抽出して，対象レシピを追加したリストを返す関数
####################################################################################
# 引数1:random_n(ランダムサンプリングするレシピ数)
# 引数2:set_recipes(嗜好が似ているユーザが評価したレシピの集合)
# 引数3:target_recipe(対象レシピ)
# 引数4:recipes_target_before(テストユーザが評価済のレシピID)
# 戻り値:random_sample_recepis(対象レシピを含めてN個のレシピIDのリスト)
def get_random_sample_recepis(random_n, set_recipes, target_recipe, recipes_target_before):
    non_rating_recipes = set_recipes - recipes_target_before  # 評価済レシピを除く
    random_sample_recepes = random.sample(non_rating_recipes, min(random_n - 1, len(non_rating_recipes)))  # ランダムにN-1個抽出したレシピID
    random_sample_recepes.append(target_recipe)  # 対象レシピを追加(合計N個になる)
    return random_sample_recepes

####################################################################################
# レシピごとの値の辞書から推薦レシピのランキングを作成
####################################################################################
# 引数1:dic_recipe_value(レシピごとの他人の評価の加重平均の辞書(key:レシピID, value:他人の評価の加重平均))
# 戻り値:rec_rankig(予測評価値を高い順にソートしたレシピIDのリスト)
def get_rec_ranking(dic_recipe_value):
    dic_recipe_value_sorted = sorted(dic_recipe_value.items(), key=lambda x:x[1], reverse=True)  # 値の大きい順にソート
    rec_rankig = [i[0] for i in dic_recipe_value_sorted]  # レシピIDのみを取得    
    return rec_rankig

####################################################################################
# 上位N個のレシピを取得
####################################################################################
# 引数1:rec_ranking(予測評価値を高い順にソートしたレシピIDのリスト)
# 引数2:top_n(上位N個のレシピを推薦するか)
# 戻り値:top_rec_recipes(上位N件のレシピID)
def get_top_rec_recipes(rec_ranking, top_n):
    top_rec_recipes = rec_ranking[:top_n]  # 上位N件を取得
    return top_rec_recipes

####################################################################################
# Ingredient mapのファイルを読み込んで，材料IDと材料名の辞書を返す関数
####################################################################################
# 引数:f_ingr(Ingredient mapのファイル)
# 戻り値:ingr_map(材料IDと材料名の辞書(dict{key: 材料ID, value: 材料名}))
def get_ingr_map(f_ingr):
    df_ingr = pd.read_pickle(f_ingr)
    ingr_ids, ingr_names = zip(*df_ingr.groupby(['id'], as_index=False)['replaced'].first().values)
    ingr_map = dict(zip(ingr_ids, ingr_names))
    ingr_map[max(ingr_ids) + 1] = ''
    return ingr_map

####################################################################################
# 2つのDataFrameから，辞書を返す関数
####################################################################################
# 引数1:df_key(keyとなるDataFrame(列数:1))
# 引数2:df_value(valueとなるDataFrame(列数:1))
# 戻り値:dic(辞書)
def df_to_dict(df_key, df_value):
    dic = {}  # 辞書(初期化)
    for key, value in zip(df_key, df_value):
        dic[key] = value  
    return dic

####################################################################################
# 学習データのDataFrameから，レシピIDの対応関係を示す辞書を返す関数
####################################################################################
# 引数:学習データのDataFrame
# 戻り値1:dic_recipe_id(key:u, value:recipe_id)
# 戻り値2:dic_raw_recipe_id(key:recipe_id, value:u)
def get_train_dic_repipe(df_train):
    # レシピID
    df_rid = df_train['i']  # 'i':Recipe ID, mapped to contiguous integers from 0
    df_recipe = df_train['recipe_id']  # 'recipe_id':Recipe ID
    # key: 0から割り振られたレシピID('u'), value: 生データのレシピID('recipe_id')
    dic_recipe_id = df_to_dict(df_rid, df_recipe)
    # key: 生データのレシピID('recipe_id'), value: 0から割り振られたレシピID('u')
    dic_raw_recipe_id = df_to_dict(df_recipe, df_rid)
    return dic_recipe_id, dic_raw_recipe_id

####################################################################################
# レシピから材料IDの集合を返す関数
####################################################################################
# 引数:recipe(レシピのDataFrame)
# 戻り値:set_ingr_id(材料IDの集合)
def set_ingr_ids(recipe):
    df_ingr = recipe['ingredient_ids']  # 材料のDataFrame
    list_ingr = list(df_ingr)[0][1:-1].split()  # 材料のリスト(str型)
    set_ingr_id = set()  # 材料IDの集合(int型)(初期化)
    for ingr in list_ingr:
        ingr_id = int(ingr.replace(',', ''))  # 材料ID
        set_ingr_id.add(ingr_id)
    return set_ingr_id

####################################################################################
# 材料IDの集合から材料名のリストを返す関数
####################################################################################
# 引数1:set_ingr_id(材料IDの集合)
# 引数2:ingr_map(材料IDと材料名の辞書(dict{key: 材料ID, value: 材料名}))
# 戻り値:list_ingr_name(材料名のリスト)
def get_ingr_name(set_ingr_id, ingr_map):
    list_ingr_name = []  # 材料名のリスト(初期化)
    for ingr in set_ingr_id:
        ingr_name = ingr_map[ingr]  # 材料名
        list_ingr_name.append(ingr_name)
    return list_ingr_name