import cv2
import numpy as np
from pathlib import Path


class ImagePreprocessingService:
    """
    Handles document image preprocessing before fraud detection.

    Processing Steps:
    1. Load image
    2. Resize normalization
    3. Convert to grayscale
    4. Noise removal
    5. Contrast enhancement
    6. Adaptive thresholding
    7. Deskew correction
    8. Save processed image
    """

    def load_image(self, image_path: str):
        """
        Load image from disk using OpenCV.
        """
        image = cv2.imread(image_path)

        if image is None:
            raise ValueError(f"Unable to load image from path: {image_path}")

        return image

    def resize_image(self, image, width: int = 1200):
        """
        Resize image while maintaining aspect ratio.
        """
        h, w = image.shape[:2]

        if w == 0:
            return image

        ratio = width / w
        new_height = int(h * ratio)

        resized = cv2.resize(image, (width, new_height))

        return resized

    def convert_to_grayscale(self, image):
        """
        Convert image to grayscale.
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def remove_noise(self, image):
        """
        Remove noise using Gaussian blur.
        """
        return cv2.GaussianBlur(image, (5, 5), 0)

    def enhance_contrast(self, image):
        """
        Improve contrast using histogram equalization.
        """
        return cv2.equalizeHist(image)

    def adaptive_threshold(self, image):
        """
        Apply adaptive thresholding for better text extraction.
        """
        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )

    def deskew(self, image):
        """
        Correct image rotation (deskew).
        """
        coords = np.column_stack(np.where(image > 0))

        if coords.size == 0:
            return image

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

        rotated = cv2.warpAffine(
            image,
            rotation_matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )

        return rotated

    def preprocess(self, image_path: str, output_path: str):
        """
        Execute full preprocessing pipeline and save processed image.
        """

        # Load image
        image = self.load_image(image_path)

        # Resize normalization
        image = self.resize_image(image)

        # Convert to grayscale
        gray = self.convert_to_grayscale(image)

        # Remove noise
        denoised = self.remove_noise(gray)

        # Enhance contrast
        contrast = self.enhance_contrast(denoised)

        # Adaptive threshold
        threshold = self.adaptive_threshold(contrast)

        # Deskew image
        deskewed = self.deskew(threshold)

        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save processed image
        cv2.imwrite(output_path, deskewed)

        return output_path