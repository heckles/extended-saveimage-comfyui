# Extended Save Image for ComfyUI

This custom node is largely identical to the usual Save Image but allows saving images also in JPEG and WEBP formats, the latter with both lossless and lossy compression. Metadata is embedded in the images as usual, and the resulting images can be used to load a workflow.

function added:   %date for date, %time for time

## Installation

To install, clone this repository into `ComfyUI/custom_nodes` folder with `git clone https://github.com/heckles/extended-saveimage-comfyui` and restart ComfyUI.


## 有些customnodes会起冲突，比如
DynamicPrompts Custom Nodes from adieyal (如果生成png可以保留workflow信息，jpg就不行)