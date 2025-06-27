from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import albumentations as A

def apply_visual_augmentation(image: Image.Image) -> Image.Image:
    # Convert PIL to NumPy array
    img_np = np.array(image)

    # Define augmentation pipeline
    transform = A.Compose([
        A.GaussianBlur(blur_limit=(3, 5), p=0.5),
        A.GaussNoise(
        std_range=(0.1, 0.2),          
        mean_range=(0.0, 0.0),         
        per_channel=True,              
        noise_scale_factor=1.0,        
        p=0.5                          
        ),
        A.RandomBrightnessContrast(p=0.5),
        A.HueSaturationValue(p=0.3),
        A.Affine(rotate=(-5, 5), shear=(-5, 5), p=0.5)
    ])

    # Apply augmentation
    augmented = transform(image=img_np)["image"]

    # Convert back to PIL
    return Image.fromarray(augmented)

# Test: Show original and augmented images
if __name__ == "__main__":
    import os
    import random
    from glob import glob

    folder_path = "output_fake_ids"
    image_paths = glob(os.path.join(folder_path, "*.jpg"))

    if len(image_paths) == 0:
        print(f"❌ ไม่พบไฟล์ใน {folder_path}")
    else:
        sample_paths = random.sample(image_paths, min(5, len(image_paths)))
        
        for idx, img_path in enumerate(sample_paths):
            original = Image.open(img_path).convert("RGB")
            augmented = apply_visual_augmentation(original)

            # Show both images side by side
            fig, axes = plt.subplots(1, 2, figsize=(10, 5))
            axes[0].imshow(original)
            axes[0].set_title(f"Original ({os.path.basename(img_path)})")
            axes[0].axis("off")

            axes[1].imshow(augmented)
            axes[1].set_title("Augmented")
            axes[1].axis("off")

            plt.tight_layout()
            plt.show()
