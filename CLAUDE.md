# CLAUDE.md

Claude 每次在這個 repo 開 session（雲端或本機）都會自動讀這個檔案。它是 Claude 跨 session 的長期記憶：存在 git 裡，所以不會隨雲端容器回收而消失。

## 專案

H-SOIT 23.8.3 技術手冊：推測性的 OIF 框架，嘗試統一重力與資訊理論，探討暗能量、黑洞毛髮與 JWST 異常，並提出可檢驗的預測。預印本 doi:10.5281/zenodo.16896518。

目前程式碼與資料都在 `HSOIT_Project_v1.2.zip` 裡（尚未解壓進 repo），內容：

- `entropy_tax.py`、`HSOIT_shear_sims/`（Python 模擬）
- `HSOIT_highD_scan.jl`（Julia）
- `HSOIT_Geff_CLASS/`（給 CLASS 用的 C 模組）
- ` HSOIT_BHwaveforms/`、` data/`（注意：這兩個資料夾名稱前面有空白）
- `figures/`、`Symbols_and_Abbr.md`、`CHANGELOG.md`
- zip 內含 macOS 的 `__MACOSX/` 雜檔，解壓時應略過。

## 記憶

在這個 repo 工作時，學到之後 session 也該知道的事（使用者的偏好、做過的決定與原因、踩過的坑），就在下面加一行，跟著那次的變更一起提交。過時的就刪掉或改寫。

- 使用者希望 Claude 跨 session 保有記憶；做法是維護這個檔案（雲端 session 用不了 `/plugin`，claude-mem 這類本機記憶在雲端容器回收後也會消失）。
