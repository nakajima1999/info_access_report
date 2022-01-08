# streamlitで入力・出力するための関数
from logging import error
from google.protobuf.descriptor import Error
import streamlit as st
from my_module import data_extra
####################################################################################
# 文字列が数字だけかどうか判定する関数
####################################################################################
def if_integer(string):
    if string[0] == ('-', '+'):
        return string[1:].isdigit()
    else:
        return string.isdigit()

####################################################################################
# 入力1:作ったことのあるレシピの入力から評価辞書を返す関数
####################################################################################
# 引数1:input_recipes(入力1:作ったことのあるレシピの入力)
# 引数2:dic_raw_recipe_id(key:生データのレシピID('recipe_id'), value:0から割り振られたレシピID('u'))
# 戻り値:dic_user_rating(評価辞書(dict{key:レシピID, value:評価}))
def get_target_rating(input_recipes, dic_raw_recipe_id):
    if input_recipes == '':
        return 'error'
    list_input_recipes = input_recipes.rstrip().split('\n') 
    dic_target_rating = {}  # 評価辞書(key:レシピID, value:評価)(初期化)
    for line in list_input_recipes:
        if '/' not in line:
            return 'error'
        else:
            col = line.split('/')
            if if_integer(col[0]):
                raw_id = int(col[0])  # 生データのレシピID('recipe_id')
            else:
                return 'error'
            if col[1] not in ['1', '2', '3', '4', '5']:
                return 'error'
            else:
                rating = int(col[1])  # 評価
                if raw_id not in dic_raw_recipe_id:
                    return 'error'
                rid = dic_raw_recipe_id[raw_id]  # 0から割り振られたレシピID('u')
                dic_target_rating[rid] = rating  # 評価辞書に格納
    return dic_target_rating
 
####################################################################################
# これまでに作ったレシピの評価辞書からレシピ名と評価を出力する関数
####################################################################################
# 引数1:dic_target_rating(評価辞書(dict{key:レシピID, value:評価}))
# 引数2:dic_recipe_id(key:0から割り振られたレシピID('u'), value:生データのレシピID('recipe_id'))
# 戻り値:dic_target_name_ratings(評価辞書(dict{key: レシピ名, value: 評価}))
def out_target_name_rating(dic_target_rating, dic_recipe_id, dic_recipe_name):
    st.write('これまでに作ったレシピ')
    i = 0
    for rid in dic_target_rating:
        recipe_id = dic_recipe_id[rid]  # 生データのレシピID('recipe_id')
        recipe_name = dic_recipe_name[recipe_id]   # レシピ名
        rating = dic_target_rating[rid]  # 評価
        recipe_url = 'https://www.food.com/search/' + str(recipe_id)  # レシピのURL
        recipe_link = '[' + recipe_name + '](' + recipe_url + ')'  # Food.comのリンク
        st.write('{}: {}（レシピID: {} / {}）/ 評価: {}'.format(i + 1, recipe_link, rid, recipe_id, rating))
        i += 1
        
####################################################################################
# 入力2:嫌いな材料の入力から嫌いな材料のリストを返す関数
####################################################################################
# 引数:input_dis_ingr(入力2:嫌いな材料の入力)
# 戻り値:list_dis_ingr(嫌いな材料のリスト)
def get_dis_ingr(input_dis_ingr):
    list_dis_ingr = []  # 嫌いな材料のリスト(初期化)
    # 嫌いな材料の入力がある場合のみ処理
    if len(input_dis_ingr) > 0:
        dis_ingr = input_dis_ingr.rstrip().split('\n')
        list_dis_ingr = []
        for ingr in dis_ingr:
            if if_integer(ingr):
                list_dis_ingr.append(int(ingr))
            else:
                return 'error'
    return list_dis_ingr

####################################################################################
# 嫌いな材料名をリストを返す関数
####################################################################################
# 引数1:list_dis_ingr(嫌いな材料のリスト)
# 引数2:ingr_map(材料IDと材料名の辞書(dict{key: 材料ID, value: 材料名}))
def get_dis_ingr_name(list_dis_ingr, ingr_map):
    if list_dis_ingr == 'error':
        return 'error'
    list_dis_ingr_name = []
    for ingr in list_dis_ingr:
        if ingr not in ingr_map:
            list_dis_ingr_name = 'error'
            break
        else:
            ingr_name = ingr_map[ingr]
            list_dis_ingr_name.append(ingr_name)
    return list_dis_ingr_name

####################################################################################
# 嫌いな材料名を出力する関数
####################################################################################
# 引数1:list_dis_ingr(嫌いな材料のリスト, ingr_map)
# 引数2:ingr_map(材料IDと材料名の辞書(dict{key: 材料ID, value: 材料名}))
def out_dis_ingr(list_dis_ingr_name):
    if len(list_dis_ingr_name) > 0:
        dis_ingr_name = '/'.join(list_dis_ingr_name)
        st.write('嫌いな材料: {}'.format(dis_ingr_name))

####################################################################################
# 入力された内容から，レシピを推薦して，表示する関数
####################################################################################
def out_rec_recipe(input_dis_ingr, recipe_top, dic_recipe_id, dic_recipe_name, df_recipes_data, ingr_map, df_raw_inter):
    rank = 0  # 順位
    for i in range(len(recipe_top)): 
            rid = recipe_top[i]  # 0からの連続した整数で割り振ったレシピID('i')
            recipe_id = dic_recipe_id[rid]  # 生データのレシピID('recipe_id')
            recipe_name = dic_recipe_name[recipe_id]   # レシピ名
            recipe_url = 'https://www.food.com/search/' + str(recipe_id)  # レシピのURL
            recipe_link = '[' + recipe_name + '](' + recipe_url + ')'  # Food.comのリンク
            recipe = df_recipes_data[df_recipes_data['i'] == rid]  # レシピのDataFrame
            set_ingr = data_extra.set_ingr_ids(recipe)  # 材料IDの集合
            list_ingr_name = data_extra.get_ingr_name(set_ingr, ingr_map)  # 材料名のリスト
            ingr_name = ', '.join(list_ingr_name)
            flag = 0  # ユーザが嫌いな材料が入っているかどうかのフラグ(0:入っていない, 1:入っている)
            # ユーザが嫌いな材料を1つずつ処理
            for dis_ingr in input_dis_ingr:
                # 材料の集合に嫌いな材料が入っている場合，フラグflagを1にする
                if dis_ingr in set_ingr:
                    flag = 1
                    break
            
            # 嫌いな材料が入っていない場合のみレシピを推薦
            if flag == 0:
                rank += 1  # 順位
                st.write('### {}位'.format(rank))
                st.write('{}（レシピID: {} / {}）'.format(recipe_link, rid, recipe_id))
                st.write('材料: {}'.format(ingr_name))
                # インタラクションの生データから，このレシピについてのデータを抽出
                df_cooked = df_raw_inter[df_raw_inter['recipe_id'] == recipe_id]  # このレシピについてのDataFrame
                list_date = df_cooked['date'].to_numpy().tolist()  # 日付のリスト
                list_rating = df_cooked['rating'].to_numpy().tolist()  # 評価のリスト
                list_review = df_cooked['review'].to_numpy().tolist()  # レビューのリスト
                # 評価平均
                avg_rating = sum(list_rating) / len(list_rating)
                avg_rating = round(avg_rating, 2)
                st.write('ユーザ評価の平均: {} （レビュー数: {}）'.format(avg_rating, len(list_rating)))
                # 評価，日付，レビュー
                for i, (date, rating, review) in enumerate(zip(list_date, list_rating, list_review)):
                    st.write('【{} 件目】\t評価: {}\t/日付: {}'.format(i + 1, rating, date))
                    st.write(review)
                    # レビューを3件だけ表示する
                    if i == 2:
                        break