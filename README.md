# 猛瑪 LARK MIX 停用自動關機

## 前言

由於 LARK MIX 體積小巧且長續航，且不同於其他類似產品 (如 DJI Mic mini) 使用時重心都靠前容易扯衣領，所以我認為無其他產品可替代。

雖然剛出了 LARK M3，但是續航縮水成 8 小時且重心前移...

此麥克風最大遺憾為相機版 RX 端在 TX 斷線後約一小時會自動關機，無任何選項可以設定，寫信詢問官方也無答覆。

雖然手機版 RX (Type-C/Lightning) 不會自動關機，但是並沒有類比音訊輸出，不適合直接接音響或其他錄音設備使用。

由於希望可以將 RX 插電後固定放著，隨時拿起 TX 就可以開始使用，所以研究了如何停用自動關機。

## 摘要

目前僅實測猛瑪 (Hollyland/MOMA) LARK MIX (初代鈕扣型麥克風，代號`6301`) 的相機版 (正面有一個大旋鈕及三個音量指示燈) 接收器。

研究來源為「猛玛音频」App `MOMASOUND_china_prod_3.2.0_20260922_1816_37.apk`，來自中國官網。

此 API 似乎與 LARK M2S (代號`6302`) 通用，但是 MIX 只有 setter 無 getter，所以無法查看狀態。

尚不清楚為何不給 MIX 使用卻有留此選項，可能是產品區隔也可能是手機版 RX 使用同樣韌體但此選項只給手機版 RX 使用。

目前已在固件版本 `2.0.0.35` 的相機版 RX 實測可用，尚不清楚其他設備。

** 使用風險請自行負責 **
** Use it at your own risk **

腳本由 ChatGPT 6 產生，本人不負任何責任。

## 環境需求

- Python3
- `pip install hidapi`

## 指令

查看裝置
`lark_mix_rx.py`

針對指定HID裝置送心跳包 (選中 device[2] `0xFF90`)
`lark_mix_rx.py --device 2`

停用自動關機
`lark_mix_rx.py --device 2 --never`

啟用自動關機
`lark_mix_rx.py --device 2 --auto`

取得目前設定值 (未驗證，實測 LARK MIX 不支援，可能 M2S 可用)
`lark_mix_rx.py --device 2 --get-shutdown`
