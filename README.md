# Python-mjc-timer

## 概要 Description
タイマー  
複数の時間を登録して順次カウントダウンするシーケンスを提供

## 特徴 Features

- 指定した時間を１秒ごとにカウントダウンします
- ２種類の時間の指定方法を提供します
	- `timer.json` ファイルに登録した時間から選んだ時間
	- `mjc_timer.json` ファイルに登録したシーケンスから選んだ一連の時間  
		シーケンスは複数の時間を登録しそれを順次カウントダウします
- 終了３秒前からブザーが鳴ります
- 時間は JSON ファイル（テキスト）に登録したものから選択します  
	自分でよく使う時間を事前に登録します
- 残り時間を数字と記号で表示します  
	記号は分単位（◎）で表示します  
	残り時間が１分を切ると秒単位（●）で表示します
- カウントダウンを中断できます

## 依存関係 Requirement

- Python 3.8.5

## 使い方 Usage
- 操作  
	- **単純なカウントダウンタイマー**
		- 時間を選択  
			「開始」ボタンの上にあるコンボボックスから時間を選択します
		- 開始：「開始」ボタンをクリック  
			ブザーが鳴りカウントダウンを開始  
		- 終了：ブザーが鳴り残り時間「0」を表示します
	- **シーケンスつきカウントダウンタイマー**
		- シーケンスを選択  
			「シーケンス開始」ボタンの上にあるコンボボックスからシーケンスを選択します
		- シーケンスの内容が「シーケンス開始」ボタンの下に表示されます
		- 開始：「シーケンス開始」ボタンをクリック  
			ブザーが鳴りカウントダウンを開始  
			- シーケンスのジョブを上から順にカウントダウンします  
				現在のジョブを選択状態にし、時間、内容を表示します
			- ジョブごとにカウントダウンが終了するとブザーが鳴り残り時間「0」を表示します
			- 続けて次のジョブのカウントダウンが始まります
		- 終了：すべてのジョブのカウントダウンが終了するとカウントダウンが停止します
	- **カウントダウンの中断**  
		- 「中断」ボタンを押します  

- 画面の説明  
	- 時間選択コンボボックス：タイマーの時間を選択します
	- 開始ボタン：カウントダウンを開始します  
	- シーケンス選択コンボボックス：シーケンスを選択します
	- シーケンス開始ボタン：シーケンスを開始します  
	- シーケンス内容表示リストボックス：シーケンスの内容を表示します  
	- 残り時間：残り時間を表示します
	- 残り時間量：残り時間をイメージ表示します
	- ジョブ内容：シーケンスのカウントダウンしているジョブを表示します  
	- 中断ボタン：タイマー動作を中断します
	- タイトル：残り時間を表示します

## 設定ファイル
以下のJSONファイルを使用します。

- `timer.json`  　　：時間用 JSON ファイル
- `mjc_timer.json`：シーケンス用 JSON ファイル

<p></p>

- 表示名と時間の設定：`[表示名, 時間]`  
	- 表示名：文字列
	- 時間：
		- 秒で指定：数字または文字列  
			例：`30`、`"30"`
		- 分秒で指定："分:秒" で指定します  
			例：`"1:0"`、`"1:30"`
- `mjc_timer.json` ファイルのシーケンスの設定：オブジェクト  
	オブジェクトの要素を追加してシーケンスを追加

## プログラムの説明サイト Program description site

- 使い方：[連続動作するタイマー【フリー】 - プログラムでおかえしできるかな](https://juu7g.hatenablog.com/entry/Python/timer-exe)  
- 作り方：[連続動作するタイマーの作り方【Python】 - プログラムでおかえしできるかな](https://juu7g.hatenablog.com/entry/Python/timer)  
  
## 作者 Authors
juu7g

## ライセンス License
このソフトウェアは、MITライセンスのもとで公開されています。LICENSEファイルを確認してください。  
This software is released under the MIT License, see LICENSE file.

