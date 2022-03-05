def result2ppformat(boxes, txts, scores):
    lines = []
    for i in range(len(boxes)):
        box = boxes[i]
        txt = txts[i]
        score = scores[i]
        line = [box, (txt, score)]
        lines.append(line)
    return lines


def parse_result(crop_ocr_result):
    boxes = [line[0] for line in crop_ocr_result]
    txts = [line[1][0] for line in crop_ocr_result]
    scores = [line[1][1] for line in crop_ocr_result]
    return boxes, txts, scores
