# Style Guide for Griddata Map
根據中心的需求，希望我們參考[樣板](https://docs.google.com/document/d/1b1dGYjO1mGeYgrPQK3_8sWPZ6pVscdeSx42hC0UKyFY/edit)，  
以該樣板為起點發展公版模組。  
樣板程式碼放置在資料夾demo_from_cwa之中，有需要請自行翻閱  
註:該樣板已與目前發展中之公版相差許多，並且該樣板是由python2.7的grads套件所繪製  

# 2024/10/23 更新摘要
1. 小範圍圖中，金門地圖比例調整到與台灣相近
2. 小範圍圖中，馬祖圖框的三張彼此地圖比例相近
3. 小範圍圖中，馬祖圖框三張靠在一起讓讀者容易理解是同個地理或行政區
4. 小範圍圖中，馬祖圖框的地圖比例尺大約是台灣比例尺的三倍

# 2024/09/04 更新摘要
1. 金門圖框放大金門陸地比例  
2. 馬祖圖框拆成三張，分別是南北竿/東引/莒光  
3. 調整最大值搜尋範圍，納入東引，移除亮島  
4. 為了避免海岸線遮蔽小島的網格資訊，預設粗細由0.8調整為0.4  
5. 將繪製高程的範例與圖片放置於此頁  

# 2024/07/23 更新摘要
1. 修正黑底模式的地圖最大值使用黑色文字標示的錯誤，改為白色
2. 在`set_info`方法新增`lead_time_unit`的關鍵字，預設為h，可以如下操作調整`Draw_obj.set_info(..., lead_time_unit='m')`

# 2024/07/16 更新摘要
1. 為了增加方便性，不設定經緯度的情況下預設提供最新版GFE網格點
2. 機率(`probability`)色階將5%以下的顏色改為白色

# 2024/07/10 更新摘要
1. 補上邊界的經緯度標示，經緯度輔助線調粗
2. 新增雷達迴波所使用之色階`Radar_Composite_Reflectivity`
3. 配合雷達迴波新增黑底模式，使用`Draw_obj.draw(..., dark_mode=True)`呼叫
4. 新增黑色的風標圖，避免底色是風速時，相同顏色的風標看不清楚的問題，使用`Draw_obj.draw(..., draw_barbs=True, black_barbs=True)`呼叫

# 2024/06/27 更新摘要
1. 新增`draw_wind_barbs`方法，可繪製僅含風標圖的透明背景圖，圖框範圍與`draw`相同  
2. 新增`put_uwind_vwind`方法，可以僅匯入風標圖所需的uwind與vwind(單位為公尺每秒)  

# 2024/06/06 更新摘要
1. 增加`calculate_gfe1km_total_water`方法，若資料是GFE1km網格點，可以用此方法計算total_water
2. 解決total water的文字超出圖框的問題
3. 解決draw_zoom_in時金馬小框的最大值文字出現在中間圖中的問題

# 2024/05/28 更新摘要
1. 圖上最大值四捨五入到整數位

# 2024/04/23 更新摘要
1. 預設移除外傘頂洲，可由`DrawGriddataMap(caisancho=True)`補回  
2. 新增功能，可在圖上標出最大值位置與數值，  
   可使用`Draw_obj.draw(..., draw_max=True)`呼叫，  
   或者`Draw_obj.draw(..., draw_max_tw=True)`只標示台灣陸地最大值，  
   還有`Draw_obj.draw(..., draw_max_main=True)`標示台澎金馬蘭嶼綠島等有一定面積的陸地區域  
3. 微調圖框比例，解決原本colorbar超過4位數的數字會被切掉的問題  


## 測試環境版本
### 筆電本機
Python 3.10.9  
cartopy 0.21.1  
matplotlib 3.7.0  
numpy 1.23.5  
### Docker Image  
Python 3.10.12  
cartopy 0.22.0  
matplotlib 3.8.0  
numpy 1.26.1  

## 使用說明
基本上是操作`module`內的`draw_griddata.py`  
操作方式可以參考`module`內的`load_demo.py`  
還有要複製ref裡面需要的參考檔。  
  
0. 增加色階設定
下方的例子中，共有50個色階，最低跟最高的色碼設定在`color_under`與`color_over`，  
其餘的48個色階設定在`hex_list`，然後48個色階會有49個邊界設定在`boundary`，  
以及這49個邊界的文字標籤設定在`ticklabels`。  
接著是單位的文字描述`unit`，以及文字坐落的位子，座標是以colorbar左下為基準，  
範例中的`unit_xloc:1.05`、`unit_yloc:1.03`會約略在colorbar的正上方，略偏右  
```json
{
    "temperature":{
        "color_under":"#000080",
        "color_over":"#9c68ad",
        "boundary":[
            -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
            10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
            20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 
            30, 31, 32, 33, 34, 35, 36, 37, 38
        ],
        "hex_list":[
            "#0000cd", "#0000ff", "#0040ff", "#006aff", "#0095ff", "#00bfff", "#00eaff", "#00ffea", "#80fff4", "#117388", 
            "#207e92", "#2e899c", "#3d93a6", "#4c9eb0", "#5ba9ba", "#69b4c4", "#78bfce" ,"#87cad8", "#96d4e2", "#a4dfec",
            "#b3eaf6", "#0c924b", "#1d9a51", "#2fa257", "#40a95e", "#51b164", "#62b96a", "#74c170", "#85c876", "#96d07c", 
            "#a7d883", "#b9e089", "#cae78f", "#dbef95", "#f4f4c3", "#f7e78a", "#f4d576", "#f1c362", "#eeb14e", "#ea9e3a", 
            "#e78c26", "#e07b03", "#ed5138", "#ed1759", "#ad053a", "#780101", "#c3a4cd", "#af86bd"
        ],
        "ticklabels":[
            -10, "", -8, "", -6, "", -4, "", -2, "", 
            0, "",  2, "",  4, "",  6, "",  8, "", 
            10, "", 12, "", 14, "", 16, "", 18, "", 
            20, "", 22, "", 24, "", 26, "", 28, "", 
            30, "", 32, "", 34, "", 36, "", 38
        ],
        "unit":"$degree$C",
        "unit_xloc":1.05,
        "unit_yloc":1.03
    }

}
```
1. 初始化繪圖工具  
從模組中匯入`DrawGriddataMap`，再將其初始化，初始化欄位有四個可以填寫，以下是名稱與預設值，  
`ref_dir='ref', china_coast=False, coast_width=0.4, caisancho=False`，第一個是參考資料夾的位子，  
第二個是是否要繪製中國海岸線，不繪製可以加速，第三個是海岸線粗細，偏粗會不容易看清離島的數值，  
偏細會影響本島縣市的判讀，最後一個是是否繪製外傘頂洲。  
```python
from module.draw_griddata import DrawGriddataMap
Draw_obj = DrawGriddataMap()
```
2. 輸入網格點ARRAY  
這裡的`lat`與`lon`都是二維的numpy array，單精度雙精度都可以使用，  
預設會以新版1公里GFE初始化(117~124, 21.2~27)，資料符合該範圍可以跳過此步驟。  
```python
Draw_obj.put_latlon(lat, lon)
```
3. 輸入資料  
除了第一個欄位values之外，後方還有幾個欄位可以使用`values, **kwargs`，  
當名稱是total_water的時候，會將數值寫在圖上totoal water的顯示位置，  
當名稱是uwind跟vwind的時候，才能繪製風標圖
```python
Draw_obj.put_data(tmax)
```
若只要繪製透明背景風標圖，可以使用以下方式只匯入風場資訊  
```python
Draw_obj.put_uwind_vwind(uwind, vwind)
```
4. 設定標題  
第一個欄位是生產的單位名稱或是產線名稱或是生產方式，  
第二個欄位是場量的名稱，第三個欄位是python的datetime物件，用來標示資料生產的時間，  
第四第五個欄位是Lead Time的起點跟終點，單位是小時，整點預報就填寫1個，有時間段的統計就填寫2個，  
第四個欄位不填寫或是填寫-999的時候就不會顯示
```python
Draw_obj.set_info('ECDCA', 'max-T', init_date, 24, 36)
```
5. 運行繪圖  
有draw, draw_zoom_in, draw_zoom_out三個方法可使用，繪製的範圍不同，  
上述方法的第一個欄位是圖片輸出路徑與名稱，第二個欄位是色階在設定檔裡面的名稱，  
第三個欄位是`draw_barbs`預設是False，改成True可以疊上風標圖(步驟3要匯入風速)，  
若使用draw_zoom_in方法，則無風標圖可使用
```python
Draw_obj.mask_sea_gfe1km() # 用以遮蔽圖資外的範圍，自行選擇是否使用
Draw_obj.draw('tmax_demo.png', 'temperature')
Draw_obj.draw_zoom_in('tmax_demo.png', 'temperature')
Draw_obj.draw_zoom_out('tmax_demo.png', 'temperature')
```
若僅要繪製透明背景的風標圖，可以使用，繪圖範圍與`draw`相同  
```python
Draw_obj.draw_wind_barbs('wind_barbs_demo.png')
```