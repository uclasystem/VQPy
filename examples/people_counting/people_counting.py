import argparse
import vqpy
from yolox_detector import YOLOXDetector
from vqpy.detector.logger import register


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
    pass


class CountPersonOnCrosswalk(vqpy.QueryBase):

    @staticmethod
    def set_output_configs() -> vqpy.OutputConfig:
        return vqpy.OutputConfig(
            # output_frame_vobj_num=True,
            output_total_vobj_num=True
            )

    @staticmethod
    def setting() -> vqpy.VObjConstraint:

        CROSSWALK_REGION = [
            (0, 295),
            (488, 1),
            (684, 1),
            (315, 479),
            (0, 479)]

        filter_cons = {"__class__": lambda x: x == Person,
                       "bottom_center": vqpy.utils.within_regions(
                            CROSSWALK_REGION
                            )}
        select_cons = {"track_id": None,
                       "direction": None,
                       }
        return vqpy.VObjConstraint(filter_cons=filter_cons,
                                   select_cons=select_cons,
                                   filename='on_crosswalk')


class CountPersonHeadTopright(CountPersonOnCrosswalk):

    @staticmethod
    def set_output_configs() -> vqpy.OutputConfig:
        return vqpy.OutputConfig(
            # output_frame_vobj_num=True,
            output_total_vobj_num=True
            )

    @staticmethod
    def setting() -> vqpy.VObjConstraint:
        filter_cons = {"direction": lambda x: x == "topright"}
        select_cons = {"track_id": None,
                       "direction": None,
                       }
        return vqpy.VObjConstraint(filter_cons=filter_cons,
                                   select_cons=select_cons,
                                   filename='head_topright')


class CountPersonHeadBottomleft(CountPersonOnCrosswalk):

    @staticmethod
    def set_output_configs() -> vqpy.OutputConfig:
        return vqpy.OutputConfig(
            # output_frame_vobj_num=True,
            output_total_vobj_num=True
            )

    @staticmethod
    def setting() -> vqpy.VObjConstraint:
        filter_cons = {"direction": lambda x: "bottomleft" in x}
        select_cons = {"track_id": None,
                       "direction": None,
                       }
        return vqpy.VObjConstraint(filter_cons=filter_cons,
                                   select_cons=select_cons,
                                   filename='head_bottomleft')


if __name__ == '__main__':
    args = make_parser().parse_args()
    register("yolox", YOLOXDetector, "yolox_x.pth")
    vqpy.launch(cls_name=vqpy.COCO_CLASSES,
                cls_type={"person": Person},
                # tasks=[CountPersonOnCrosswalk()],
                tasks=[CountPersonHeadTopright(), CountPersonHeadBottomleft()],
                video_path=args.path,
                save_folder=args.save_folder,
                detector_name="yolox",
                detector_model_dir=args.pretrained_model_dir)
