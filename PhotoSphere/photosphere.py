import cv2
import numpy as np
from glob import glob
import os

class AdvancedPhotoSphere:
    def __init__(self):
        self.stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
        
    def create_sphere_with_blending(self, image_folder):
        """Create photo sphere with multi-band blending"""
        
        images = []
        for img_path in glob(os.path.join(image_folder, "*")):
            if img_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = cv2.imread(img_path)
                if img is not None:
                    # Resize if images are too large (for performance)
                    h, w = img.shape[:2]
                    if w > 2000:
                        scale = 2000 / w
                        img = cv2.resize(img, (int(w*scale), int(h*scale)))
                    images.append(img)
        
        if len(images) < 2:
            return None
            
        print(f"Processing {len(images)} images...")
        
        # Stitch with multi-band blending
        status, panorama = self.stitcher.stitch(images)
        
        if status == cv2.Stitcher_OK:
            # Post-processing: remove black borders
            panorama = self.remove_black_borders(panorama)
            return panorama
        else:
            print(f"Stitching failed with error code: {status}")
            return None
    
    def remove_black_borders(self, image):
        """Remove black borders from stitched image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Crop the image
            cropped = image[y:y+h, x:x+w]
            return cropped
        
        return image

# Usage
def main_advanced():
    generator = AdvancedPhotoSphere()
    image_folder = "./PhotoSphere/input_images"  # Change this
    
    result = generator.create_sphere_with_blending(image_folder)
    
    if result is not None:
        cv2.imwrite("./PhotoSphere/advanced_panorama.jpg", result)
        print("Advanced panorama saved!")
        
        # Display
        cv2.imshow("Photo Sphere", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("Failed to create photo sphere")

if __name__ == "__main__":
    main_advanced()