# 目前在保存comfyui生成的图片为jpg格式且带workflow信息的基础上，增加了文件名和路径中实现日期和时间通配符的功能
# 下一步试试保存prompt的文本，以及在comfyui中能够用插件读取prompt的文本、并导出到工作流
# 1
# 有些customnodes会起冲突，比如
# DynamicPrompts Custom Nodes from adieyal (如果生成png可以保留workflow信息，jpg就不行)


from comfy.cli_args import args
import folder_paths
import json
import numpy
import os
from PIL import Image, ExifTags
from PIL.PngImagePlugin import PngInfo

# ========================================Mod=============================================
from datetime import datetime


def get_timestamp(time_format):
    now = datetime.now()
    try:
        timestamp = now.strftime(time_format)
    except:
        timestamp = now.strftime("%Y-%m-%d %H-%M-%S")
    return timestamp


def make_pathname(filename):
    filename = filename.replace("%date", get_timestamp("%Y-%m-%d"))
    filename = filename.replace("%time", get_timestamp("%H-%M-%S"))
    return filename


# 这里的变量得在后面得class输入里赋值，要不会报错


def wildcards_to_string(wildcards):
    if wildcards is None:
        return ""
    return wildcards.replace(",", "_")  # 把多个wildercards用&连接起来
    # return wildcards.replace(" ", "_").replace(",", "&")    .replace可以叠用


# =====================================================================================


class SaveImageExtended:
    def __init__(self):
        pass

    FILE_TYPE_PNG = "PNG"
    FILE_TYPE_JPEG = "JPEG"
    FILE_TYPE_WEBP_LOSSLESS = "WEBP (lossless)"
    FILE_TYPE_WEBP_LOSSY = "WEBP (lossy)"
    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "image"

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "%date %time"}),
                "file_type": (
                    [
                        s.FILE_TYPE_PNG,
                        s.FILE_TYPE_JPEG,
                        s.FILE_TYPE_WEBP_LOSSLESS,
                        s.FILE_TYPE_WEBP_LOSSY,
                    ],
                    {"default": "JPEG"},
                ),
                "wildcards": ("STRING", {"default": ""}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    def save_images(
        self,
        images,
        wildcards,
        filename_prefix="ComfyUI",
        file_type=FILE_TYPE_PNG,
        prompt=None,
        extra_pnginfo=None,
    ):
        output_dir = folder_paths.get_output_directory()
        # ======================================================
        filename_prefix = make_pathname(filename_prefix)
        wildcards = wildcards_to_string(wildcards)
        # ======================================================
        full_output_folder, filename, counter, subfolder, _ = (
            folder_paths.get_save_image_path(
                filename_prefix, output_dir, images[0].shape[1], images[0].shape[0]
            )
        )
        # 元组解包赋值
        extension = {
            self.FILE_TYPE_PNG: "png",
            self.FILE_TYPE_JPEG: "jpg",
            self.FILE_TYPE_WEBP_LOSSLESS: "webp",
            self.FILE_TYPE_WEBP_LOSSY: "webp",
        }.get(file_type, "png")

        results = []
        for image in images:
            array = 255.0 * image.cpu().numpy()
            img = Image.fromarray(numpy.clip(array, 0, 255).astype(numpy.uint8))

            kwargs = dict()
            if extension == "png":
                kwargs["compress_level"] = 4
                if not args.disable_metadata:
                    metadata = PngInfo()
                    if prompt is not None:
                        metadata.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        for x in extra_pnginfo:
                            metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                    kwargs["pnginfo"] = metadata
            else:
                if file_type == self.FILE_TYPE_WEBP_LOSSLESS:
                    kwargs["lossless"] = True
                else:
                    kwargs["quality"] = 90
                if not args.disable_metadata:
                    metadata = {}
                    if prompt is not None:
                        metadata["prompt"] = prompt
                    if extra_pnginfo is not None:
                        metadata.update(extra_pnginfo)
                    exif = img.getexif()
                    exif[ExifTags.Base.UserComment] = json.dumps(metadata)
                    kwargs["exif"] = exif.tobytes()

            file = (
                f"{filename}_{counter:05}_{wildcards}.{extension}"  # ==================
            )
            img.save(os.path.join(full_output_folder, file), **kwargs)
            results.append(
                {
                    "filename": file,
                    "subfolder": subfolder,
                    "type": "output",
                }
            )
            counter += 1

        return {"ui": {"images": results}}


NODE_CLASS_MAPPINGS = {"SaveImageExtended": SaveImageExtended}

NODE_DISPLAY_NAME_MAPPINGS = {"SaveImageExtended": "Save Image (Extended)【Mod】"}

WEB_DIRECTORY = "web"
