import vqpy
from vqpy.function.logger import vqpy_func_logger
from yolox_detector import YOLOXDetector
from vqpy.detector.logger import register

import torch
import numpy as np
import argparse

# pose detection
from PoseEstimateLoader import SPPE_FastPose
from ActionsEstLoader import TSSTG

# default values
# model checkpoints are hard-coded in Actionsrecognition/ and PoseEstimation/
pose_model = SPPE_FastPose('resnet50', 224, 160, device='cuda')
action_model = TSSTG()


def make_parser():
    parser = argparse.ArgumentParser('VQPy Demo!')
    parser.add_argument('--path', help='path to video')
    parser.add_argument(
        "--save_folder",
        default=None,
        help="the folder to save the final result",
    )
    parser.add_argument(
        "-d",
        "--pretrained_model_dir",
        help="Directory to pretrained models")
    return parser


class Person(vqpy.VObjBase):
    required_fields = ['class_id', 'tlbr']

    @vqpy.property()
    @vqpy.stateful(30)
    def keypoints(self):
        # per-frame property, but tracker can return objects not in the current frame
        image = self._ctx.frame
        if self.getv('tlbr') is None:
            return None
        return pose_model.predict(image, torch.tensor([self.getv('tlbr')]))

    @vqpy.property()
    def pose(self) -> str:
        keypoints_list = []
        for i in range(-self._track_length, 0):
            keypoint = self.getv('keypoints', i)
            if keypoint is not None:
                keypoints_list.append(keypoint)
            if len(keypoints_list) >= 30:
                break
        if len(keypoints_list) < 30:
            return 'unknown'
        pts = np.array(keypoints_list, dtype=np.float32)
        out = action_model.predict(pts, self._ctx.frame.shape[:2])
        action_name = action_model.class_names[out[0].argmax()]
        return action_name


class ListPersonPose(vqpy.QueryBase):
    """The class obtaining all fallen person"""
    @staticmethod
    def setting() -> vqpy.VObjConstraint:
        filter_cons = {'__class__': lambda x: x == Person,
                       'pose': lambda x: x == "Fall Down"}
        select_cons = {'track_id': None,
                       'pose': None}
        return vqpy.VObjConstraint(filter_cons=filter_cons,
                                   select_cons=select_cons,
                                   filename='fall')


if __name__ == '__main__':
    args = make_parser().parse_args()
    register("yolox", YOLOXDetector, "yolox_x.pth")
    vqpy.launch(cls_name=vqpy.COCO_CLASSES,
                cls_type={"person": Person},
                tasks=[ListPersonPose()],
                video_path=args.path,
                save_folder=args.save_folder,
                detector_name="yolox",
                detector_model_dir=args.pretrained_model_dir)
