# Product Recongnization

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




## Pattern Discovery

 [More detail](./find_pattern/README.md)
### 計算詞彙的 Entropy

#### Run code

```
	python3 find_pattern/find_frequency_pattern_by_entropy.py
```

### 分析 **detail\_information.txt**

#### Run code

```
	python3 find_pattern/alg.py
```
## Human Correction
[More detail](./Human_Correction/README.md)

### Add Reference

#### Run code

```
  python3 Human_Correction/add_reference.py usr/find_frequency_pattern/filtered_alg.txt usr/find_frequency_pattern/source.txt
```

### 人工標注

[人工標注](./Human_Correction/README.md)

### Seperate Word and Product

#### Run code

```
python3 Human_Correction/seperate_product.py [tagged_file]
```
### Decompse word

#### Run code

```
python3 Human_Correction/word_decompose.py usr/human_correction/word.txt
```

## Model build