# List Red Moving Vehicles example
This example demonstrates how to use VQPy to generate a query that returns the plate numbers of all red moving vehicles.

## Environment preparation
You can follow the instructions [here](../../README.md#installation) to prepare your environment for VQPy.

Pretrained onnx model for the specific car detector can be found [here](https://github.com/PINTO0309/PINTO_model_zoo/tree/main/276_HybridNets), the `hybridnets_384x512` model and anchors are used.

Besides, please use below command to install other dependencies for this example.
```
pip install webcolors ColorDetect opencv-python
```

## Download Dataset
TO BE ADDED.

## Run Example
You can simply use `python main.py` to run the example. Below are the arguments you need to specify.
* `--path`: your own video dataset path.
* `--save_folder`: the folder that you preferred to save the query result.
* `-d`: your directory for all pretrained models.