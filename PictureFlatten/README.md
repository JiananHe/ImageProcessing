# 图像展平(LocalityFlatten.py)
本代码的展平算法的大致思路是：对图片待展平区域（即mask对应的区域），进行分区，再对每个小区域进行形变。

## 依赖
Python 3.6
- opencv-python
- Numpy<br>

pip install -r requirements.txt

## 运行
python LocalityFlatten.py <原图> <原图mask> [Flags] <br>
例子：<br>
python LocalityFlatten.py  D:\src.jpg D:\mask.jpg<br>

### Flags
-o|--output <result.jpg> <br>
      声明输出图片的保存路径，默认为该脚本同路径下的result.jpg。<br>
-s|--show<br>
      是否将中间过程可视化。<br>
--middle_region_ratio <0.2><br>
      控制最中间区域的宽度。<br>
--region_width_decay <0.85><br>
      控制从中间区域向两边区域的递减率。<br>
--min_width_ratio <0.2><br>
      控制最小区域宽度。<br>
--region_height_ratio <0.2><br>
      控制区域的高度。<br>
      <br>
后四个参数控制着图像分区的精细程度，一般而言，钢瓶的半径越小，或者与摄像头靠得越近，划分得要越细。<br>
