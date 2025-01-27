from PIL import Image
import os
from pathlib import Path
import sys

def compress_image(input_path, output_path, max_size_kb=150):
    """Compress image to target size while maintaining acceptable quality"""
    # Open image
    img = Image.open(input_path)
    
    # Convert to RGB if image is in RGBA mode
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Initial quality
    quality = 95
    min_quality = 5
    
    # Binary search approach for finding optimal quality
    while quality > min_quality:
        # Save image to temporary buffer to check size
        temp_output = Path(output_path).with_suffix('.temp.jpg')
        img.save(temp_output, 'JPEG', quality=quality)
        
        # Check file size
        size_kb = os.path.getsize(temp_output) / 1024
        
        # Remove temporary file
        os.remove(temp_output)
        
        if size_kb <= max_size_kb:
            break
        
        # Reduce quality for next iteration
        quality -= 5
    
    # Save final version
    img.save(output_path, 'JPEG', quality=quality)
    return quality, size_kb

def main():
    # Get input and output directories from user
    input_dir = input("Enter the input directory path: ").strip()
    output_dir = input("Enter the output directory path: ").strip()
    
    # Validate input directory
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Supported image formats
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    
    # Process each file
    processed_count = 0
    skipped_count = 0
    
    print("\nStarting batch compression...")
    print("-" * 50)
    
    for filename in os.listdir(input_dir):
        input_path = os.path.join(input_dir, filename)
        
        # Skip if not a file or not a supported image format
        if not os.path.isfile(input_path) or not any(filename.lower().endswith(fmt) for fmt in supported_formats):
            skipped_count += 1
            continue
        
        # Create output path with jpg extension
        output_filename = os.path.splitext(filename)[0] + '.jpg'
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            # Compress image
            quality, final_size = compress_image(input_path, output_path)
            
            print(f"Processed: {filename}")
            print(f"  - Output: {output_filename}")
            print(f"  - Quality: {quality}%")
            print(f"  - Final size: {final_size:.2f}KB")
            print("-" * 50)
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            skipped_count += 1
    
    print(f"\nCompression complete!")
    print(f"Successfully processed: {processed_count} images")
    print(f"Skipped/Failed: {skipped_count} files")

if __name__ == "__main__":
    main()