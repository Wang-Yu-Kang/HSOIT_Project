# H-SOIT-FM 金融預測研究

以 H-SOIT 理論結構建立預測模型，並在預先登記的條件下與標準基準模型比較樣本外準確度。

- 研究規則與成功條件：[PREREGISTRATION.md](PREREGISTRATION.md)
- 設計提案：<https://claude.ai/artifact/QyXxVvaexeMpBJKgJ5WMRF>

## 目前進度

| 階段 | 狀態 |
| --- | --- |
| 0. 預先登記 | v1 已登記 |
| 資料管線與封存期鎖 | 完成 |
| 基準模型與評估工具 | 完成，尚待真實資料執行 |
| 1. 機制單項檢驗 | 尚未開始 |
| 2. H-SOIT-FM 結構核心 | 尚未開始 |

## 使用方式

```bash
cd finance
pip install -r requirements.txt
python -m pytest -q tests          # 測試只用模擬資料
python -m scripts.run_baselines    # 下載資料並跑開發期基準
```

結果寫在 `results/`。若無法連到 Yahoo Finance，可以把 `date,open,high,low,close,volume` 格式的 CSV 手動放在 `data/raw/<代號>.csv`，例如 `data/raw/_GSPC.csv`。

## 封存期鎖

2022-01-01 以後的資料在 `hsoit_fm/data.py` 一律截斷，下載請求也只到 2021-12-31。只有在模型凍結、建立 `freeze-v*` git 標籤，並設定 `HSOIT_UNSEAL=<標籤名>` 之後才會開啟，每次開啟都記錄在 `UNSEAL_LOG.md`。

## 檔案

| 路徑 | 內容 |
| --- | --- |
| `hsoit_fm/config.py` | 登記的日期、市場、時間窗與門檻 |
| `hsoit_fm/data.py` | 資料下載、快取與封存期鎖 |
| `hsoit_fm/targets.py` | A1、A2、B1、C1、C2 預測目標 |
| `hsoit_fm/features.py` | 基準模型使用的因果特徵 |
| `hsoit_fm/walkforward.py` | 擴張窗 walk-forward 與標籤防洩漏間隔 |
| `hsoit_fm/baselines.py` | HAR-RV、EWMA、GARCH-t、歷史頻率、Logit |
| `hsoit_fm/evaluate.py` | QLIKE、Brier、對數損失、AUC、DM、MCS、SPA、Holm |
| `TRIALS.md` | 所有嘗試過的設定，供 SPA 檢定使用 |

此研究只做預測評估，不構成投資建議。
