# Detect people loitering example

## Setup

You can follow the instructions [here](../../vqpy/README.md) to prepare your environment for VQPy. No other dependency is used.

Video used in this query can be found [here](https://youtu.be/EuLMrUFNRxQ).

## Query logic

This example demonstrates VQPy's built-in filter condition wrapper `vqpy.utils.continuing`.

Loitering is the activity of remaining in an area for no obvious reason. In this example, we are interested in people staying in the garage (red polygon region below) for more than 10 seconds.

<img src="./README.assets/region.png" alt="region of interest" style="zoom: 30%;" />

To find all such people, first define a `Person` class and specify that COCO class "person" should map to VObj type `Person`:

```python
class Person(vqpy.VObjBase):
    pass
...
vqpy.launch(
    cls_name=vqpy.COCO_CLASSES,
    cls_type={"person": Person},
    ...
)
```

Compose the the query with filter condition:

```python
filter_cons = {
    "__class__": lambda x: x == Person,
    "bottom_center": vqpy.utils.continuing(
        condition=vqpy.utils.within_regions(REGIONS),
        duration=10, name="in_roi"
    ),
}
```

where:

- `__class__` specifies type of VObj should be `Person`;
- `bottom_center` is a built-in property of VObj, it returns the middle point of the bottom of VObj's bounding box (i.e. where the person is standing);
- `vqpy.utils.within_regions(REGIONS)` is used to check if the coordinate is in any part of the region specified in `REGIONS`, set to the area of interest as shown in the picture above;
- `vqpy.utils.continuing` wraps the condition `within_regions(REGIONS)`, while also specifying the condition should be satisfied for at least 10 seconds, and name `in_roi` should be used to store time periods of condition being satisfied.

Later in `select_cons`, we can use `in_roi_periods` to retrieve time periods of `Person` satisfying the condition:

```python
select_cons = {
    ...
    "in_roi_periods": None,
}
```

## Run example

To run locally

```python
python VQPy/examples/loitering/main.py
    --path videos/loitering/loitering.mp4
    --save_folder vqpy_outputs/loitering
    -d models
```

- `--path`: path of video;
- `--save_folder`: the folder that you preferred to save the query result;
- `-d`: directory with pre-trained models (only model for YOLOX is used).

Or use [Jupyter Notebook](./demo.ipynb). Notebook tested Google Colab, it's advised to use a unused, clean Python3.8 environment if you prefer to run it locally.

## Expected results

```json
...
{
    "frame_id": 1096,
    "data": [
      {
        "track_id": 606,
        "coordinate": "[1126.6016   301.42188]",
        "in_roi_periods": [[40, 73]]
      }
    ]
}
```

At frame 1096, person with `track_id` 606 and coordinate `[1126,301]` is in the garage, he is in the garage from 40-73 second of the video.
