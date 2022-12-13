import argparse

import vqpy
from vqpy.detector.logger import register
from yolox_detector import YOLOXDetector


def make_parser():
    parser = argparse.ArgumentParser("VQPy Demo!")
    parser.add_argument("--path", help="path to video")
    parser.add_argument(
        "--save_folder",
        default=None,
        help="the folder to save the final result",
    )
    parser.add_argument(
        "-d", "--pretrained_model_dir", help="Directory to pretrained models"
    )
    return parser


class Person(vqpy.VObjBase):
    @vqpy.property()
    def coordinate_center(self):
        tlbr = self.getv("tlbr")
        if tlbr is not None:
            return str((tlbr[:2] + tlbr[2:]) / 2)


class People_loitering_query(vqpy.QueryBase):
    @staticmethod
    def setting() -> vqpy.VObjConstraint:
        REGION = [
            (550, 550), (1162, 400), (1720, 720), (1430, 1072), (600, 1073)
            ]
        REGIONS = [REGION]

        filter_cons = {
            "__class__": lambda x: x == Person,
            "bottom_center": vqpy.utils.lasting(
                trigger=vqpy.utils.within_regions(REGIONS),
                time=10, name="in_roi"
            ),
        }
        select_cons = {
            "coordinate_center": None,
            "track_id": None,
            # name in vqpy.lasting + '_time_periods' stored in VObj
            # can be accessed by getv, be used in select_cons, etc.
            "in_roi_time_periods": None,
        }
        return vqpy.VObjConstraint(
            filter_cons, select_cons, filename="loitering"
        )


if __name__ == "__main__":
    args = make_parser().parse_args()
    register("yolox", YOLOXDetector, "yolox_x.pth")
    vqpy.launch(
        cls_name=vqpy.COCO_CLASSES,
        cls_type={"person": Person},
        tasks=[People_loitering_query()],
        video_path=args.path,
        save_folder=args.save_folder,
        detector_name="yolox",
        detector_model_dir=args.pretrained_model_dir,
    )
