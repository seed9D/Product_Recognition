## Training model

此步驟，要利用神經網路訓練出模型，能有效的對句子中產品詞彙進行標注。
此問題實際上就是NLP裡的 Name entity recongnition，只不過把問題簡化成只標注產品名。
****
### Tagging Source
* 標注出產品詞
* 把 **Human correction** 找出的產品詞彙標注回 **source** 文件裡


#### Taggin scheme
採用 B、I、E、S、O tag 句子, 代表的意義如下：

```
B: begin word of a product name in a sentnece
I: inter word of a product name in a sentence
E: end word of a product name in a sentence
S: a single product word
O: other, a word not belongs to product name
```
##### 例子 1:
`自控/B  飞机/E  厂家/O  六臂/O  旋转/B  升降/I  飞机/E  12/O    臂/O    豪华/O  自控/B  飞机/E  价格/O`

* **自控飛機**、**旋轉升降飛機**是兩個產品詞

  * **自控飛機** 可以拆解成 **自控** + **飛機**，所以**自控**標注 *B*; **飛機**標注 *E*
  * **旋轉升降飛機** 可以拆解成 **旋轉**+**升降**+**飛機**, 所以**旋轉**標注 *B*; **升降** 標注 *I*; **飛機** 標注 *E*
  
* 其餘不相關詞彙標注 *O*

##### 例子 2：
`现货/O  定做/O  热卖/O  款/O    充气床/S`


  * **充气床** 可以作為單獨產品名不可被拆解，所以標注為 *S*
#### Run Code

```
python3 training_model/tag_product.py usr/find_frequency_pattern/source.txt usr/human_correction/product.txt usr/human_correction/base_word.txt
```
* input 有三
  1. source.txt，原始位標注文件，即待標注文件
  
  ```
  创意硅胶胡子 生活日用橡胶制品 瓶酒瓶硅胶瓶套 欧美创意酒瓶套
  可以来图来样定制的酒吧垫 装饰品 时尚山羊胡子酒瓶套
  厂家直销个性创意酒瓶硅胶胡子 欢迎来样定做酒瓶胡子标识
  达强供应食品级硅胶胡子酒瓶识别器 硅胶酒瓶套  环保无毒
  达强专业生产批发创意环保硅胶酒瓶胡子 硅胶胡子瓶套
  ```

  2. product.txt，產品名詞彙文件
  
  ```
  公仔礼品
  公园滑梯
  六轴陀螺仪
  兵器
  内置陀螺仪
  写字板
  军事模型
  军刀
  ```
  
  3. base_word.txt, 各種有意義的基本詞，詞的長度介於1 ~ 3，可以組合出更多有意義詞，用來將組合的產品詞彙拆解成 B、I、E 形式
  `EX： 旋轉升降飛機 可以拆解成 旋轉+升降+飛機`
  
  ```
  吸水
  冰球
  晨宇
  专用
  书签
  制作
  加工
  包
  加盟
  坐垫
  好
  ```
* 輸出有 4，預設放在 **usr/training_model** 下
  1. **source_segement.txt**: **source.txt** 被分詞後的文件
  
  ```
  厂家 供应 自拍器 硅胶套 白色 透明 软胶 套 蓝牙 自拍器 套 现模 生产
  厂家 供应 自拍器 硅胶套 白色 透明 软胶 套 蓝牙 自拍器 套 现模 生产
  蓝牙 自拍器 硅胶套 软胶 套壳 磨砂 透明 自拍杆 遥控器
  供应 高品质 进口 硅胶 眼镜 防滑 耳 勾 眼镜 配件 防滑 耳套
  东莞 厂家 现货供应 硅胶 眼镜 防滑 套 耳套 耳托 量 大 从优
  胡子 硅胶 酒瓶 套 酒吧 专用 个性 胡子 杯 垫 硅胶 胡子 瓶套
  硅胶 酒瓶 胡子 套 创意 硅胶 胡子 酒瓶 套 厂家直销 欢迎 订购
  ```
  2. **source_tag.txt**: **source.txt** 裡成功找出產品名的句子集合
  
  ```
  厂家/O  供应/O  自拍器/S        硅胶套/S        白色/O  透明/O  软/O    胶套/S  蓝牙/B  自拍器/I        套/E    现模/O  生产/O
  厂家/O  供应/O  自拍器/S        硅胶套/S        白色/O  透明/O  软/O    胶套/S  蓝牙/B  自拍器/I        套/E    现模/O  生产/O
  蓝牙/B  自拍器/E        硅胶套/S        软/O    胶套/S  壳/O    磨砂/O  透明/O  自拍/O  杆/O    遥控器/S
  供应/O  高品质/O        进口/O  硅胶/S  眼镜/S  防滑/O  耳/O    勾/O    眼镜/S  配件/S  防滑/O  耳套/O
  东莞/O  厂家/O  现货供应/O      硅胶/S  眼镜/S  防滑/O  套/O    耳套/O  耳托/O  量大/O  从优/O
  胡子/O  硅胶/S  酒瓶/B  套/E    酒吧/O  专用/O  个性/O  胡子/O  杯垫/S  硅胶/S  胡子/O  瓶套/S
  硅胶/S  酒瓶/O  胡子/O  套/O    创意/O  硅胶/S  胡子/O  酒瓶/B  套/E    厂家直销/O      欢迎/O  订购/O
  硅胶/S  胡子/O  标记/O  现模/O  供应/O  硅胶/S  胡子/O  酒瓶/B  套/E
  东莞/O  硅胶/S  制品厂/O        专业/O  定制/O  生产/O  硅胶/S  单点/O  按键/O
  厂家/O  供应/O  硅胶/S  红/O    酒瓶/O  饰品/S  硅胶/S  胡子/O  时尚/O  造型/O  瓶套/S  批发/O  供应/O
  创意/O  硅胶/S  胡子/O  生活/O  日用/O  橡胶制品/O      瓶/O    酒瓶/O  硅胶/S  瓶套/S  欧美/O  创意/O  酒瓶/B  套/E
  ```
  

  3. **source_tag_negative.txt**: **source.txt** 無法找出產品名的句子集合
      * 不代表句子裡沒產品名，很可能是**product.txt** 裡未收錄。
      * 之後可以用訓練好的 NER 模型重新識別
  
  ```
  上链    小      乌龟
  眩光    YOYO    三款    混装
  弹跳    球
  熊出没  卡通    形象    授权
  卡乐咪  自动    充气    鳄鱼    球
  卡乐咪  袋鼠    跳跳    跳
  卡乐咪  软式    棍球
  卡乐咪  儿童    瑜伽    球
  卡乐咪  万能    面条    棍
  卡乐咪  团队    游戏    粘      粘      看
  卡乐咪  九宫    游戏
  ```
  4. **tag_vocab.txt**： 輸出tag scheme的對應編號
  
  ```
  B       0
  I       1
  E       2
  S       3
  O       4
  ```
****
### Training NER model
  
  NER model 訓練請參考 [kcws](https://github.com/koth/kcws)，訓練的過程大致上分成四個步驟
  1. 訓練 word to vector：
    事實上，在這邊訓練了兩個 vector，一個是詞向量; 一個是字向量。
    舉例來說，**现货** 其詞向量是指兩個字合在一起看的向量，字向量是指**現**
    的向量和**貨**的向量。而代表**現貨**的特徵是詞向量跟字向量的concate。
    字向量來自[kcws](https://github.com/koth/kcws)對人民日報語料的訓練結果，詞向量是 **source_segement.txt** 的訓練結果。
  2. 正式訓練NER 模型：
    網路架構請參考 [train_ner.py]()
  
  3. 模型導出：
    利用tensorlfow 提供的 freeze_graph.py 將網路圖和參數固化到一個檔案
  4. dump vector index：
    將詞向量和字向量 vector 所代表的詞彙以index表示
    詞向量 索引:
      ```
      驾驶台  10420
      折合    10418
      网球场  10417
      MOMO    10414
      Melody  10413
      小面包  10411
      ```
      字向量 索引:
      
      ```
        浜      4646
        伴      1169
        瑛      3025
        觉      634
        湎      5645
        贝      1551
        贱      3131
        见      396
        积      571
        隐      1139
      ```
    
  
#### Run code

在[kcws](https://github.com/koth/kcws)中，訓練過程較為繁瑣，按照下面python檔案即可濃縮步驟
1. 切換到 **training_model/kcws** 執行 `./configure` [構建](https://github.com/koth/kcws/blob/master/README.md#%E6%9E%84%E5%BB%BA) 完成環境部署
2. 切回根目錄執行 **training_model/training_model.py**，內含 training NER的所有步驟
    ```
    python3 training_model/training_model.py usr/training_model/source_segement.txt usr/training_model/source_tag.txt usr/training_model/tag_vocab.txt usr/training_model/char_vec.txt
    ```
    * 輸入有四：
    **source_segement.txt**、**source_tag.txt**、**tag_vocab.txt** 在前面提過。
    **char_vec.txt** 即字向量，由人民日報語料訓練得出([kcws](https://github.com/koth/kcws))
    * 主要輸出有三，預設放置在 **/usr/training_model** 下
      1. **product_model.pbtxt**: 訓練出的的神經網路模型
      2. **char_vec_index.txt**: 字向量索引
      3. **word_vec_index.txt**: 詞向量索引
      