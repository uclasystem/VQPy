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

        def get_bottom_central_point(tlbr):
            x = (tlbr[0] + tlbr[2]) / 2
            y = tlbr[3]
            return (x, y)

        def in_region_of_interest(tlbr):
            from shapely.geometry import Point, Polygon

            botton_central_point = get_bottom_central_point(tlbr)
            point = Point(botton_central_point)
            poly = Polygon(REGION)
            if point.within(poly):
                return True
            return False

        filter_cons = {
            "__class__": lambda x: x == Person,
            "tlbr": vqpy.lasting(
                trigger=in_region_of_interest, time=10, name="in_roi"
            ),
        }
        select_cons = {
            "coordinate_center": None,
            "track_id": None,
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
