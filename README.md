# Product Recognition

#### 目的：

```
	秋千 儿童 室内 婴儿幼儿童室内荡秋千户外 宝宝玩具
	儿童六一礼物儿童室内秋千户外吊椅室外荡秋千家用运动健身器材
	幼儿园儿童组合滑梯淘气堡室内滑梯宝宝游乐园滑滑梯秋千玩具包邮
	加厚滑滑梯儿童室内幼儿园婴儿玩具家用滑梯秋千组合海洋球球池
	滑梯批发 幼儿园儿童滑梯 室外最畅销塑料滑梯 秋千组合滑滑梯
	游乐设施幼儿园玩具户外大型小区儿童组合工程塑料室外幼儿园滑梯
```
以上字段是從淘寶網上爬取的標題，可以看出商家習慣性的把所有關鍵字塞進去，且沒明顯的分界。
目標是要將上面的句子分詞，並找出哪些是產品名。

#### 困難處：
* 特定領域的分詞任務，general 分詞器（Jieba hanglp) 可能效用不佳
* 產品名歧異大，人都很難說準什麼是產品
	* ex: 儿童组合滑梯淘气堡？ 淘气堡？ 组合滑梯？ 组合滑梯淘气堡？


#### 流程分成三大步驟：

1. Pattern Discovery： 分詞和新詞發現 
2. Human Correction: 發現的新詞和分詞，要經由人工校正並找出**詞意**是產品的詞彙
3. 神經網路學習 Product name 的組成

#### Furtue work:

1. 第三步驟中，神經網路訓練可以疊代
2. 第一步驟中，加入字典的幫助，減少人工量



****

## Pattern Discovery

 [More detail](./find_pattern/README.md)
### 計算詞彙的 Entropy

```
python3 find_pattern/find_frequency_pattern_by_entropy.py
```

### 分析 **detail\_information.txt**

```
python3 find_pattern/alg.py
```

****

## Human Correction
[More detail](./Human_Correction/README.md)

### Add Reference

```
python3 Human_Correction/add_reference.py usr/find_frequency_pattern/filtered_alg.txt usr/find_frequency_pattern/source.txt
```

### 人工標注

[人工標注](./Human_Correction/README.md)

### Seperate Word and Product

```
python3 Human_Correction/seperate_product.py [tagged_file]
```
### Decompse word

```
python3 Human_Correction/word_decompose.py usr/human_correction/word.txt
```

****

## Training Model
[More detail](./training_model/README.md)

### Tagging Source


```
python3 training_model/tag_product.py usr/find_frequency_pattern/source.txt usr/human_correction/product.txt usr/human_correction/base_word.txt
```

### Training NER model

在[kcws](https://github.com/koth/kcws)中，訓練過程較為繁瑣，按照下面python檔案即可濃縮步驟

1. 切換到 **training_model/kcws** 執行 `./configure` [構建](https://github.com/koth/kcws/blob/master/README.md#%E6%9E%84%E5%BB%BA) 完成環境部署
2. 切回根目錄執行 **training_model/training_model.py**，內含 training NER的所有步驟
    ```
    python3 training_model/training_model.py usr/training_model/source_segement.txt usr/training_model/source_tag.txt usr/training_model/tag_vocab.txt usr/training_model/char_vec.txt
    ```

****

## Run Recognization
[More detail](./recognition/README.md)


```
python3 recognition/product_recognition_test.py usr/recognition/hz_chinese_50.txt
```

從待測試文件中發現的產品名
  
      ```
      保护套
      工具
      轮胎
      家具
      机械
      平板电脑
      电池芯
      挂壁
      棉花
      婴儿手推车
      苹果
      宝马
      海狮
      干燥剂
      水果
      蘑菇
      座椅
      家电
      学习桌
      推车
      绳子
      电话
      食品
      糖果
      婴儿车
      ```
     
   可以看出發現的產品名還滿可靠的
