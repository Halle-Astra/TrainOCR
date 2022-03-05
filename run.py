from TrainOCR import TrainOCR
import json
import os,sys
import argparse
from easydict import EasyDict
# sys.path.append(os.path.dirname(__file__)+os.sep+'../')

# os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('--config', default='',type=str,
                      help='the path to the configuration. Other arguments will be ignored when it is provided.')
    args.add_argument('--origin',
                      type=str, help='the path to the video.')
    args.add_argument('--line_left',
                      type=list, help='line represented by [[x1,y1],[x2,y2]] format.',default=[[724,0],[288,1080]])
    args.add_argument('--line_right',
                      type=list, help='line represented by [[x1,y1],[x2,y2]] format.',default=[[1169,0],[1666,1080]])
    args.add_argument('--img_height',
                      type=int, help='height of image',default=1080)
    args.add_argument('--img_wide',
                      type=int, help='wide of image',default=1920)
    args.add_argument('--stride',
                      type=int, help='stride of vertical sliding.',default=50)
    args.add_argument('--crop_height',
                      type=int, help='height of crop for OCR.',default=90)
    args.add_argument('--show',
                      type=int, help='height of crop for OCR.',default=True)
    args.add_argument('--stride_num',
                      type=int, help='height of crop for OCR.',default=20)

    args_cmd = args.parse_args()
    if args_cmd.config and os.path.exists(args_cmd.config):
        with open(args_cmd.config,encoding='utf-8') as f :
            args = json.load(f)
            args = EasyDict(args)

            for key in args.keys():
                if key in args_cmd and args_cmd.__getattribute__(key) is not None:
                    args[key] = args_cmd.__getattribute__(key)
    else:
        args = args_cmd

    train_ocr = TrainOCR(args)
    train_ocr.run()
