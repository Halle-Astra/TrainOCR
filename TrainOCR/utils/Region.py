import cv2
import numpy as np
from .utils import express_line_and_inverse

class TrainMask:
    def __init__(self,line_left, line_right, img_height=1080, img_wide=1920):
        [[self.x_top_left, self.y_top_left],
         [self.x_bottom_left, self.y_bottom_left]] = line_left
        [[self.x_top_right, self.y_top_right],
         [self.x_bottom_right, self.y_bottom_right]] = line_right
        self.img_height, self.img_wide = img_height, img_wide
        self.line_left, self.line_left_inverese, self.line_right, self.line_right_inverse = self.build_func_line()
        self.mask = self.compute_mask()

    def build_func_line(self):
        line_left, line_left_inverse = express_line_and_inverse(self.x_top_left, self.y_top_left,
                                      self.x_bottom_left, self.y_bottom_left)
        line_right, line_right_inverse = express_line_and_inverse(self.x_top_right, self.y_top_right,
                                       self.x_bottom_right, self.y_bottom_right)
        return line_left, line_left_inverse, line_right, line_right_inverse

    def compute_mask(self):
        X, Y = np.meshgrid(np.arange(self.img_wide),
                                       np.arange(self.img_height))
        mask_left = Y<self.line_left(X)
        mask_right = Y<self.line_right(X)
        mask = mask_left+mask_right
        mask = 1-np.minimum(mask, 1)
        mask = np.transpose([mask,mask,mask], (1,2,0))
        return mask

    def apply_mask(self,img):
        return (img*self.mask).astype(np.uint8)

    def crop(self, img, top, bottom):
        left = self.line_left_inverese(bottom)
        right = self.line_right_inverse(bottom)
        left = int(left)
        right = int(right)
        crop_ = img[top:bottom, left:right]
        return crop_,left ,right






