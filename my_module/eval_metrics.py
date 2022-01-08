# 評価指標を計算する関数
import math
####################################################################################
# 対象レシピの予測評価値を返す関数
####################################################################################
# 引数1:dic_recipe_value(レシピごとの予測評価値の辞書(key:ユーザID, value:予測評価値))
# 引数2:target_recipe(対象レシピのレシピID)
# 戻り値:pred_rating(対象レシピの予測評価値)
def get_pred_rating(dic_recipe_value, target_recipe):
    if target_recipe in dic_recipe_value:
        pred_rating = dic_recipe_value[target_recipe]  # 対象レシピの予測評価値  
    else:
        pred_rating = 0
    return pred_rating

####################################################################################
# 上位N件以内に対象レシピが入っているか（推薦が成功したかどうか(0/1)）を返す関数
####################################################################################
# 引数1:recipe_rank(対象レシピの順位)
# 引数2:recipe_top_n(上位何件を推薦するか)
# 戻り値:hit(推薦が成功したかどうか(0/1))
def get_hit(recipe_rank, recipe_top_n):
    if recipe_rank <= recipe_top_n:
        hit = 1  # N位以内ならば，成功
    else:
        hit = 0  # それ以外，失敗
    return hit

####################################################################################
# 評価指標を計算するために必要な値(Absolute Error, Squared Error, Hit)を返す関数
####################################################################################
# 引数1:dic_recipe_value(レシピごとの予測評価値(key:レシピID, value:予測評価値))
# 引数2:rec_ranking(ランキング)
# 引数3:target_recipe(対象レシピのレシピID)
# 引数4:true_rating(対象レシピの真の評価値)
# 引数5:recipe_top_n(上位何件を推薦するか)
# 戻り値1:absolute_error
# 戻り値2:squared_error
# 戻り値3:hit
def get_evals(dic_recipe_value, rec_ranking, target_recipe, true_rating, recipe_top_n):
    pred_rating = get_pred_rating(dic_recipe_value, target_recipe) # 対象レシピの予測評価値
    recipe_rank = rec_ranking.index(target_recipe) + 1  # 対象レシピの順位         
    absolute_error = abs(pred_rating - true_rating)  # Absolute Error
    squared_error = abs(pred_rating - true_rating) ** 2  # Squared Error
    hit = get_hit(recipe_rank, recipe_top_n)  # Hit
    return absolute_error, squared_error, hit

####################################################################################
# 評価指標の辞書を返す関数
####################################################################################
# 引数1:list_ae(Absolute Errorを格納したリスト)
# 引数2:list_se(Squared Errorを格納したリスト)
# 引数3:c_hits(推薦が成功した件数)
# 引数4:total_test(テストケース数)
# 引数5:recipe_top_n(上位何件を推薦するか)
# 戻り値:dic_metrics(key:評価指標の名称, value:評価指標の値)
def get_dic_metrics(list_ae, list_se, c_hits, total_test, recipe_top_n):
    mae = sum(list_ae) / len(list_ae)  # MAE
    rmse = math.sqrt(sum(list_se) / len(list_se))  # RMSE
    recall = c_hits / total_test  # Recall
    precision = recall / recipe_top_n  # Precision
    dic_metrics = {'MAE': mae,
                    'RMSE': rmse,
                    'Recall':recall,
                    'Precision': precision}
    return dic_metrics