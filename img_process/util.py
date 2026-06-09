def complete_img(image, padding, padding_y=0, background=255):
    padding_y = padding if padding_y == 0 else padding_y
    
    complete_arr = []
    
    for index_x, x in enumerate(image):
        complete_arr.append([background])
        for index_y, y in enumerate(x):
            if index_y <  padding - 1:
                complete_arr[index_x].insert(0, background)
            complete_arr[index_x].append(y)
        for i in range(padding_y):
            complete_arr[index_x].append(background)
        
        
    return complete_arr