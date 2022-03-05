import cv2
import os
import shutil
from skimage import img_as_ubyte

def imread(img_path):
    img = cv2.imread(img_path)
    img = img[...,:3]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    if img.max()<=1:
        img = img_as_ubyte(img)
    img = img.astype('uint8')
    return img

def viopen(video_path):
    """Video Opening"""
    ecflag = False # ext change flag
    video_prefix, video_ext = os.path.splitext(video_path)
    if video_ext not in ['.mp4', '.MP4']:
        # new_path = video_prefix+'.mp4'
        new_path = 'temp.mp4'
        print(os.getcwd())
        shutil.copyfile(video_path, new_path)
        video_path = new_path
        ecflag = True
    vi = cv2.VideoCapture(video_path)
    return ecflag, vi

def express_line_and_inverse(x1, y1, x2 ,y2):
    k = (y2-y1)/(x2-x1)
    b = y1-k*x1
    y = lambda x: k*x+b
    x = lambda y: (y-b)/k
    return y, x

def ms2timeList(ms):
    seconds = int(ms/1000)
    ms = ms%1000
    minutes = int(seconds/60)
    seconds = seconds%60
    hours = int(minutes/60)
    minutes = minutes%60
    hours, minutes, seconds, ms = map(lambda i: str(int(i)), [hours, minutes, seconds, ms])
    return [hours, minutes, seconds, ms]

def time2timestr(timeList, delimiter):
    return delimiter.join(timeList)

def ms2timestr(ms, delimiter):
    time = ms2timeList(ms)
    time_str = time2timestr(time, delimiter)
    return time_str

class VideoContainer:
    def __init__(self, file_name):
        self.file_name = file_name
        try:
            self.file_name = int(file_name)
        except ValueError:
            pass

    def __iter__(self):
        if isinstance(self.file_name, int):
            self.cap = cv2.VideoCapture(self.file_name)
            self.ecflag = False
        else:
            self.ecflag, self.cap = viopen(self.file_name)
        if not self.cap.isOpened():
            raise IOError('Video {} cannot be opened'.format(self.file_name))
        return self

    def __next__(self):
        # 帧数截取间隔（每隔30帧截取一帧）
        frameRate = 100
        while(True):
            was_read, img = self.cap.read()
            if not was_read:
                raise StopIteration
            if(frameRate == 0):
                return img
            frameRate -=1
            # ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
            # time = ms2timestr(ms, '-')

    @property
    def time(self):
        ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        time = ms2timestr(ms, '-')
        return time

class ImageContainer:
    def __init__(self, file_names):# 这里需要自行修改
        self.file_names = file_names
        self.max_idx = len(file_names)

    def __iter__(self):
        self.idx=0
        self.ecflag = False
        return self

    def __next__(self):
        if self.idx == self.max_idx:
            raise StopIteration
        img = imread(self.file_names[self.idx])
        if img.size == 0:
            raise IOError('Image {} cannot be read'.format(self.file_names[self.idx]))
        self.idx = self.idx+1
        return img

    @property
    def time(self):
        """if ret-val is equal to -1, the first frame is not yet taken."""
        return self.idx-1
