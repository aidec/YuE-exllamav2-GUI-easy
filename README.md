# YuE-exllamav2-GUI-easy
YuE-exllamav2-GUI簡易版介面

gui.py、config.json 放在src/yue/ 目錄內

top_200_tags.json 放在YuE-exllamav2主目錄內

## 使用方式
python src/yue/gui.py

有使用虛擬環境的話

myevnv\Scripts\activate && python src/yue/gui.py

記得config.josn內的模型1、模型2、虛擬環境路徑要做對應修改

## GUI
![image](https://github.com/user-attachments/assets/b0d2ce40-aeb2-49d6-b1e3-2c858471abea)

## 其他細節
若不能輸入中文，通過修改src/yue/infer_stage1.py，改成utf-8 就能通過中文了
with open(args.genre_txt, "r", encoding="utf-8") as f:

        genres = f.read().strip()

    with open(args.lyrics_txt, "r", encoding="utf-8") as f:

        lyrics = f.read().strip()

# 安裝方式        
https://blog.aidec.tw/post/yue-install-win
