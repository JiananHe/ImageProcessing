import sys, getopt
import cv2
import numpy as np

'''
omit the mask extraction procedure
'''


def usage():
    print("Flatten a picture in which the roi is the surface of a cylinder according to the surface mask.\n")
    print(sys.argv[0] + " src_img mask_img [Flags]\n")
    print("Flags:\n")

    print("    -o|--output <result.jpg>")
    print("        Declare the save path of result image, the defalut is 'result.jpg' under the script path. \n")

    print("    -s|--show")
    print("        If set this flag, all intermediate processes would be shown.\n")

    print("    --middle_region_ratio <0.2>")
    print('\tSet the ratio of the width of the middle region to the total length of the mask, the default value is 0.2.')
    print("\tThe closer the object is to the camera, or the greater the radius of the cylinder, the higher the value should be.\n")

    print("    --region_width_decay <0.85>")
    print("\tSet the decline rate for the width of the region from the middle to the sides, the default value is 0.85.\n")

    print("    --min_width_ratio <0.2>")
    print("\tSets the minimum ratio of the width of the most marginal region to the width of the middle region, the default value is 0.2.\n")

    print("    --region_height_ratio <0.2>")
    print("\tSet the ratio of the height of each region to the height of the mask, the default value is 0.2.\n")


def postProcess(img):
    black_col_left = 0
    while (img[:, black_col_left, :] == 0).all():
        black_col_left = black_col_left + 1

    black_col_right = img.shape[1] - 1
    while (img[:, black_col_right, :] == 0).all():
        black_col_right = black_col_right - 1

    return img[:, black_col_left:black_col_right, :]


def flattenArea(lr, tb, middle_region_ratio, region_width_decay, min_width_ratio, region_height_ratio):
    width = mid_col - leftmost if lr == "left" else rightmost - mid_col
    init_interval_length = int(width * middle_region_ratio + 0.5)
    min_interval_length = int(init_interval_length * min_width_ratio + 0.5)

    dst_height = mask_bottom[mid_col] - mid_row if tb == "bottom" else mid_row - mask_top[mid_col]
    dst = np.zeros((dst_height, init_interval_length, 3), dtype='int64')
    total_interval_width = 0

    interval_width = init_interval_length
    if lr == "left":
        interval_right = mid_col
        interval_left = mid_col - interval_width
    elif lr =="right":
        interval_left = mid_col
        interval_right = mid_col + interval_width

    interval_dst_width = init_interval_length
    interval_dst_height = int(dst_height * region_height_ratio)

    while total_interval_width < width:
        if tb == "bottom":
            col_right_height = mask_bottom[interval_right] - mid_row
            col_left_height = mask_bottom[interval_left] - mid_row
        elif tb == "up":
            col_right_height = mid_row - mask_top[interval_right]
            col_left_height = mid_row - mask_top[interval_left]

        if lr == "left":
            col_left_height = col_left_height if col_left_height <= col_right_height else col_right_height
        elif lr =="right":
            col_right_height = col_right_height if col_right_height <= col_left_height else col_left_height

        dst_col = np.zeros((dst_height, interval_dst_width, 3), dtype='int64')
        for k, i in enumerate(np.arange(0, 1, region_height_ratio)):
            if tb == "bottom":
                interval_left_top = mid_row + i * col_left_height
                interval_left_bottom = mid_row + (i + region_height_ratio) * col_left_height
                interval_right_top = mid_row + i * col_right_height
                interval_right_bottom = mid_row + (i + region_height_ratio) * col_right_height
            elif tb == "up":
                interval_left_bottom = mid_row - i * col_left_height
                interval_left_top = mid_row - (i + region_height_ratio) * col_left_height
                interval_right_bottom = mid_row - i * col_right_height
                interval_right_top = mid_row - (i + region_height_ratio) * col_right_height

            pts1 = np.float32([[interval_left, interval_left_top], [interval_right, interval_right_top],
                               [interval_left, interval_left_bottom], [interval_right, interval_right_bottom]])
            cv2.line(src_temp, (int(interval_left), int(interval_left_top)),
                     (int(interval_right), int(interval_right_top)),
                     (0, 255, 0))
            cv2.line(src_temp, (int(interval_right), int(interval_right_top)),
                     (int(interval_right), int(interval_right_bottom)), (0, 255, 0))
            cv2.line(src_temp, (int(interval_right), int(interval_right_bottom)),
                     (int(interval_left), int(interval_left_bottom)), (0, 255, 0))
            cv2.line(src_temp, (int(interval_left), int(interval_left_bottom)),
                     (int(interval_left), int(interval_left_top)),
                     (0, 255, 0))

            pts2 = np.float32(
                [[0, 0], [interval_dst_width, 0], [0, interval_dst_height], [interval_dst_width, interval_dst_height]])

            M = cv2.getPerspectiveTransform(pts1, pts2)
            dst_interval = cv2.warpPerspective(src, M, (interval_dst_width, interval_dst_height))

            if tb == "bottom":
                dst_col[k * interval_dst_height:(k + 1) * interval_dst_height, :, :] = dst_interval
            elif tb == "up":
                dst_col[dst_height - (k + 1) * interval_dst_height:dst_height - k * interval_dst_height, :, :] = dst_interval

        if lr == "left":
            dst[:, 0:init_interval_length, :] = dst_col
            dst = np.hstack((np.zeros((dst_height, init_interval_length, 3)), dst))
        elif lr == "right":
            dst[:, dst.shape[1] - init_interval_length:dst.shape[1], :] = dst_col
            dst = np.hstack((dst, np.zeros((dst_height, init_interval_length, 3))))

        total_interval_width = total_interval_width + interval_width
        interval_width = int(interval_width * region_width_decay + 0.5)
        if interval_width < min_interval_length:
            interval_width = min_interval_length
        elif lr == "left" and interval_width > interval_left - leftmost:
            interval_width = interval_left - leftmost
        elif lr == "right" and interval_width > rightmost - interval_left:
            interval_width = rightmost - interval_left

        if lr == "left":
            interval_right = interval_left
            interval_left = interval_right - interval_width
        elif lr == "right":
            interval_left = interval_right
            interval_right = interval_right + interval_width

    if show:
        cv2.imshow(lr + tb, src_temp)

    # post processing
    dst = postProcess(dst)
    return dst


if __name__ == "__main__":
    # ******************************* processing input argv *******************************
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    try:
        options, args = getopt.getopt(sys.argv[3:], "o:s",
                                      ["output=", "show", "middle_region_ratio=", "region_width_decay=",
                                       "min_width_ratio=", "region_height_ratio="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    src_path = sys.argv[1]
    mask_path = sys.argv[2]
    output_path = "result.jpg"
    show = False
    middle_region_ratio = 0.2
    region_width_decay = 0.85
    min_width_ratio = 0.2
    region_height_ratio = 0.2
    for name, value in options:
        if name in ("-o", "--output"):
            output_path = value
        if name in ("-s", "--show"):
            show = True
        if name == "--middle_region_ratio":
            middle_region_ratio = float(value)
        if name == "--region_width_decay":
            region_width_decay = float(value)
        if name == "--min_width_ratio":
            min_width_ratio = float(value)
        if name == "--region_height_ratio":
            region_height_ratio = float(value)

    print("output_path is: " + output_path)
    print("middle_region_ratio is: " + str(middle_region_ratio))
    print("region_width_decay is: " + str(region_width_decay))
    print("min_width_ratio is: " + str(min_width_ratio))
    print("region_height_ratio is: " + str(region_height_ratio))

    # ******************************* find roi boundary according to mask **********************************
    # read and resize the mask
    src = cv2.imread(src_path)
    mask = cv2.imread(mask_path)

    mask_temp = np.copy(mask)
    src_temp = np.copy(src)
    src_gray = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)

    h, w = mask_gray.shape[:2]
    print("the mask shape is " + str(mask_gray.shape))
    if show:
        cv2.imshow("gray mask", mask_gray)

    # find the top, bottom, leftmost and rightmost point in mask
    # top
    mask_top = np.argmax(mask_gray, axis=0)
    top = np.min(mask_top[mask_top > 0])
    cv2.line(mask_temp, (0, top), (w, top), (0, 255, 0))
    for i, v in enumerate(mask_top):
        mask[v][i][:] = [0, 255, 0]

    # bottom
    mask_bottom = h - np.argmax(mask_gray[::-1], axis=0)
    bottom = np.max(mask_bottom[mask_bottom < h])
    cv2.line(mask_temp, (0, bottom), (w, bottom), (0, 255, 0))

    # leftmost
    mask_left = np.argmax(mask_gray, axis=1)
    leftmost = np.min(mask_left[mask_left > 0])
    cv2.line(mask_temp, (leftmost, 0), (leftmost, h), (0, 255, 0))

    # rightmost
    mask_right = w - np.argmax(np.fliplr(mask_gray), axis=1)
    rightmost = np.max(mask_right[mask_right < w])
    cv2.line(mask_temp, (rightmost, 0), (rightmost, h), (0, 255, 0))

    # middle
    mid_col = int((leftmost + rightmost) / 2 + 0.5)
    mid_row = int((top + bottom) / 2 + 0.5)
    cv2.line(mask_temp, (mid_col, 0), (mid_col, h), (0, 255, 0))
    cv2.line(mask_temp, (0, mid_row), (w, mid_row), (0, 255, 0))

    if show:
        cv2.imshow("border", mask_temp)

    # ******************************* partition the roi and warp every region **********************************
    left_bottom_dst = flattenArea("left", "bottom", middle_region_ratio, region_width_decay, min_width_ratio, region_height_ratio)
    left_up_dst = flattenArea("left", "up", middle_region_ratio, region_width_decay, min_width_ratio, region_height_ratio)
    right_bottom_dst = flattenArea("right", "bottom", middle_region_ratio, region_width_decay, min_width_ratio, region_height_ratio)
    right_up_dst = flattenArea("right", "up", middle_region_ratio, region_width_decay, min_width_ratio, region_height_ratio)

    print("the shape of left-bottom area is " + str(left_bottom_dst.shape))
    print("the shape of left-up area is " + str(left_up_dst.shape))
    print("the shape of right-bottom area is " + str(right_bottom_dst.shape))
    print("the shape of right-up area is " + str(right_up_dst.shape))

    dst = np.hstack((np.vstack((left_up_dst, left_bottom_dst)), np.vstack((right_up_dst, right_bottom_dst))))
    cv2.imwrite(output_path, dst)

    if show:
        dst_img = cv2.imread(output_path)
        cv2.imshow("result", dst_img)

    cv2.waitKey(0)
