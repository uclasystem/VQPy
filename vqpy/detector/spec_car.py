# References:
# https://github.com/ibaiGorordo/ONNX-HybridNets-Multitask-Road-Detection
# https://github.com/PINTO0309/PINTO_model_zoo/tree/main/276_HybridNets
# using 384x512 model and anchors

from vqpy.detector.utils import onnx_inference
from vqpy.base.detector import DetectorBase
from vqpy.utils.classes import COCO_CLASSES
import numpy as np
from typing import Dict, List
import cv2
from vqpy.detector.logger import register
import os


input_width = 512
input_height = 384  # use hybridnets_384x512.onnx, hard code size for now
output_names = ["regression", "classification", "segmentation"]
anchor_name = "anchors_384x512.npy"
conf_thres = 0.5
iou_thres = 0.5


class SpecCarDetector(DetectorBase):
    """The detector for car detection"""

    cls_names = COCO_CLASSES
    output_fields = ["tlbr", "score", "class_id"]

    def inference(self, img: np.ndarray) -> List[Dict]:
        # TODO: allow loading multiple files from "model_path"
        anchor_path = os.path.join(os.path.dirname(self.model_path),
                                   anchor_name)
        processed_img = preprocess(img)
        detections = onnx_inference(processed_img, self.model_path)
        outputs = postprocess(detections, img.shape, anchor_path)
        return outputs


def preprocess(image):
    input_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Resize input image
    input_img = cv2.resize(input_img, (input_width, input_height))

    # Scale input pixel values to -1 to 1
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]
    input_img = (input_img / 255.0 - mean) / std
    input_img = input_img.transpose(2, 0, 1)
    input_tensor = input_img[np.newaxis, :, :, :].astype(np.float32)

    return input_tensor


def postprocess(detections, image_size, anchor_path):
    boxes = np.squeeze(detections[0])
    scores = np.squeeze(detections[1])

    anchors = np.squeeze(np.load(anchor_path))
    transformed_boxes = transform_boxes(boxes, anchors)
    filtered_boxes = transformed_boxes[scores > conf_thres]
    filtered_scores = scores[scores > conf_thres]

    filtered_boxes[:, [0, 2]] *= image_size[1] / input_width
    filtered_boxes[:, [1, 3]] *= image_size[0] / input_height

    filtered_boxes, filtered_scores = nms_fast(
        filtered_boxes, filtered_scores, iou_thres
    )

    rets = []
    for (tlbr, score) in zip(filtered_boxes, filtered_scores):
        # todo: convert dict to named tuple
        rets.append(
            {"tlbr": tlbr, "score": score, "class_id": 2}   # class_id for car
        )
    return rets


def transform_boxes(boxes, anchors):
    y_centers_a = (anchors[:, 0] + anchors[:, 2]) / 2
    x_centers_a = (anchors[:, 1] + anchors[:, 3]) / 2
    ha = anchors[:, 2] - anchors[:, 0]
    wa = anchors[:, 3] - anchors[:, 1]

    w = np.exp(boxes[:, 3]) * wa
    h = np.exp(boxes[:, 2]) * ha

    y_centers = boxes[:, 0] * ha + y_centers_a
    x_centers = boxes[:, 1] * wa + x_centers_a

    ymin = y_centers - h / 2.0
    xmin = x_centers - w / 2.0
    ymax = y_centers + h / 2.0
    xmax = x_centers + w / 2.0

    return np.vstack((xmin, ymin, xmax, ymax)).T


# Ref: https://python-ai-learn.com/2021/02/14/nmsfast/
def nms_fast(bboxes, scores, iou_threshold=0.5):
    areas = (bboxes[:, 2] - bboxes[:, 0] + 1) * \
        (bboxes[:, 3] - bboxes[:, 1] + 1)

    sort_index = np.argsort(scores)

    i = -1
    while len(sort_index) >= 1 - i:

        max_scr_ind = sort_index[i]
        ind_list = sort_index[:i]

        iou = iou_np(
            bboxes[max_scr_ind], bboxes[ind_list],
            areas[max_scr_ind], areas[ind_list]
        )

        del_index = np.where(iou >= iou_threshold)
        sort_index = np.delete(sort_index, del_index)
        i -= 1

    bboxes = bboxes[sort_index]
    scores = scores[sort_index]

    return bboxes, scores


# Ref: https://python-ai-learn.com/2021/02/14/nmsfast/
def iou_np(box, boxes, area, areas):
    x_min = np.maximum(box[0], boxes[:, 0])
    y_min = np.maximum(box[1], boxes[:, 1])
    x_max = np.minimum(box[2], boxes[:, 2])
    y_max = np.minimum(box[3], boxes[:, 3])

    w = np.maximum(0, x_max - x_min + 1)
    h = np.maximum(0, y_max - y_min + 1)
    intersect = w * h

    iou_np = intersect / (area + areas - intersect)
    return iou_np


register("spec_car", SpecCarDetector, "hybridnets_384x512.onnx")
