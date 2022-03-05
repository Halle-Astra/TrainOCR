# TrainOCR
## 运行环境
1. Paddle-gpu==2.0.0.post101    
2. paddleocr==2.0.2

## 运行说明
本项目主要构造TrainOCR类实现火车编号识别的pipeline，自行调用形式参考run.py。测试运行时可直接执行`python run.py --config config.json`，将读取视频并以视频形式展示识别结果，并将识别结果保存到输入文件同级目录下，比如当输入视频为`D:\Other\<file_name>.ts`时，识别结果将保存为`D:\Other\<file_name>.txt`;同时，中间所读取出的每一帧将保存在`frames\<file_name>`文件夹下，每一帧保存时的命名为该帧在视频中的时间`<hour>-<minute>-<second>-<millisecond>.png`.

### 参数说明
run.py中的参数都将会在TrainOCR类中被使用，命令行参数说明如下：
1. config：指定参数配置文件，run.py将解析该文件载入参数；指定配置文件时仍然可以以命令行参数的形式指定其他参数，命令行参数优先级高于参数配置表,目前命令行参数不完整，更推荐使用配置文件方法。
   
2. origin：输入源，如果传入的字符串是一个文件夹，则将读取文件夹的图片进行执行。如果传入的是数字，则将寻找摄像头作为视频源。如果输入的是一个文件路径，则将按照视频文件进行读取。由于ts文件不被opencv支持，而将ts文件改名为MP4后缀后无影响，再由于opencv对中文的不支持。在读取视频时，本项目将把视频改名成temp.mp4并搬移至工作目录下，当程序结束或被Ctrl-C终止时，将通过析构函数的形式将视频路径和文件名复原。

3. line_left：视频中应当被遮罩区域的左边界直线，以直线端点[[x1,y1],[x2,y2]]形式表示，以图像上下边界与直线交点给出端点两点，顺序不重要。

4. line_right：视频中应当被遮罩区域的右边界直线。

5. img_height：视频中每一帧的图像高度。

6. img_wide：视频中每一帧的图像宽度。

7. stride： 对单帧图像做识别时，以滑动窗口的形式划分窗口自下而上识别，stride为滑动步长。

8。 crop_height: 单帧图像识别时的窗口高度。

配置文件中的其他参数：
1. show： 是否对识别结果可视化，目前可视化形式为视频。

2. stride_num： 对单帧图像做识别时，窗口个数。

## TrainOCR
### TrainOCR.process
这个方法是用于对单张图像进行处理，取出一帧后自下而上生成滑动窗口并进行字符识别、识别结果后处理、识别结果保存、单帧展示。返回值为识别结果(识别结果保存文件的格式相同)：

    [{'url':'frames\\<file_name>\\<time>.png','time':<time>,'result':<ocr_result>},
    {'url':'frames\\<file_name>\\<time>.png','time':<time>,'result':<ocr_result>},
    {{'url':'frames\\<file_name>\\<time>.png','time':<time>,'result':<ocr_result>}]

如果识别结果为空，则返回值为空列表。

### TrainOCR.run
这个方法将迭代取出输入源中的每一张图像，然后送入process方法，并将process返回的识别结果汇总成一个列表。

### OCR识别结果
`<ocr_result>`的格式为

    [[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (<txt>, <score>)],
    [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (<txt>, <score>)],
    [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (<txt>, <score>)]]

x1，x2，x3，x4分别是识别边框（bbox）的左上角、右上角、右下角、左下角（顺时针）的横坐标。`<txt>`为该bbox中所含的文字，`<score>`为模型输出的该bbox中文字识别结果的置信度。