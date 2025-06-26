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
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.5),
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

    input_path = "thai_id_000.jpg"
    if os.path.exists(input_path):
        original = Image.open(input_path).convert("RGB")
        augmented = apply_visual_augmentation(original)

        # Show both images side by side
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(original)
        axes[0].set_title("Original")
        axes[0].axis("off")

        axes[1].imshow(augmented)
        axes[1].set_title("Augmented")
        axes[1].axis("off")

        plt.tight_layout()
        plt.show()
    else:
        print(f"❌ ไม่พบไฟล์ {input_path}")
