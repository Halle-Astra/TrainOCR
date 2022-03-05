import os, sys
from .utils import ImageContainer, VideoContainer
from .utils.Region import TrainMask
from .utils.tools_ppocr import parse_result, result2ppformat
import cv2
import glob
import shutil
import numpy as np
from PIL import Image
from easydict import EasyDict
from paddleocr import PaddleOCR, draw_ocr


class _Basic():
    def __init__(self, args):
        self.ppocr = PaddleOCR(use_angle_cls=True,
                               use_gpu=args.use_gpu,
                               det_model_dir=args.det_model_dir,
                               rec_model_dir=args.rec_model_dir,
                               gpu_mem=args.gpu_mem)
        self.current = EasyDict()

    def run(self):
        try:
            print('Train OCR started.')
            results = []
            for img in self.frame_provider:
                result = self.process(img)
                results.append(result)
        except KeyboardInterrupt as e:
            print(e)
            exit()
        return results

    def __call__(self):
        results = self.run()
        return results

    def __del__(self):
        if hasattr(self.frame_provider, 'ecflag') and self.frame_provider.ecflag:
            if self.show_flag:
                cv2.destroyAllWindows()
            # origin_name, origin_ext = os.path.splitext(self.origin)
            mp4_path = 'temp.mp4'
            self.frame_provider.cap.release()
            shutil.move(mp4_path, self.origin)

    def build_frame_provider(self, origin):
        if not os.path.exists(origin):
            print(origin + ' is not existing!')
            exit()

        if isinstance(origin, int):
            frame_provider = VideoContainer(origin)
        elif isinstance(origin, str):
            if os.path.isfile(origin):
                frame_provider = VideoContainer(origin)
            elif os.path.isdir(origin):
                files = []
                for ext in ['jpg', 'JPG', 'png', 'PNG', 'jpeg', 'JPEG']:
                    imgs_ = glob.glob(origin + '/.' + ext)
                    files += imgs_
                frame_provider = ImageContainer(files)
        elif isinstance(origin, list):
            frame_provider = ImageContainer(origin)
        else:
            print('Original input must be one of WebCamera, video file, images root or images list.')
            exit()
        return frame_provider

    @property
    def empty_box(self):
        return [[0, 0], [0, 0], [0, 0], [0, 0]]

    @property
    def empty_result(self):
        return [[self.empty_box, (' ', 0)]]

    def ocr(self, img):
        """单独的ocr模块，方便优化"""
        result = self.ppocr.ocr(img)
        return result


class TrainOCR(_Basic):
    def __init__(self, args):  # origin: [list, int, str], line_left, line_right,img_height, img_wide):
        super().__init__(args)
        self.frame_provider = self.build_frame_provider(args.origin)
        self.train_mask = TrainMask(args.line_left, args.line_right,
                                    # 'Cause fixed image size, all inputs must be the same size.
                                    args.img_height, args.img_wide)
        self.img_height, self.img_wide = args.img_height, args.img_wide
        self.stride = args.stride
        self.crop_height = args.crop_height
        self.origin = args.origin
        self.show_flag = args.show
        self.stride_num = args.stride_num
        if self.stride_num < 0:
            self.stride_num = 1000
        file_name = os.path.split(self.origin)[-1]
        file_name, _ = os.path.splitext(file_name)
        self.frames_root = os.path.splitext(args.origin)[0]
        self.result_file = os.path.splitext(args.origin)[0] + '.txt'
        os.makedirs(self.frames_root, exist_ok=True)

        f = open(self.result_file, 'w')
        f.write('')
        f.close()

    def process(self, orignImg):
        """自下而上文字识别"""
        img = self.train_mask.apply_mask(orignImg)
        y_ls = np.arange(0, self.img_height, self.stride)
        y_ls = self.img_height - y_ls

        results = []
        for i in range(min(y_ls.size, self.stride_num)):
            bottom = y_ls[i]
            top = bottom - self.crop_height
            if top < 0:
                continue
            crop, left, right = self.train_mask.crop(img, top, bottom)
            crop_ocr_result = self.ocr(crop)
            results.append(crop_ocr_result)
        results = self.results_fix(results, top, left)
        if self.show_flag:
            self.show(img, results)
        self.save(results, orignImg)
        return self.current.results

    def boxes_fix(self, boxes, top, left):
        for i in range(len(boxes)):
            bbox = boxes[i]
            if bbox == self.empty_box:
                continue
            bbox = np.array(bbox)
            bbox[:, 1] += top
            bbox[:, 0] += left
            boxes[i] = bbox.tolist()
        return boxes

    def results2saving_format(self, results):
        results_new = []
        if results:
            img_path = self.frame_provider.time + '.png'
            actResult = []
            for i in range(len(results)):
                result = results[i]
                if result == self.empty_result:
                    continue
                for j in range(len(result)):
                    region, actStrAndRate = result[j]
                    actResult.append(actStrAndRate[0])
            if len(actResult) == 0:
                return results_new
            result = {"url": img_path,
                      "time": self.frame_provider.time,
                      "result": actResult}
            results_new.append(result)
        return results_new

    def results_fix(self, results, top, left):
        results_new = []
        for result in results:
            if result == []:
                result = self.empty_result
                # continue

            boxes, txts, scores = parse_result(result)
            boxes = self.boxes_fix(boxes, top, left)
            result = result2ppformat(boxes, txts, scores)
            results_new.append(result)
        return results_new

    def show(self, img, results):
        if self.show_flag:
            for result in results:
                boxes, txts, scores = parse_result(result)
                img_temp = draw_ocr(img.copy(), boxes, txts, scores)
            cv2.imshow('train ocr', img_temp)
            cv2.waitKey(1)
        # else:
        #     cv2.imshow('train ocr', img)
        #     cv2.waitKey(1)

    def save(self, results, img):
        Image.fromarray(img).save(os.path.join(self.frames_root, self.frame_provider.time + '.png'))

        results = self.results2saving_format(results)
        self.current.results = results

        if results:
            results = [str(i) for i in results]
            results = '\n'.join(results) + '\n'
            f = open(self.result_file, 'a')
            f.write(results)
            f.close()
