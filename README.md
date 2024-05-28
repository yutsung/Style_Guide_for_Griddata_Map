# Style Guide for Griddata Map
根據中心的需求，希望我們配合[樣板](https://docs.google.com/document/d/1b1dGYjO1mGeYgrPQK3_8sWPZ6pVscdeSx42hC0UKyFY/edit)，  
制定並生產公版模組，上述文件中已包含部分因子的色階指引，可直接使用或自行從設定檔擴充，  
因為是統一格式，所以希望大家把意見彙集成一份模組就好，  
目前有開權限給大家，歡迎翻閱取用與回饋  

目前局內有提供產生範本的繪圖程式，是由python2.7的grads套件所繪製  
我放置在資料夾demo_from_cwa之中，請自行翻閱

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
操作方式也可以參考`module`內的`load_demo.py`  
  
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
`ref_dir='ref', china_coast=True, coast_width=0.8, caisancho=False`，第一個是參考資料夾的位子，  
第二個是是否要繪製中國海岸線，不繪製可以加速，第三個是海岸線粗細，偏粗會不容易看清離島的數值，  
偏細會影響本島縣市的判讀，最後一個是是否繪製外傘頂洲。  
```python
from module.draw_griddata import DrawGriddataMap
Draw_obj = DrawGriddataMap()
```
2. 輸入網格點ARRAY  
這裡的`lat`與`lon`都是二維的numpy array，單精度雙精度都可以使用
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
Draw_obj.mask_sea_gfe1km() # 若要不繪製非圖資範圍的顏色，非必要
Draw_obj.draw('tmax_demo.png', 'temperature')
Draw_obj.draw_zoom_in('tmax_demo.png', 'temperature')
Draw_obj.draw_zoom_out('tmax_demo.png', 'temperature')
```

