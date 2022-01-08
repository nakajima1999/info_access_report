# streamlitで入出力を行う
import pandas as pd
import streamlit as st
from my_module import data_extra, st_proc, collaborative_filtering
####################################################################################
# データの読み込み
####################################################################################
# レシピデータ
f_recipes = 'dataset/PP_recipes.csv'
df_recipes_data = pd.read_csv(f_recipes)
# レシピの生データ
f_raw_recipes =  'dataset/RAW_recipes.csv'
df_raw_recipes = pd.read_csv(f_raw_recipes)
# インタラクションの生データ
f_raw_inter =  'dataset/RAW_interactions.csv'
df_raw_inter = pd.read_csv(f_raw_inter)
# インタラクションデータ(学習データ)
f_train = 'dataset/interactions_train.csv'
df_train = pd.read_csv(f_train)
# Ingredient map(材料IDとその材料名の辞書)
f_ingr = 'dataset/ingr_map.pkl'
ingr_map = data_extra.get_ingr_map(f_ingr)  # key: ingr_ids(材料ID), value: ingr_names(材料名)

####################################################################################
# DataFrameから辞書にする
####################################################################################
# レシピIDとレシピ名の辞書(key: レシピID('id'), value: レシピ名('name'))
dic_recipe_name = data_extra.df_to_dict(df_raw_recipes['id'], df_raw_recipes['name'])
# レシピIDの対応関係を示す辞書
# key: 0から割り振られたレシピID('u'), value: 生データのレシピID('recipe_id')
# key: 生データのレシピID('recipe_id'), value: 0から割り振られたレシピID('u')
dic_recipe_id, dic_raw_recipe_id = data_extra.get_train_dic_repipe(df_train)
# 2種類の評価辞書を取得
# ユーザごとの評価辞書:key: ユーザID, value: dict{key: レシピID, value: 評価}
# レシピごとの評価辞書:key: レシピID, value: dict{key: ユーザID, value: 評価}
dic_train_user_rating, dic_train_recipe_rating = data_extra.get_dic_rating(df_train)
# 協調フィルタリングで使う辞書(ユーザごとの評価平均)
dic_avg_rating = collaborative_filtering.get_dic_avg_rating(dic_train_user_rating)  # key:ユーザID, value:ユーザの評価平均

# パラメータ
sim_top_n = 5  # 上位何人の嗜好が似ているユーザを取得するか
recipe_top_n = 100  # 上位N個のレシピを推薦するか
#########################################################################
# ページに出力する内容
#########################################################################
st.title('レシピ推薦')
st.header('作ったことのあるレシピから')
st.header('好みを考慮してレシピを推薦')
# サイドバー
st.sidebar.header('入力')
# 入力1:作ったことのあるレシピの入力
st.sidebar.write('1. 作ったことのあるレシピを入力(必須)')
input_recipes = st.sidebar.text_area('入力: レシピID/評価 (※1行に1つのレシピを入力, 評価は1~5の5段階)', '')  # レシピID
st.sidebar.text('入力例:')
st.sidebar.code("""  
        16954/4
        134316/5
        39446/5
       """, language='text')
# 入力2:嫌いな材料の入力
st.sidebar.write('2. 嫌いな材料を入力(任意)')
input_dis_ingr = st.sidebar.text_area('入力: 材料ID (※1行に1つの材料を入力)', '')  # 材料
submit = st.sidebar.button('送信')  # 送信ボタン

# ボタンがクリックされた後の処理
if submit == True:
    # 入力1の内容を辞書に格納
    dic_target_before = st_proc.get_target_rating(input_recipes, dic_raw_recipe_id)
    # 入力2の内容をリストに格納
    list_dis_ingr = st_proc.get_dis_ingr(input_dis_ingr)
    # 嫌いな材料名のリスト
    dis_ingr_name = st_proc.get_dis_ingr_name(list_dis_ingr, ingr_map)

    if dic_target_before == 'error' or len(dic_target_before) == 0 or dis_ingr_name == 'error':
        st.write('入力が正しくありません')
    else:
        recipes_target_before = set(dic_target_before.keys())  # レシピID集合
        target_avg_rating = sum(dic_target_before.values()) / len(dic_target_before)  # 評価平均
        # これまでに作ったレシピのレシピ名と評価を出力
        st_proc.out_target_name_rating(dic_target_before, dic_recipe_id, dic_recipe_name)
        # 嫌いな材料の材料名を出力
        st_proc.out_dis_ingr(dis_ingr_name)
        ################################################
        # 協調フィルタリングによるレシピ推薦
        ################################################
        # 学習データのユーザとのコサイン類似度の辞書を取得
        dic_cos_sim = collaborative_filtering.get_dic_cos_sim(dic_train_user_rating, dic_target_before, '')
        # アクティブユーザと嗜好が似ているユーザを取得 
        sim_users = collaborative_filtering.get_similairty_users(dic_cos_sim, sim_top_n)
        # 嗜好が似ているユーザが評価したレシピの集合(推薦レシピ)を取得
        rec_recipes = collaborative_filtering.get_recommend_recipes(dic_train_user_rating, sim_users, recipes_target_before)
        # 上記のレシピ集合に対して加重平均(予測評価値)の辞書を取得
        dic_weighted_sum = collaborative_filtering.get_dic_weighted_sum(rec_recipes, target_avg_rating, dic_cos_sim, dic_train_recipe_rating, dic_avg_rating, '')
        # 上記の予測評価値の辞書からランキングを作成
        rec_ranking = data_extra.get_rec_ranking(dic_weighted_sum)
        # 上位N件を取得
        top_rec_recipes = data_extra.get_top_rec_recipes(rec_ranking, recipe_top_n)
        # 結果を表示
        st_proc.out_rec_recipe(input_dis_ingr, top_rec_recipes, dic_recipe_id, dic_recipe_name, df_recipes_data, ingr_map, df_raw_inter)