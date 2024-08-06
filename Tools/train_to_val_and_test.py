import os
import shutil
import random

def split_dataset(dataset_path, val_ratio=0.1, test_ratio=0.1):
    # Create validation and test directories if they don't exist
    val_dir = os.path.join(dataset_path, 'val')
    test_dir = os.path.join(dataset_path, 'test')
    os.makedirs(val_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    
    # Get the list of classes (subdirectories) in the dataset path
    classes = [d for d in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, d)) and d not in ['val', 'test']]
    
    for cls in classes:
        cls_path = os.path.join(dataset_path, cls)
        images = [f for f in os.listdir(cls_path) if os.path.isfile(os.path.join(cls_path, f))]
        
        # Shuffle the images to ensure randomness
        random.shuffle(images)
        
        # Calculate the number of validation and test images
        num_val = int(len(images) * val_ratio)
        num_test = int(len(images) * test_ratio)
        
        # Split the images
        val_images = images[:num_val]
        test_images = images[num_val:num_val + num_test]
        
        # Create class directories in val and test folders if they don't exist
        val_cls_dir = os.path.join(val_dir, cls)
        test_cls_dir = os.path.join(test_dir, cls)
        os.makedirs(val_cls_dir, exist_ok=True)
        os.makedirs(test_cls_dir, exist_ok=True)
        
        # Move images to the respective directories
        for img in val_images:
            shutil.move(os.path.join(cls_path, img), os.path.join(val_cls_dir, img))
        
        for img in test_images:
            shutil.move(os.path.join(cls_path, img), os.path.join(test_cls_dir, img))

    print(f"Dataset split completed. Validation and test sets created in '{val_dir}' and '{test_dir}'.")

# Example usage
dataset_path = r'C:\Capstone\data\classify\train'
split_dataset(dataset_path)
