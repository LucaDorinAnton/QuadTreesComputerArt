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

    global color_depth, max_tree_depth, output, variance_file, variance_max
    curr = arr[y1:y2, x1:x2]
    c = np.average(curr[:,:, 0])
    m = np.average(curr[:, :, 1])
    y = np.average(curr[:, :, 2])
    k = np.average(curr[:, :, 3])
    color_lvl = [c, m, y, k]
    curr_variance = np.var(curr)
    variance_file.write(str(curr_variance) + "\n")
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
            for i in range(0, 4):
                output[i].append("NW [")
            create_tree(arr, NW, current_depth, x1, y1, avg_x, avg_y, "NW ")
            for i in range(0, 4):
                output[i].append("]")

            for i in range(0, 4):
                output[i].append("NE [")
            create_tree(arr, NE, current_depth, x1, avg_y, avg_x, y2, "NE ")
            for i in range(0, 4):
                output[i].append("]")

            for i in range(0, 4):
                output[i].append("SE [")
            create_tree(arr, SE, current_depth, avg_x, avg_y, x2, y2, "SE ")
            for i in range(0, 4):
                output[i].append("]")

            for i in range(0, 4):
                output[i].append("SW [")
            create_tree(arr, SW, current_depth, avg_x, y1, x2, avg_y, "SW ")
            for i in range(0, 4):
                output[i].append("]")

        else:
            c_int = int(color_lvl[0]*color_depth)
            m_int = int(color_lvl[1]*color_depth)
            y_int = int(color_lvl[2]*color_depth)
            k_int = int(color_lvl[3]*color_depth)
            output[0].append(direction + str(c_int))
            output[1].append(direction + str(m_int))
            output[2].append(direction + str(y_int))
            output[3].append(direction + str(k_int))
            node.set_leaf(color_lvl, x1, y1, x2, y2)
    else:
        c_int = int(color_lvl[0] * color_depth)
        m_int = int(color_lvl[1] * color_depth)
        y_int = int(color_lvl[2] * color_depth)
        k_int = int(color_lvl[3] * color_depth)
        output[0].append(direction + str(c_int))
        output[1].append(direction + str(m_int))
        output[2].append(direction + str(y_int))
        output[3].append(direction + str(k_int))
        node.set_leaf(color_lvl, x1, y1, x2, y2)

# By using the output from the create_tree function
# Generate the text lists for each color


def create_lists(lst):
    out_lst = []
    aux = []
    global color_depth
    if re.search("All", lst[0]):
        return [["Incompatible parameters. Please change parameters for a better result"]]
    else:
        for i in range(1, color_depth):
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


def parse_tree(node, draw):
    global count, mode
    if not node.is_leaf:
        parse_tree(node.NW, draw)
        parse_tree(node.SW, draw)
        parse_tree(node.SE, draw)
        parse_tree(node.NE, draw)
    else:
        if mode == "COLOR":
            pixel = cmyk_to_rgb(node.color_lvl)
        else:
            gray = int(node.color_lvl[3]*255)
            pixel = (gray, gray, gray)

        draw.rectangle((node.x1, node.y1, node.x2, node.y2), fill=pixel, outline=(0, 0, 0))

        count += 1

# Various conversion helepr functions


def cmyk_to_rgb(x):

    c = x[0]
    m = x[1]
    y = x[2]
    k = x[3]
    r = int(255 * (1 - c))
    g = int(255 * (1 - m))
    b = int(255 * (1 - y))
    return r, g, b


def cmyk_to_grayscale(x):
    c = x[0]
    m = x[1]
    y = x[2]
    k = x[3]
    c = c * (1 - k) + k
    m = m * (1 - k) + k
    y = y * (1 - k) + k

    r, g, b = (1 - c), (1 - m), (1 - y)
    y = 0.299 * r + 0.587 * g + 0.114 * b
    return [0.0, 0.0, 0.0, y]


def rgb_to_grayscale(x):
    r = int(x[0])
    g = int(x[1])
    b = int(x[2])
    mean = int((r + b + g)/3)
    return np.array([mean, mean, mean, mean])


def main():
    global color_depth, max_tree_depth, variance_max, output, variance_file, width1, height1, mode

    script_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_path)
    img_dir = os.path.join(script_path, "images")

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    text_dir = os.path.join(script_path, "texts")
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    variance_file = open("variance.txt", "w")

    if len(sys.argv) == 6:

        img_file = sys.argv[1]
        color_depth = int(sys.argv[2])
        max_tree_depth = int(sys.argv[3])
        variance_max = float(sys.argv[4])
        dire = os.path.join(script_path, img_file)
        im = Image.open(dire)
        im = im.convert("CMYK")
        img_arr = np.array(im)
        img_arr = img_arr / 255 * color_depth
        img_arr = img_arr.astype(int)
        img_arr = img_arr / color_depth
        width1, height1 = im.size
        output = [[], [], [], []]

        if sys.argv[5] in ["no", "n", "N", "0", "nope", "false", "False"]:
            mode = "GRAYSCALE"
            img_arr = np.apply_along_axis(cmyk_to_grayscale, 2, img_arr)

            root = QNode(None)
            create_tree(img_arr, root, 0, 0, 0, width1, height1, "All: ")
            result = create_lists(output[3])
            image2 = Image.new("RGB", (width1, height1))
            draw = ImageDraw.Draw(image2)
            parse_tree(root, draw)
            path = os.path.splitext(img_file)[0] + "_grayscale_quad.jpg"
            os.chdir(img_dir)
            image2.save(path, options="w")

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
            create_tree(img_arr, root, 0, 0, 0, width1, height1, "All: ")
            image2 = Image.new("RGB", (width1, height1))
            draw = ImageDraw.Draw(image2)
            parse_tree(root, draw)
            img_path = os.path.splitext(img_file)[0]
            path_color = img_path + "_color_quad.jpg"
            path_c = img_path + "_c_quad.jpg"
            path_m = img_path + "_m_quad.jpg"
            path_y = img_path + "_y_quad.jpg"
            path_k = img_path + "_k_quad.jpg"
            os.chdir(img_dir)
            image2.save(path_color, options="w")
            image2 = image2.convert("CMYK")
            img_cmyk = np.array(image2)
            img_c = img_cmyk[:, :, 0]
            im_c = Image.new("CMYK", (width1, height1))
            for i in range(0, height1):
                for j in range(0, width1):
                    im_c.putpixel((j, i), (img_c[i, j], 0, 0, 0))
            im_c.save(path_c, options="w")
            img_m = img_cmyk[:, :, 1]
            im_m = Image.new("CMYK", (width1, height1))
            for i in range(0, height1):
                for j in range(0, width1):
                    im_m.putpixel((j, i), (0, img_m[i, j], 0, 0))
            im_m.save(path_m, options="w")
            img_y = img_cmyk[:, :, 2]
            im_y = Image.new("CMYK", (width1, height1))
            for i in range(0, height1):
                for j in range(0, width1):
                    im_y.putpixel((j, i), (0, 0, img_y[i, j], 0))
            im_y.save(path_y, options="w")
            img_k = img_cmyk[:, :, 3]
            im_k = Image.new("CMYK", (width1, height1))
            for i in range(0, height1):
                for j in range(0, width1):
                    im_k.putpixel((j, i), (0, 0, 0, img_k[i, j]))
            im_k.save(path_k, options="w")

            path_c = img_path + "_c_quad.txt"
            path_m = img_path + "_m_quad.txt"
            path_y = img_path + "_y_quad.txt"
            path_k = img_path + "_k_quad.txt"

            result_c = create_lists(output[0])
            result_m = create_lists(output[1])
            result_y = create_lists(output[2])
            result_k = create_lists(output[3])
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

        variance_file.close()

    else:
        variance_file.write("Argument List incorrect. Please try again.")
        variance_file.close()
        sys.exit(0)


if __name__ == '__main__':
    main()
