// VideoToImage.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include "pch.h"

#include <iostream>
#include <io.h>
#include <direct.h>
#include <string>
#include "highgui/highgui.hpp"
#include "core/core.hpp"

using namespace std;
using namespace cv;

bool Video_To_Image(string filename)
{
	bool is_success = true;
	VideoCapture capture(filename);
	string save_folder;
	save_folder.assign(filename, 0, filename.length() - 4);
	const int save_folder_length = save_folder.length();

	if (!capture.isOpened())
	{
		cout << "无法打开视频文件 " << filename << endl;
		return false;
	}
	else 
	{//创建文件夹保存提取的图片
		if (_access(save_folder.c_str(), 0) == -1)
		{
			int flag = _mkdir(save_folder.c_str());
			if (!flag)
				cout << "已创建文件夹 " << save_folder << " 来保存视频" << filename << "中提取的图片" << endl;
			else
			{
				cout << "无法创建文件夹 " << save_folder << endl;
				return false;
			}
		}
		else
		{
			cout << "视频文件 " << filename << " 已提取" << endl;
			return false;
		}
	}
	
	/*CV_CAP_PROP_POS_MSEC – 视频的当前位置（毫秒）
	CV_CAP_PROP_POS_FRAMES – 视频的当前位置（帧）
	CV_CAP_PROP_FRAME_WIDTH – 视频流的宽度
	CV_CAP_PROP_FRAME_HEIGHT – 视频流的高度
	CV_CAP_PROP_FPS – 帧速率（帧 / 秒）*/
	int frame_width = (int)capture.get(CV_CAP_PROP_FRAME_WIDTH);
	int frame_height = (int)capture.get(CV_CAP_PROP_FRAME_HEIGHT);
	float frame_fps = capture.get(CV_CAP_PROP_FPS);
	int frame_number = capture.get(CV_CAP_PROP_FRAME_COUNT);//总帧数
	cout << "帧宽为" << frame_width << endl;
	cout << "帧高为" << frame_height << endl;
	cout << "帧率为" << frame_fps << endl;
	cout << "总帧为" << frame_number << endl << endl;

	double cur_frame = .0;//当前帧数
	int cur_pic = 0;//当前保存的图片
	long frame_gap = 1 * 60 * frame_fps;//提取图片的帧间隔(一分钟一张)

	while (cur_frame < frame_number)
	{
		bool flag = capture.set(CV_CAP_PROP_POS_FRAMES, cur_frame);//设置当前帧
		if (!flag)
			continue;
		Mat frame;
		bool bSuccess = capture.read(frame);//从视频中读取一个帧

		if (!bSuccess)
		{//读取失败
			cout << "不能从" << "filename" << "文件中读取第" << cur_frame << "帧" << endl;
			is_success = false;
		}
		else
		{//读取成功，保存图片
			char* save_img_name = new char[save_folder_length + 10];
			sprintf_s(save_img_name, save_folder_length + 10, "%s%s%d%s", save_folder.c_str(), "\\", cur_pic, ".jpg");
			imwrite(save_img_name, frame);
			if (_access(save_img_name, 0) == -1)
			{
				cout << "第" << cur_frame << "帧保存失败" << endl;
				is_success = false;
			}
			else
				cout << "第" << cur_frame << "帧保存成功" << endl;
		}
		cur_frame += frame_gap;
		++cur_pic;
	}
	capture.release();
	if (!is_success)
	{
		_rmdir(save_folder.c_str());
	}
}

int main()
{
	//遍历当前路径，获取目录下的所有.mp4文件
	char cur_path[200];
	_getcwd(cur_path, 200);
	cout << "当前路径：" << cur_path << endl;

	//文件句柄  
	intptr_t hFile = 0;
	//文件信息  
	struct _finddata_t file_info;
	string p;
	if ((hFile = _findfirst(p.assign(cur_path).append("\\*").c_str(), &file_info)) != -1)
	{
		do
		{
			if (!(file_info.attrib &  _A_SUBDIR))//如果是目录则跳过
			{
				string file_name = file_info.name;
				string suffix = file_name.substr(file_name.find_last_of('.') + 1, 4);
				if(suffix == "mp4")
					Video_To_Image(file_name);
			}
		} while (_findnext(hFile, &file_info) == 0);
		_findclose(hFile);
	}
	/*string video_name = "D:\\Code\\GasTank\\VideoToImage\\x64\\Release\\NVR_ch1_main_20190306100000_20190306102003.mp4";
	Video_To_Image(video_name);*/

	system("pause");
	return 0;
}