# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
This script shifts colors from base to target in images. This is useful for changing themes, such as from a green to a yellow theme.
It reads images from a specified input folder, processes them to change the green color to yellow, and saves the modified images to a specified output folder.
It uses OpenCV for image processing and NumPy for numerical operations.
"""

import os

import cv2
import numpy as np

# Base and target colors
green_rgb = np.array([36, 127, 76], dtype=np.uint8)
yellow_rgb = np.array([251, 181, 25], dtype=np.uint8)

# Convert base and target colors to HSV
green_hsv = cv2.cvtColor(green_rgb[np.newaxis, np.newaxis, :], cv2.COLOR_RGB2HSV)[0, 0]
yellow_hsv = cv2.cvtColor(yellow_rgb[np.newaxis, np.newaxis, :], cv2.COLOR_RGB2HSV)[0, 0]

# Compute hue shift
hue_shift = (int(yellow_hsv[0]) - int(green_hsv[0])) % 180

print(f"Hue shift: {hue_shift}")

# How strongly to blend saturation and brightness toward yellow target
alpha = 0.5  # 0.0 = keep original, 1.0 = fully yellow values


def shift_green_to_yellow(image_path, output_path):
    # Read the image with alpha channel
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if image is None:
        print(f"Failed to read {image_path}")
        return

    if image.shape[2] == 4:
        # Separate alpha channel
        bgr = image[:, :, :3]
        alpha_channel = image[:, :, 3]
    else:
        bgr = image
        alpha_channel = None

    # Convert BGR to HSV
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

    # Define green hue range
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([85, 255, 255])

    # Create mask for green areas
    mask = cv2.inRange(hsv, lower_green, upper_green)

    hsv_shifted = hsv.copy()

    # Only modify pixels in the mask
    # Shift hue
    hsv_shifted[:, :, 0] = np.where(mask > 0, (hsv[:, :, 0] + hue_shift) % 180, hsv[:, :, 0])

    # Blend saturation toward yellow's saturation
    hsv_shifted[:, :, 1] = np.where(mask > 0, hsv[:, :, 1] * (1 - alpha) + yellow_hsv[1] * alpha, hsv[:, :, 1])

    # Blend brightness toward yellow's brightness
    hsv_shifted[:, :, 2] = np.where(mask > 0, hsv[:, :, 2] * (1 - alpha) + yellow_hsv[2] * alpha, hsv[:, :, 2])

    # Convert back to BGR
    bgr_shifted = cv2.cvtColor(hsv_shifted, cv2.COLOR_HSV2BGR)

    # Reattach alpha if present
    if alpha_channel is not None:
        result = cv2.merge((bgr_shifted, alpha_channel))
    else:
        result = bgr_shifted

    cv2.imwrite(output_path, result)
    print(f"Saved {output_path}")


# Example usage
input_folder = "./old-light"
output_folder = "./light-theme"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(".png"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        shift_green_to_yellow(input_path, output_path)
