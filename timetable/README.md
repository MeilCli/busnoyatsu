# 時刻表データについて

## データタイプ
JSON

## ファイル名規則
ファイル名は下記フォーマットに準拠する．{FROM_POINT}にはバスの出発点が入る．

```
{FROM_POINT}.json
```
#### 例
kutc.json, takatsuki.json, tonda.json

## ファイル内記述規則
ファイル内の記述は下記フォーマットに準拠する．

```
"from": {
	"to": {
		"week": {
			"hour": [
				["minute", "destination", "status"],
				more...
			],
			more...
		},
		"sat": {
			"hour": [
				["minute", "destination", "status"],
				more...
			],
			more...
		},
		"sun": {
			"hour": [
				["minute", "destination", "status"],
				more...
			],
			more...
		}
	}
}
```

### from
バス出発点

### to
バス到着点

### week, sat, sun
平日（月ー金），土曜日，日曜祝日

### hour
時（0-24）

### minute
分（0-59）

### destination
行き先の指定（0-3）

- toと同じ（０）
- 高槻行（１）
- 萩谷行（２）
- 萩谷総合公園行（３）

### status
運行タイプの指定（0-3）

- 通常（０）
- 学休日は運休（１）
- 学休日のみ運行（２）
- 直行便（３）

##### 注
直行便に関しては，学休日は運休である．


## その他
***ファイル内に間違いを見つけたら，適宜修正して下さい***
