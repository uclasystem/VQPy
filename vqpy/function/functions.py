"""VQPy basic libfunctions"""

from .logger import vqpy_func_logger


@vqpy_func_logger(['tlbr'], ['bbox_velocity'], ['tlbr'], required_length=2)
def bbox_velocity(obj, tlbr):
    """compute the bounding box velocity using the center
    estimate the scaling by the height of box
    """
    from math import sqrt
    tlbr_c, tlbr_p = tlbr, obj.getv('tlbr', -2)
    center_c = (tlbr_c[:2] + tlbr_c[2:]) / 2
    center_p = (tlbr_p[:2] + tlbr_p[2:]) / 2
    tlbr_avg = (tlbr_c + tlbr_p) / 2
    scale = (tlbr_avg[3] - tlbr_avg[1]) / 1.5
    dcenter = (center_c - center_p) / scale * obj._ctx.fps
    v = sqrt(sum(dcenter * dcenter))
    return [v]


@vqpy_func_logger(['frame', 'tlbr'], ['image'], [], required_length=1)
def image_boundarycrop(obj, frame, tlbr):
    """crop the image of object from bounding box"""
    from vqpy.utils.images import crop_image
    return [crop_image(frame, tlbr)]


@vqpy_func_logger(['image'], ['license_plate'], [], required_length=1)
def license_plate_lprnet(obj, image):
    """recognize license plate using LPRNet"""
    from vqpy.models.lprnet import GetLP
    return [GetLP(image)]


@vqpy_func_logger(['image'], ['license_plate'], [], required_length=1)
def license_plate_openalpr(obj, image):
    """recognize license plate using OpenAlpr"""
    from vqpy.models.openalpr import GetLP
    return [GetLP(image)]


@vqpy_func_logger(['tlbr'], ['coordinate'], [], required_length=1)
def coordinate_center(obj, tlbr):
    """compute the center of the bounding box"""
    return [(tlbr[:2] + tlbr[2:]) / 2]


@vqpy_func_logger(['tlbr'], ['bottom_center'], [], required_length=1)
def bottom_center_coordinate(obj, tlbr):
    """compute the coordinate of bottom center of the bounding box"""
    x = (tlbr[0] + tlbr[2]) / 2
    y = tlbr[3]
    return [(x, y)]


@vqpy_func_logger(['tlbr'], ['direction'], ['tlbr'], required_length=5)
def direction(obj, tlbr):
    """
    The general direction computed with the past 5 historical frames.
    There are 9 posible results:
    "top", "topright", "right", "bottomright",
    "bottom", "bottomleft", "left", "topleft",
    and None, which means the vobj stays still in the past 5 frames.
    """
    def denoise(target, reference):
        THRESHOLD = 10
        if target != 0 and reference / target >= THRESHOLD:
            target = 0
        return target

    def get_name(value, pos_name, neg_name):
        if value > 0:
            result = pos_name
        elif value < 0:
            result = neg_name
        else:
            result = ""
        return result

    def get_center(tlbr):
        return (tlbr[:2] + tlbr[2:]) / 2

    def most_frequent(List):
        from collections import Counter
        occurence_count = Counter(List)
        return occurence_count.most_common(1)[0][0]

    hist_len = 5
    tlbr_past = [obj.getv("tlbr", (-1)*i) for i in range(1, 1 + hist_len)]
    for value in tlbr_past:
        if value is None:
            return [None]

    centers = list(map(get_center, tlbr_past))
    diffs = [centers[i+1] - centers[i] for i in range(hist_len - 1)]

    diff_xs = [denoise(diff[0], diff[1]) for diff in diffs]
    diff_ys = [denoise(diff[1], diff[0]) for diff in diffs]

    horizontal = most_frequent([get_name(diff_x, "right", "left")
                                for diff_x in diff_xs])
    vertical = most_frequent([get_name(diff_y, "bottom", "top")
                              for diff_y in diff_ys])
    direction = vertical + horizontal
    if direction == "":
        direction = None

    return [direction]
