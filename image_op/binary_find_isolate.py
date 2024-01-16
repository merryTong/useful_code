import numpy as np

def find_isolated_points(img_mask):

    img_pad = np.full((img_mask.shape[0]+2, img_mask.shape[1]+2), 0)
    img_pad[1:-1, 1:-1] = img_mask

    up_bound = abs(img_pad[1:-1, 1:-1] - img_pad[:-2, 1:-1])
    down_bound = abs(img_pad[1:-1, 1:-1] - img_pad[2:, 1:-1])
    left_bound = abs(img_pad[1:-1, 1:-1] - img_pad[1:-1, :-2])
    right_bound = abs(img_pad[1:-1, 1:-1] - img_pad[1:-1, 2:])

    up_bound = up_bound[...,np.newaxis]
    down_bound = down_bound[...,np.newaxis]
    left_bound = left_bound[...,np.newaxis]
    right_bound = right_bound[...,np.newaxis]
    bounds_map = np.concatenate((up_bound, down_bound, left_bound, right_bound), axis=-1)
    bounds_map = np.sum(bounds_map, axis=-1)
    print(bounds_map, bounds_map.shape)
    img_mask[bounds_map == 4] = 0
    return img_mask