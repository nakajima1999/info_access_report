# ファイルや数値を指定して評価を実行
import time
from datetime import datetime
from my_module import eval_main
start_time = time.perf_counter()  # 開始
####################################################################################
# パラメータ
####################################################################################
f_train = 'dataset/interactions_train.csv'  # 学習データのインタラクションデータファイル
f_test = 'dataset/interactions_test.csv'  # テストデータのインタラクションデータファイル
sim_top_n = 5  # 上位何人の嗜好が似ているユーザを取得するか
random_n = 1000  # ランダムサンプリングするレシピ数
recipe_top_n = 100  # 上位N個のレシピを推薦するか

####################################################################################
# 評価結果
####################################################################################
result = eval_main.eval(f_train, f_test, sim_top_n, random_n, recipe_top_n)
dic_count = result[0]
dic_cf_metrics = result[1]
dic_tp_metrics = result[2]
print('パラメータ')
print('上位何人の嗜好が似ているユーザを取得するか:', sim_top_n)
print('ランダムサンプリングするレシピ数:', random_n)
print('上位N個のレシピを推薦するか:', recipe_top_n)
print()
print('データ数')
print(dic_count)
print()
print('協調フィルタリング')
print(dic_cf_metrics)
print()
print('TopPopular')
print(dic_tp_metrics)
print()

end_time = time.perf_counter()  # 終了
elapsed_time = end_time - start_time  # 実行時間(秒)
print('done!')
print('実行時間(秒):', elapsed_time)
print('実行時間(分):', elapsed_time / 60)
print('実行時間(時間):', elapsed_time / 60 / 60)