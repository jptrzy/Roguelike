
def linear_gradient(start_color, end_color, n):
    color_list = []

    for i in range(1, n):
        color = []
        for j in range(3):
            color.append(int(start_color[j] + (float(i)/(n-1))*(end_color[j]-start_color[j])))
        color_list.append(color)

    #s.insert(0, 255)    # NO TRANSPARENCY SET, MUST DEFINE
    color_list.insert(0, start_color)
    return color_list

def blend(colors, strength):
    # blend( [color1, color2, ... ] , [color1str, color2str, ... ]    )
    total_str = 0
    
    for i in range(len(colors)):
        total_str += strength[i]

    if total_str == 0:
        return [0,0,0]
        
    mean = []

    for j in range(3):
        mean_j = 0
        for i in range(len(colors)):
            mean_j += colors[i][j]*strength[i]
        mean.append(int(mean_j / total_str))

    return mean