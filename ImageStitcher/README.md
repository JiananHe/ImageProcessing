# 图像拼接
- [python](./python)中的[autoStitcher.py](./python/autoStitcher.py)基于opencv-python实现图像拼接，[fixedStitcher.py](./python/fixedStitcher.py)实现人为选定特征点进行拼接；
- [cxx](./cxx)直接调用OpenCV中的Stitcher类进行全景图片拼接；
- [cxx_details](./cxx_details)基于OpenCV实现图像拼接(在Stitcher类源码的基础上修改)。

## [cxx_details](./cxx_details)
### 环境依赖
[OpenCV 3.4.2](https://opencv.org/releases.html)<br>
若要在源码[stitching_details.cpp](./cxx_details/stitching_details.cpp)的基础再开发，则需要搭建OpenCV环境，有2中方法：通过OpenCV Win pack或者通过编译OpenCV源码，本项目环境搭建是通过编译OpenCV源码，具体过程可参考博客https://blog.csdn.net/anhec/article/details/88763495 。

### 项目运行
若希望直接使用可执行文件，可以下载[runfile.rar](./cxx_details/runfile.rar)，解压后双击其中Stithcer.bat文件，即可运行ImageStitcherDetails.exe可执行文件，exe的用法如下：<br>
```
ImageStitcherDetails.exe img1 img2 [...imgN] [Flags]
```
```
Flags:
  --one_batch (yes|no)
      Whether to Stitch all images in one batch. The default value is no.
      If yes, then stitch all images in one batch, otherwise stitch two images in every batch.
      The images must be read in order if one_batch is no.
  --features (surf|orb)
      Type of features used for images matching. The default is surf.
  --matcher (homography|affine)
      Matcher used for pairwise image matching.
 --conf_thresh <float>
      Threshold for two images are from the same panorama confidence.
  --show_process (yes|no)
      Show the features found in images and the features match result, The default value is 'no’.
 --output <result_img>
      The default is 'result.jpg'.

```
若拼接无法成功，可适当降低conf_thresh(默认值为0.5)。
