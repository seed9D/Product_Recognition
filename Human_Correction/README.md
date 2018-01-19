## Human Correction

### 目標
* 人工標注在 **find frequency pattern** 裡挖掘出的詞彙，標注出哪些詞彙是產品名 ，賦予字彙辭意

****
### Add Reference
* 為所有詞彙加上 協助/幫助 判斷的句子

#### Run code

```
  python3 Human_Correction/add_reference.py usr/find_frequency_pattern/filtered_alg.txt usr/find_frequency_pattern/source.txt
```
  * 輸入：第一個 argument 請放待標注詞彙file，參考格式如下

    ```
    詞彙            accept reject
    ----------------------
  	儿童摇摆车      5.7813  0
  	儿童摸鱼池      5.0308  0
  	儿童支架游泳池  4.633   0
  	儿童新款        20.9389 19.388
    ```
  
    第二個 argument 請放原始文件。 用意是加入一段完整的句子來幫助判斷詞彙是否有意義，此句子可以理解成此詞彙是從某句子中挖掘出來。

  * 輸出：預設輸出放置在 **usr/human_correction/recognition_reference.txt**
    參考格式如下：
    ```
    詞彙                            reference 句子
    -----------------------------------------------
    亲子游戏        1.2713  0       对战游戏亲子游戏魔幻陀螺超绝版豪华对战套装B
    亲子碰碰车      4.8463  0       河南儿童各种颜色双人亲子碰碰车机器人造型
    人偶    79.1719 0       卡通人偶公司直销行走卡通人偶
    人偶服装        2.25    0       卡通人偶服装
    人偶服饰        2.25    0       卡通人偶服饰
    ```
****
### 人工標注

1. 開啟 **usr/human_correction/recognition_reference.txt**
2. 刪除無意義的詞, 並將產品名標注 **P**
  ```
  pvc充气玩具     5.5713  0       环保pvc充气玩具厂家 P
  - ra      35.6389 0       minecraft彩盒
  - re      18.288  0       宝宝学步车reach151
  - st      16.9927 0       studio幼儿园中班教学蜡线
  - us      23.8777 19.018  Music
  usb     8.8971  0       2通遥控飞机不带陀带usb线 
  u盘     16.0046 0       u盘外壳生产厂家 P
  - y玩     0.02    0       kitty玩具
  一次    10.9541 0       湖北荆州钢架蹦床一次可玩几个孩子6变形的那种
  一次性  1.2459  0       一次性香皂旅馆小香皂批发
  七夕    4.742   0       七夕阿狸阿桃桃子情侣公仔
  七彩    131.9334        0       2只七彩陀螺
  七彩灯  2.8734  0.0735  七彩灯电动漂移车正品批发
  七彩灯光        68.3933 0.0525  七彩灯光.四轮带灯光.音乐
  七彩闪光        16.3163 0       七彩闪光灯
  七彩闪灯        8.8354  0       七彩闪灯VIP专享设置吸引小孩子 P
  七星瓢虫        12.6831 0       南博万七星瓢虫乐园
  - 万向电动        15.0123 0       万向电动动带3D触摸故事机功能
  万圣节  44.0423 0       供应万圣节面具
  ```
  * 每行前面有 *-* 號者，代表刪除整段 (line 2,3,4,5,8,18)
  * 只留下有意義的詞，並在產品明後方標注 **P**

****
### Seperate Word and Product

此步驟將標注完的檔案分開成兩個檔案，一個全是商品名，一個全是有意義詞

#### Run code

```
python3 Human_Correction/seperate_product.py [tagged_file]
```
* 輸入是標記完產品和塞選完有意義詞彙的檔案
* 輸出有二，一是產品名，預設放在 **usr/human_correction/product.txt**：

  ```
  乐高式场景积木
  乐高式拼装积木
  乐高式积木
  乒乓球
  乒乓球台
  书包
  书签
  二支装水枪
  ```
  另一是有意義詞彙,預設放在 **usr/human_correction/word.txt**：
  
  ```
  奇趣
  奔跑
  奔驰
  奖杯
  套圈
  套庄
  套装
  套装批发
  套餐
  ```
****
### Decompse word

此步驟是進一步將組合詞/複合字拆解成基本詞
`EX:套装批发 to 套裝 批發`

#### Run code

```
python3 Human_Correction/word_decompose.py usr/human_correction/word.txt
```

* input 即前一步驟產生的有意義詞
* output 預設放在 **usr/human_correction/base_word.txt**，格式如下

  ```
  车
  专色
  商场
  印花
  品牌
  一起
  喷球车
  发音
  ```

