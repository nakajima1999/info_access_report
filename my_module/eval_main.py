# ファイルや数値を受け取って，評価する
import time
from tqdm import tqdm
import pandas as pd
from my_module import data_extra
from my_module import collaborative_filtering
from my_module import toppopular
from my_module import eval_metrics
def eval(f_train, f_test, sim_top_n, random_n, recipe_top_n):  
    ####################################################################################
    # 使用するデータの抽出・整形
    ####################################################################################
    # データの読み込み
    df_train = pd.read_csv(f_train)  # 学習データ
    df_test = pd.read_csv(f_test)  # テストデータ
    set_train_user = set(df_train.u.unique())  # 学習データのユーザ集合
    set_test_user = set(df_test.u.unique())  # テストデータのユーザ集合
    set_train_recipe = set(df_train.i.unique())  # 学習データのレシピ集合

    # 2種類の評価辞書を取得
    # ユーザごとの評価辞書:key: ユーザID, value: dict{key: レシピID, value: 評価}
    # レシピごとの評価辞書:key: レシピID, value: dict{key: ユーザID, value: 評価}
    dic_train_user_rating, dic_train_recipe_rating = data_extra.get_dic_rating(df_train)  # 学習データ
    dic_test_user_rating, dic_test_recipe_rating = data_extra.get_dic_rating(df_test)  # テストデータ
    
    # 協調フィルタリングで使う辞書
    dic_avg_rating = collaborative_filtering.get_dic_avg_rating(dic_train_user_rating)  # key:ユーザID, value:ユーザの評価平均
    # TopPopularで使う辞書
    dic_recipe_count = toppopular.get_dic_recipe_count(dic_train_recipe_rating)  # key:レシピID, value:評価数
    dic_recipe_avg = toppopular.get_dic_recipe_avg(dic_train_recipe_rating)  # key:レシピID, value:レシピの評価平均
    
    # テストユーザ：学習データとテストデータの両方に含まれるユーザであり，評価対象となるユーザ
    # すなわち，テストデータのみに含まれるユーザは除去する
    # 作ったことのあるレシピとして，学習データ中のインタラクションデータを入力するため，
    # 学習データ中にインタラクションデータがないユーザは評価ができない
    set_active_user = set_train_user & set_test_user

    # テストユーザの評価が4以上のレシピのみの評価辞書を取得
    # テストユーザを更新(4以上の評価がないユーザは除去)
    dic_active_high_rating, set_active_user = data_extra.get_dic_active_high_rating(set_active_user, dic_test_user_rating)

    ####################################################################################
    # 評価
    ####################################################################################
    # 評価指標を計算するためのリストや数値の初期化
    # 協調フィルタリング
    list_cf_ae = []  # Absolute Errorのリスト
    list_cf_se = []  # Squared Errorのリスト
    c_cf_hits = 0  # 推薦が成功した件数

    # TopPopular
    list_tp_ae = []  # Absolute Errorのリスト
    list_tp_se = []  # Squared Errorのリスト
    c_tp_hits = 0  # 推薦が成功した件数

    total_test = 0  # テストケースの総数
    i = 0
    for target in tqdm(set_active_user):  # テストユーザを1人ずつ処理
        dic_target_before = dic_train_user_rating[target]  # テストユーザがこれまでに作ったレシピについての評価辞書
        recipes_target_before = set(dic_target_before.keys())  # テストユーザがこれまでに作ったレシピのレシピID集合
        target_avg_rating = sum(dic_target_before.values()) / len(dic_target_before)  # 評価平均
        dic_target_after = dic_active_high_rating[target]  # 評価辞書(評価4以上):推薦システムが推薦すべきレシピ

        ################################################
        # 協調フィルタリング
        ################################################
        # 学習データのユーザとのコサイン類似度の辞書を取得
        dic_cos_sim = collaborative_filtering.get_dic_cos_sim(dic_train_user_rating, dic_target_before, target)
        # テストユーザと嗜好が似ているユーザを取得 
        sim_users = collaborative_filtering.get_similairty_users(dic_cos_sim, sim_top_n)
        # 嗜好が似ているユーザが評価したレシピの集合(推薦レシピ，ランキングの対象となるレシピ集合)を取得
        rec_recipes = collaborative_filtering.get_recommend_recipes(dic_train_user_rating, sim_users, recipes_target_before)

        # テストユーザのテストレシピを1つずつ処理
        for target_recipe in dic_target_after:
            total_test += 1
            true_rating = dic_target_after[target_recipe]  # 真の評価
            ################################################
            # 協調フィルタリング
            ################################################
            # 推薦レシピ(テストユーザが評価済のレシピは除く)からランダムにN個抽出して，対象レシピを追加したリストを取得
            cf_random_recepis = data_extra.get_random_sample_recepis(random_n, rec_recipes, target_recipe, recipes_target_before)
            # 上記のレシピ集合に対して加重平均(予測評価値)の辞書を取得
            dic_weighted_sum = collaborative_filtering.get_dic_weighted_sum(cf_random_recepis, target_avg_rating, dic_cos_sim, dic_train_recipe_rating, dic_avg_rating, target)
            # 上記の予測評価値の辞書からランキングを作成
            cf_rec_ranking = data_extra.get_rec_ranking(dic_weighted_sum)
            # 評価
            cf_absolute_error, cf_squared_error, cf_hit = eval_metrics.get_evals(dic_weighted_sum, cf_rec_ranking, target_recipe, true_rating, recipe_top_n) 
            list_cf_ae.append(cf_absolute_error)
            list_cf_se.append(cf_squared_error)
            c_cf_hits += cf_hit
    
            ################################################
            # TopPopular
            ################################################
            # 学習データ中のレシピ(テストユーザが評価済のレシピは除く)からランダムにN個抽出して，対象レシピを追加したリストを取得
            tp_random_recepis = data_extra.get_random_sample_recepis(random_n, set_train_recipe, target_recipe, recipes_target_before)
            # 上記のレシピ集合に対しての評価数の辞書を取得
            dic_random_count = toppopular.get_dic_random_count(dic_recipe_count, tp_random_recepis)
            # 上記の評価数の辞書からランキングを作成
            tp_rec_ranking = data_extra.get_rec_ranking(dic_random_count)        
            # 評価
            tp_absolute_error, tp_squared_error, tp_hit = eval_metrics.get_evals(dic_recipe_avg, tp_rec_ranking, target_recipe, true_rating, recipe_top_n)
            list_tp_ae.append(tp_absolute_error)
            list_tp_se.append(tp_squared_error)
            c_tp_hits += tp_hit
                
        i += 1
        #if i == 100:
            #break  
        time.sleep(1)
    
    ####################################################################################
    # 評価指標
    ####################################################################################
    # 協調フィルタリング
    dic_cf_metrics = eval_metrics.get_dic_metrics(list_cf_ae, list_cf_se, c_cf_hits, total_test, recipe_top_n)  
    # TopPopular
    dic_tp_metrics = eval_metrics.get_dic_metrics(list_tp_ae, list_tp_se, c_tp_hits, total_test, recipe_top_n)
    # 学習データの数の辞書
    dic_count = {'インタラクションデータ数': len(df_train), 
                'ユーザ数:': len(set_train_user), 
                'レシピ数': len(set_train_recipe), 
                'テストユーザ数': len(set_active_user),
                'テストケース数': total_test}
    # 結果
    result = [dic_count, dic_cf_metrics, dic_tp_metrics]
    return result