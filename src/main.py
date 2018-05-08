import sys
import os
import numpy as np
import re

from PIL import Image
from random import randint

max_tree_depth = 0
color_depth = 0
variance_max = 0
output = []
variance_file = ''

class QNode:
    def __init__(self, isLeaf, parent):
        self.parent = parent
        self.isLeaf = isLeaf
        self.NW = None
        self.NE = None
        self.SE = None
        self.SW = None
        self.lvl = None

def create_tree(arr, node, current_depth):

    # print(arr)
    global color_depth
    global max_tree_depth
    global output
    global variance_file
    height = arr.shape[0]
    width = arr.shape[1]
    if width > height:
        aux = height
        height = width
        width = aux

    if height > 1 and width > 1:

        half_height = int(height/2)
        half_width = int(width/2)
        arrNW = arr[0:half_width, 0:half_height]
        # print(arrNW)
        NW_avg_lvl = int(np.average(arrNW)*color_depth)
        NW_var = np.var(arrNW)

        arrSW = arr[half_width:width, 0:half_height]
        # print(arrSW)
        SW_avg_lvl = int(np.average(arrSW)*color_depth)
        SW_var = np.var(arrSW)

        arrSE = arr[half_width:width, half_height:height]
        # print(arrSE)
        SE_avg_lvl = int(np.average(arrSE) * color_depth)
        SE_var = np.var(arrSE)

        arrNE = arr[0:half_width, half_height:height]
        # print(arrNE)
        NE_avg_lvl = int(np.average(arrNE) * color_depth)
        NE_var = np.var(arrNE)
        variance_file.write(str(NW_var) + " - " + str(NE_var) + " - " + str(SE_var) + " - " + str(SW_var) + "\n")
        if current_depth < max_tree_depth:
            current_depth += 1

            if NW_var >= variance_max and current_depth < max_tree_depth:
                if arrNW.shape[0] > 1 and arrNW.shape[1] > 1:
                    node.NW = QNode(False, node)
                    output.append("NW [")
                    create_tree(arrNW, node.NW, current_depth)
                    output.append("]")
                else:
                    output.append("NW " + str(NW_avg_lvl))
            else:
                node.NW = QNode(True, node)
                output.append("NW " + str(NW_avg_lvl))
                node.NW.lvl = NW_avg_lvl

            if NE_var >= variance_max and current_depth < max_tree_depth:
                if arrNE.shape[0] > 1 and arrNE.shape[1] > 1:
                    node.NE = QNode(False, node)
                    output.append("NE [")
                    create_tree(arrNE, node.NE, current_depth)
                    output.append("]")
                else:
                    output.append("NE " + str(NE_avg_lvl))
            else:
                node.NE = QNode(True, node)
                output.append("NE " + str(NE_avg_lvl))
                node.NE.lvl = NE_avg_lvl

            if SE_var >= variance_max and current_depth < max_tree_depth:
                if arrSE.shape[0] > 1 and arrSE.shape[1] > 1:
                    node.SE = QNode(False, node)
                    output.append("SE [")
                    create_tree(arrSE, node.SE, current_depth)
                    output.append("]")
                else:
                    output.append("SE " + str(SE_avg_lvl))
            else:
                node.SE = QNode(True, node)
                output.append("SE " + str(SE_avg_lvl))
                node.SE.lvl = SE_avg_lvl

            if SW_var >= variance_max and current_depth < max_tree_depth:
                if arrSW.shape[0] > 1 and arrSW.shape[1] > 1:
                    node.SW = QNode(False, node)
                    output.append("SW [")
                    create_tree(arrSW, node.SW, current_depth)
                    output.append("]")
                else:
                    output.append("SW " + str(SW_avg_lvl))
            else:
                node.SW = QNode(True, node)
                output.append("SW " + str(SW_avg_lvl))
                node.SW.lvl = SW_avg_lvl

        else:
            node.isLeaf = True
            node.lvl = int(np.average(arr)*color_depth)
            output.append(str(node.lvl))

    else:
        node.isLeaf = True
        node.lvl = int(np.average(arr) * color_depth)
        output.append(str(node.lvl))

def rgb_to_cmyk(arr):
    r = arr[0]
    g = arr[1]
    b = arr[2]
    if (r == 0) and (g == 0) and (b == 0):
        return [0, 0, 0, 1]
    c = 1 - r / 255.
    m = 1 - g / 255.
    y = 1 - b / 255.

    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    return [c, m, y, k]


def create_lists():
    out_lst = []
    aux = []
    global color_depth
    for i in range(1, color_depth):
        # print(i)
        del(aux[:])
        # print(aux)
        aux.append("Color Number: " + str(i))
        # print(aux)
        aux.append("----------")
        # print(len(output))
        for line in output:
            # print(line)
            if re.search("\[", re.escape(line)):
                s = line
                aux.append(s)
            elif re.search("\]", line):
                # if re.search("\[", re.escape(aux[-1])):
                #     print(aux[-1], " Removing!")
                #     aux.remove(aux[-1])
                # else:
                    aux.append(line)
                    # print(aux[-1], "Added")
            else:
                x = [int(s) for s in line.split() if s.isdigit()]
                x = x[0]
                if x >= i:
                    # print(x, "-", i)
                    s = line.replace(str(x), "")
                    aux.append(s)
        tabs = 0
        for j in range(0, len(aux)):
            if re.search("\[", re.escape(aux[j])):
                #print(tabs)
                aux[j] = build_tabs(tabs) + aux[j]
                tabs += 1
            elif re.search("\]", re.escape(aux[j])):
                tabs -= 1
                aux[j] = build_tabs(tabs) + aux[j]
            else:
                aux[j] = build_tabs(tabs) + aux[j]
        aux.append("----------")
        # print(len(aux))
        # print(i)
        # print(aux[0])
        # for line in aux:
        #     file.write(line)
        #     file.write("\n")
        out_lst.append(aux.copy())

    # print(np.shape(out_lst))
    # print(out_lst)
    #print(out_lst)
    # for i in range(0, color_depth-1):
    #     print(i)
    #     for line in out_lst[i]:
    #         file.write(line)
    #         file.write("\n")
    # file.close()
    return out_lst

def build_tabs(tabs):
    s = ""
    for i in range(0, tabs):
        s += "  "
    return s

def remove_empty(lst):
    for item in lst:
        # print(len(item))
        # print(item)
        index_lst = []
        changed = True
        while changed:
            index_lst = []
            changed = False
            for i in range(0, len(item)):
                # print(i)
                line = item[i]
                if re.search("\]", line):
                    before = item[i-1]
                    if re.search("\[", before):
                        # print("Removing: ", before, line)
                        index_lst.append(i-1)
                        index_lst.append(i)
                        changed = True
            # print("Indexes=" + str(len(index_lst)))
            # print(sorted(index_lst, reverse=True))

            for i in sorted(index_lst, reverse=True):
                stri = str(len(item)) + " "
                del item[i]
                # print(stri + str(len(item)))

    return lst


def main():
    if len(sys.argv) == 6:
        script_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_path)
        dirname = os.getcwd()
        dire = os.path.join(dirname, sys.argv[1])
        im = Image.open(dire)
        img_arr = np.array(im)
        global color_depth
        color_depth = int(sys.argv[2])
        global max_tree_depth
        max_tree_depth = int(sys.argv[3])
        global variance_max
        variance_max = float(sys.argv[4])
        global output
        global variance_file
        variance_file = open("variance.txt", "w")

        if sys.argv[5] in ["no", "n", "N", "0", "nope", "false", "False"]:
            img = img_arr[:, :, 0]
            img[0:img.shape[0], 0:img.shape[1]] = 255 - img[0:img.shape[0], 0:img.shape[1]]
            img = img/255
            root = QNode(False, None)
            output = []
            create_tree(img, root, 0)
            result = create_lists()
            result = remove_empty(result)
            file_name = os.path.splitext(sys.argv[1])[0] + ".txt"
            file = open(file_name, "w")
            file.write("-------------\nQuad for GRAYSCALE\n-------------\n")
            for item in result:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

        else:
            img_cmyk = np.apply_along_axis(rgb_to_cmyk, 2, img_arr)
            img_c = img_cmyk[:, :, 0]
            img_m = img_cmyk[:, :, 1]
            img_y = img_cmyk[:, :, 2]
            img_k = img_cmyk[:, :, 3]

            output = []
            root_c = QNode(False, None)
            create_tree(img_c, root_c, 0)
            result = create_lists()
            result = remove_empty(result)
            file_name = os.path.splitext(sys.argv[1])[0] + "_c.txt"
            file = open(file_name, "w")
            file.write("-------------\nQuad for color channel CYAN\n-------------\n")
            for item in result:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

            output = []
            root_m = QNode(False, None)
            create_tree(img_m, root_m, 0)
            result = create_lists()
            result = remove_empty(result)
            file_name = os.path.splitext(sys.argv[1])[0] + "_m.txt"
            file = open(file_name, "w")
            file.write("-------------\nQuad for color channel MAGENTA\n-------------\n")
            for item in result:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

            output = []
            root_y = QNode(False, None)
            create_tree(img_y, root_y, 0)
            result = create_lists()
            result = remove_empty(result)
            file_name = os.path.splitext(sys.argv[1])[0] + "_y.txt"
            file = open(file_name, "w")
            file.write("-------------\nQuad for color channel YELLOW\n-------------\n")
            for item in result:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()

            output = []
            root_k = QNode(False, None)
            create_tree(img_k, root_k, 0)
            result = create_lists()
            result = remove_empty(result)
            file_name = os.path.splitext(sys.argv[1])[0] + "_k.txt"
            file = open(file_name, "w")
            file.write("-------------\nQuad for color channel KEY/BLACK\n-------------\n")
            for item in result:
                for line in item:
                    file.write(line)
                    file.write("\n")
            file.close()
        variance_file.close()


    else:
        print("Argument list incorrect. Please try again")
        sys.exit(0)

if __name__ == '__main__':
    main()
