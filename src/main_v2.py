import sys
import os
import numpy as np
import re

from PIL import Image
from PIL import ImageDraw

max_tree_depth = 0
color_depth = 0
variance_max = 0
width1 = 0
height1 = 0
output = []
variance_file = ''
count = 0
mode = "COLOR"
var_mode = "DIRECT"
line_mode = True
var_lst = []

# QNode represents a node in the QuadTree
# each QNode has 4 children
# if it a QNode is a leaf, it stores pixel information


class QNode:
    def __init__(self, parent):
        self.parent = parent
        self.NW = None
        self.NE = None
        self.SE = None
        self.SW = None
        self.is_leaf = False
        self.color_lvl = None
        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

    def set_leaf(self, color_lvl, x1, y1, x2, y2):
        self.is_leaf = True
        self.color_lvl = color_lvl
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

# starting from an array of pixels
# and a root node, recursivley create and calculate the Quadtree


def create_tree(arr, node, current_depth, x1, y1, x2, y2, direction):

    global color_depth, max_tree_depth, output, variance_file, variance_max, var_lst
    curr = arr[y1:y2, x1:x2]
    c = np.average(curr[:, :, 0])
    m = np.average(curr[:, :, 1])
    y = np.average(curr[:, :, 2])
    k = np.average(curr[:, :, 3])
    color_lvl = [c, m, y, k]
    curr_variance = get_variance(curr)
    variance_file.write(str(curr_variance) + "\n")
    var_lst.append(curr_variance)
    if x2 - x1 >= 2 and y2 - y1 >= 2 and current_depth <= max_tree_depth:
        if curr_variance >= variance_max:
            current_depth += 1
            avg_x = int(x1 + (x2-x1)/2)
            avg_y = int(y1 + (y2 - y1)/2)
            NW = QNode(node)
            NE = QNode(node)
            SE = QNode(node)
            SW = QNode(node)
            node.NW = NW
            node.NE = NE
            node.SE = SE
            node.SW = SW
            if direction != "All: ":
                for i in range(0, 4):
                    output[i].append(direction + " [")
            create_tree(arr, NW, current_depth, x1, y1, avg_x, avg_y, "NW ")
            create_tree(arr, NE, current_depth, avg_x, y1, x2, avg_y, "NE ")
            create_tree(arr, SE, current_depth, avg_x, avg_y, x2, y2, "SE ")
            create_tree(arr, SW, current_depth, x1, avg_y, avg_x, y2, "SW ")

            if direction != "All: ":
                for i in range(0, 4):
                    output[i].append("]")

        else:
            for i in range(0, 4):
                color_lvl[i] = int(round(color_lvl[i] * color_depth))
                color_lvl[i] = color_lvl[i]/color_depth
            c_int = color_depth - int(color_lvl[0]*color_depth)
            m_int = color_depth - int(color_lvl[1]*color_depth)
            y_int = color_depth - int(color_lvl[2]*color_depth)
            k_int = color_depth - int(color_lvl[3]*color_depth)
            output[0].append(direction + str(c_int))
            output[1].append(direction + str(m_int))
            output[2].append(direction + str(y_int))
            output[3].append(direction + str(k_int))
            node.set_leaf(color_lvl, x1, y1, x2, y2)
    else:
        for i in range(0, 4):
            color_lvl[i] = int(round(color_lvl[i] * color_depth))
            color_lvl[i] = color_lvl[i] / color_depth
        c_int = color_depth - int(color_lvl[0] * color_depth)
        m_int = color_depth - int(color_lvl[1] * color_depth)
        y_int = color_depth - int(color_lvl[2] * color_depth)
        k_int = color_depth - int(color_lvl[3] * color_depth)
        output[0].append(direction + str(c_int))
        output[1].append(direction + str(m_int))
        output[2].append(direction + str(y_int))
        output[3].append(direction + str(k_int))
        node.set_leaf(color_lvl, x1, y1, x2, y2)


def get_variance(arr):
    global var_mode
    if var_mode == "DIRECT":
        return np.var(arr)
    elif var_mode == "AVERAGE":
        c = np.var(arr[:, :, 0])
        m = np.var(arr[:, :, 1])
        y = np.var(arr[:, :, 2])
        k = np.var(arr[:, :, 3])
        return np.average([c, m, y, k])


# By using the output from the create_tree function
# Generate the text lists for each color


def create_lists(lst):
    for line in lst:
        print(line)
    out_lst = []
    aux = []
    global color_depth
    if re.search("All", lst[0]):
        return [["Incompatible parameters. Please change parameters for a better result"]]
    else:
        for i in range(1, color_depth + 1):
            del(aux[:])
            aux.append("Color Number: " + str(i))
            aux.append("----------")
            for line in lst:
                if re.search("\[", re.escape(line)):
                    s = line
                    aux.append(s)
                elif re.search("\]", line):
                        aux.append(line)
                else:
                    x = [int(s) for s in line.split() if s.isdigit()]
                    x = x[0]
                    print(x)
                    if x >= i:
                        s = line.replace(str(x), "")
                        aux.append(s)
            tabs = 0
            for j in range(0, len(aux)):
                if re.search("\[", re.escape(aux[j])):
                    aux[j] = build_tabs(tabs) + aux[j]
                    tabs += 1
                elif re.search("\]", re.escape(aux[j])):
                    tabs -= 1
                    aux[j] = build_tabs(tabs) + aux[j]
                else:
                    aux[j] = build_tabs(tabs) + aux[j]
            aux.append("----------")
            out_lst.append(aux.copy())

        return out_lst

# Build a string of tabs


def build_tabs(tabs):
    s = ""
    for i in range(0, tabs):
        s += "  "
    return s

# Remove the empty entries from the text list


def remove_empty(lst):
    for item in lst:
        changed = True
        while changed:
            index_lst = []
            changed = False
            for i in range(0, len(item)):
                line = item[i]
                if re.search("\]", line):
                    before = item[i-1]
                    if re.search("\[", before):
                        index_lst.append(i-1)
                        index_lst.append(i)
                        changed = True

            for i in sorted(index_lst, reverse=True):
                del item[i]

    return lst

# Go through the Quadtree and reconstruct the image


def parse_tree(node, draw, lvl):
    global count, mode, line_mode, color_depth
    if not node.is_leaf:
        parse_tree(node.NW, draw, lvl)
        parse_tree(node.SW, draw, lvl)
        parse_tree(node.SE, draw, lvl)
        parse_tree(node.NE, draw, lvl)
    else:
        if mode == "COLOR":
            channel_lvl_c = int(round(node.color_lvl[0] * color_depth))
            if color_depth - channel_lvl_c >= lvl:
                channel_lvl_c = color_depth - lvl
            channel_lvl_c = channel_lvl_c / color_depth

            channel_lvl_m = int(round(node.color_lvl[1] * color_depth))
            if color_depth - channel_lvl_m >= lvl:
                channel_lvl_m = color_depth - lvl
            channel_lvl_m = channel_lvl_m / color_depth

            channel_lvl_y = int(round(node.color_lvl[2] * color_depth))
            if color_depth - channel_lvl_y >= lvl:
                channel_lvl_y = color_depth - lvl
            channel_lvl_y = channel_lvl_y / color_depth

            channel_lvl_k = int(round(node.color_lvl[3] * color_depth))
            if color_depth - channel_lvl_k >= lvl:
                channel_lvl_k = color_depth - lvl
            channel_lvl_k = channel_lvl_k / color_depth

            cmyk_normalized = (channel_lvl_c, channel_lvl_m, channel_lvl_y, channel_lvl_k)
            c_normalized = (channel_lvl_c, 0, 0, 0)
            m_normalized = (0, channel_lvl_m, 0, 0)
            y_normalized = (0, 0, channel_lvl_y, 0)
            k_normalized = (0, 0, 0, channel_lvl_k)
            rgb_pixel = cmyk_to_rgb(cmyk_normalized)

            pixel_c = cmyk_to_rgb(c_normalized)
            pixel_m = cmyk_to_rgb(m_normalized)
            pixel_y = cmyk_to_rgb(y_normalized)
            pixel_k = cmyk_to_rgb(k_normalized)
            if line_mode:
                draw[0].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_c, outline=(0, 0, 0))
                draw[1].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_m, outline=(0, 0, 0))
                draw[2].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_y, outline=(0, 0, 0))
                draw[3].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_k, outline=(0, 0, 0))
                draw[4].rectangle((node.x1, node.y1, node.x2, node.y2), fill=rgb_pixel, outline=(0, 0, 0))
            else:
                draw[0].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_c)
                draw[1].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_m)
                draw[2].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_y)
                draw[3].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel_k)
                draw[4].rectangle((node.x1, node.y1, node.x2, node.y2), fill=rgb_pixel)

        else:
            # gray = int(round(node.color_lvl[3]*255))
            # pixel = (gray, gray, gray)
            # if line_mode:
            #     draws[0].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel, outline=(0, 0, 0))
            # else:
            #     draws[0].rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel)

            gray_lvl = int(round(node.color_lvl[3]*color_depth))
            # print(no_of_images)
            if color_depth - gray_lvl >= lvl:
                gray_lvl = color_depth - lvl
            gray = int(round(gray_lvl/color_depth*255))
            pixel = (gray, gray, gray)
            if line_mode:
                draw.rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel, outline=(0, 0, 0))
            else:
                draw.rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel)
        count += 1


def create_images(root, draws):
    global color_depth

    for i in range(1, color_depth + 1):
        parse_tree(root, draws[i - 1], i)

# Various conversion helper functions


def cmyk_to_byte(x):
    c = int(round(255 * x[0]))
    m = int(round(255 * x[1]))
    y = int(round(255 * x[2]))
    k = int(round(255 * x[3]))
    return  c, m, y, k


def cmyk_to_rgb(x):

    c = x[0]
    m = x[1]
    y = x[2]
    k = x[3]
    r = int(round(255 * (1 - c)))
    g = int(round(255 * (1 - m)))
    b = int(round(255 * (1 - y)))
    return r, g, b


def cmyk_to_grayscale(x):
    c = x[0] / 255
    m = x[1] / 255
    y = x[2] / 255
    k = x[3] / 255
    c = c * (1 - k) + k
    m = m * (1 - k) + k
    y = y * (1 - k) + k

    r, g, b = (1 - c), (1 - m), (1 - y)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return [0.0, 0.0, 0.0, y]


def rgb_to_grayscale(x):
    r = int(round(x[0]))
    g = int(round(x[1]))
    b = int(round(x[2]))
    mean = int((r + b + g)/3)
    return np.array([mean, mean, mean, mean])


def main():
    global color_depth, max_tree_depth, variance_max, output
    global variance_file, width1, height1, mode, var_mode
    global line_mode, var_lst

    script_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_path)
    img_dir = os.path.join(script_path, "images")

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    text_dir = os.path.join(script_path, "texts")
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    variance_file = open("variance.txt", "w")

    if len(sys.argv) == 8:

        img_file = sys.argv[1]
        color_depth = int(sys.argv[2]) - 1
        max_tree_depth = int(sys.argv[3])
        variance_max = float(sys.argv[4])
        if sys.argv[6] in ["no", "n", "N", "0", "nope", "false", "False"]:
            var_mode = "DIRECT"
        else:
            var_mode = "AVERAGE"
        if sys.argv[7] in ["no", "n", "N", "0", "nope", "false", "False"]:
            line_mode = False
        else:
            line_mode = True
        dire = os.path.join(script_path, img_file)
        im = Image.open(dire)
        im = im.convert("CMYK")
        img_arr = np.array(im)
        width1, height1 = im.size
        output = [[], [], [], []]

        if sys.argv[5] in ["no", "n", "N", "0", "nope", "false", "False"]:
            mode = "GRAYSCALE"
            img_arr = np.apply_along_axis(cmyk_to_grayscale, 2, img_arr)
            root = QNode(None)
            create_tree(img_arr, root, 0, 0, 0, width1, height1, "All: ")
            result = create_lists(output[3])
            remove_empty(result)
            images = []
            draws = []
            for i in range(0, color_depth):
                image2 = Image.new("RGB", (width1, height1), (255, 255, 255))
                draw = ImageDraw.Draw(image2)
                images.append(image2)
                draws.append(draw)
            create_images(root, draws)
            path = os.path.splitext(img_file)[0] + "_grayscale_quad_"
            os.chdir(img_dir)
            for i in range(0, color_depth):
                curr_path = path + str(i + 1) + ".jpg"
                images[i].save(curr_path, options="w")

            file_name = os.path.splitext(img_file)[0] + "_grayscale_quad.txt"
            os.chdir(text_dir)
            file = open(file_name, "w")
            file.write("-------------\nQuad for GRAYSCALE\n-------------\n")
            for item in result:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

        else:
            mode = "COLOR"
            root = QNode(None)
            img_arr = img_arr / 255
            create_tree(img_arr, root, 0, 0, 0, width1, height1, "All: ")
            img_path = os.path.splitext(img_file)[0]
            path_color = "_color_quad.jpg"
            path_c = "_c_quad.jpg"
            path_m = "_m_quad.jpg"
            path_y = "_y_quad.jpg"
            path_k = "_k_quad.jpg"
            path_lst = [path_c, path_m, path_y, path_k, path_color]
            suffix_lst = []
            for i in range(1, color_depth + 1):
                suffix_lst.append("-" + str(i))
            os.chdir(img_dir)
            images = []
            draws = []
            for i in range(0, color_depth):
                img_lst = []
                draw_lst = []
                for j in range(0, 5):
                    curr_img = Image.new("RGB", (width1, height1), (0, 0, 0, 1))
                    img_lst.append(curr_img)
                    curr_draw = ImageDraw.Draw(curr_img, mode="RGB")
                    draw_lst.append(curr_draw)
                images.append(img_lst)
                draws.append(draw_lst)

            create_images(root, draws)
            img_file_short = os.path.splitext(img_file)[0]
            for i in range(0, color_depth):
                for j in range(0, 5):
                    save_path = img_file_short + suffix_lst[i] + path_lst[j]
                    images[i][j].save(save_path, options="w")

            path_c = img_path + "_c_quad.txt"
            path_m = img_path + "_m_quad.txt"
            path_y = img_path + "_y_quad.txt"
            path_k = img_path + "_k_quad.txt"

            result_c = remove_empty(create_lists(output[0]))
            result_m = remove_empty(create_lists(output[1]))
            result_y = remove_empty(create_lists(output[2]))
            result_k = remove_empty(create_lists(output[3]))
            os.chdir(text_dir)

            file = open(path_c, "w")
            file.write("-------------\nQuad for CYAN\n-------------\n")
            for item in result_c:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

            file = open(path_m, "w")
            file.write("-------------\nQuad for MAGENTA\n-------------\n")
            for item in result_m:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

            file = open(path_y, "w")
            file.write("-------------\nQuad for YELLOW\n-------------\n")
            for item in result_y:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

            file = open(path_k, "w")
            file.write("-------------\nQuad for BLACK/KEY\n-------------\n")
            for item in result_k:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()
        avg_variance = np.average(var_lst)
        min_variance = np.min(var_lst)
        max_variance = np.max(var_lst)
        variance_file.write("Minimum variance: " + str(min_variance) + "\n")
        variance_file.write("Average variance: " + str(avg_variance) + "\n")
        variance_file.write("Maximum variance: " + str(max_variance) + "\n")
        variance_file.close()

    else:
        variance_file.write("Argument List incorrect. Please try again.")
        variance_file.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
