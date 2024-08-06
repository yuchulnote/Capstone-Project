import os
import random
import shutil

def create_val_set(train_dir, val_dir, split_ratio=0.1):
    # Ensure the val directory exists
    if not os.path.exists(val_dir):
        os.makedirs(val_dir)
    
    # Get the list of subdirectories (classes)
    classes = [d for d in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, d))]
    
    for cls in classes:
        # Paths to the class directories in train and val
        train_class_dir = os.path.join(train_dir, cls)
        val_class_dir = os.path.join(val_dir, cls)
        
        # Ensure the val class directory exists
        if not os.path.exists(val_class_dir):
            os.makedirs(val_class_dir)
        
        # Get all files in the current class directory
        files = os.listdir(train_class_dir)
        # Determine the number of files to move
        num_val_files = int(len(files) * split_ratio)
        # Randomly select files to move
        val_files = random.sample(files, num_val_files)
        
        # Move the files
        for file in val_files:
            src_path = os.path.join(train_class_dir, file)
            dst_path = os.path.join(val_class_dir, file)
            shutil.move(src_path, dst_path)

# Example usage
train_dir = r'C:\Capstone\data\classify\train'
val_dir = r'C:\Capstone\data\classify\val'
create_val_set(train_dir, val_dir)
