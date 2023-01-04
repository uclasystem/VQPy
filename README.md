# VQPy : An object-oriented Video Query Language

[![License](https://img.shields.io/badge/License-Apache_2.0-brightgreen.svg)](https://github.com/uclasystem/VQPy/blob/main/LICENSE)

VQPy is an object-oriented language for modern video analytics. With VQPy, users can express their video queries in a composable and reusable manner with Python. 

VQPy is still under active development. VQPy compiler, which generates a query plan with optimized performance for users' video analytics applications, is working in progress. With VQPy compiler, users can simply focus on the declaration of video queries for their own applications, and multiple optimizations defined in the compiler will be transparently applied to the user’s video analytics pipeline.

## Getting Started

### Basic usage

In order to declare a video query with VQPy, users need to extend two classes defined in VQPy, namely `Query` and `VObj`. `VObj` defines the objects of interest (e.g., cars, humans, animals, etc.) in one or more video streams, and `Query` defines the video query.  

#### Define a `VObj`

Users can define their own objects of interest, as well as the property in the objects they hope to query on, with a `VObj` class. The definition should start with a `@vqpy.property` decorator.

For example, if we are interested in the vehicle object in the video, and want to query the license plate. We can define a `Vobj` class as below. 

```python
class Vehicle(vqpy.VObjBase):

    @vqpy.property()
    def license_plate(self):
        # infer license plate with vqpy built-in openalpr model
        return self.infer('license_plate', {'license_plate': 'openalpr'})
```

For more details on how users can define their own property, please refer to the **Examples** section and see how we define objects in our demos.

#### Define a `Query`

Users can express their queries through SQL-like constraints with `VObjConstraint`, which is a return value of the `setting` method in their `Query` class. In `VObjConstraint`, users can specify query constraints on the interested object with `filter_cons`, and `select_cons` gives the projection of the properties the query shall return.

Moreover, the user can provide some functions when The projected properties will pass a postprocess function provided by the user, which is the identity function by default. 

The code below demonstrates a query that selects all the `Vehicle` objects whose velocity is greater than 0.1, and chooses the two properties of `track_id`  and `license_plate` for return.

```python
class ListMovingVehicle(vqpy.QueryBase):

    @staticmethod
    def setting() -> vqpy.VObjConstraint:
        filter_cons = {'__class__': lambda x: x == Vehicle,
                       'velocity': lambda x: x >= 0.1}
        select_cons = {'track_id': None,
                       'license_plate': None}
        return vqpy.VObjConstraint(filter_cons=filter_cons,
                                   select_cons=select_cons)
```

#### Launch the task

Last, we can call `vqpy.launch` to start query video frames.

```python
vqpy.launch(cls_name=vqpy.COCO_CLASSES, # detection class
            cls_type={"car": Vehicle, "truck": Vehicle}, # mappings from detection class to VObj
            tasks=[ListMovingVehicle()], # a list of Queries to apply
            video_path=args.path, # the path of the queried video
            save_folder=args.save_folder, # result of query will be saved as a json file in this folder
            detector_name="yolox", # optional, specify the name of user's own model
            detector_model_dir=args.pretrained_model_dir # optional, specify the directory of user's pretrained model
            )
```

Under the hood, VQPy will automatically select an object detection model that outputs the specified `cls_name`. Multiple video optimizations will be conducted transparently to improve the end-to-end video query performance. 

### Customization

For more details on customization, please refer to the document [here](https://github.com/uclasystem/VQPy/blob/main/docs/frontend.md#customization).

## Examples

We have included several examples for demonstrating VQPy.

- [Fall Detection](examples/fall_detection): detect people in the video and recognize fallen person.
- [List red moving vehicle](examples/list_red_moving_vehicle): show license plate of red moving vehicle.
- [People Loitering](examples/loitering): count the number of person loitering around.
- [People Counting](examples/people_counting): count the number of person heading both directions. 
- [Unattended Baggage Detection](examples/unattended_baggage): detect unattended baggages.

In the following, we will discuss about the objects of interests in each of the above examples, which may help understand how to code with VQPy.

TODO:

### Fall Detection

### List Red Moving Vehicle

### People Loitering

### People Counting

### Unattended Baggage Detection
