from PIL import Image
import os
from pathlib import Path
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor


def compress_image(input_path, output_path, max_size_kb=53*1024, min_quality=30):
    """Compress and resize the image to target size while maintaining acceptable quality."""
    # Open the image
    img = Image.open(input_path)
    
    # Convert to RGB if image is in RGBA mode (i.e., has transparency)
    if img.mode == 'RGBA':
        img = img.convert('RGB')

    # Resize the image to 25% of its original resolution (more aggressive resize)
    width, height = img.size
    new_size = (int(width * 0.25), int(height * 0.25))  # Resize to 25% of original
    img = img.resize(new_size, Image.Resampling.LANCZOS)  # Correct resampling method
    
    # Initial quality (starting at 75%)
    quality = 75
    min_quality = max(min_quality, 30)  # Ensure quality doesn't go below 30%
    
    # In-memory compression (to avoid writing temporary files)
    while quality >= min_quality:
        buffer = BytesIO()
        img.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        
        size_kb = len(buffer.getvalue()) / 1024  # Size in KB
        
        if size_kb <= max_size_kb:
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())  # Save the compressed image
            break
        
        # Reduce quality for the next iteration
        quality -= 5


def process_image(input_path, output_path, max_size_kb=53*1024, min_quality=30):
    """Helper function to process each image."""
    try:
        compress_image(input_path, output_path, max_size_kb, min_quality)
        return (input_path, output_path, "Success")
    except Exception as e:
        return (input_path, None, f"Error: {str(e)}")


def main():
    input_dir = Path(input("Enter the input directory path: ").strip())
    output_dir = Path(input("Enter the output directory path: ").strip())

    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist!")
        return

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Supported image formats
    supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
    
    # List of image files to process
    input_files = [
        file for file in input_dir.iterdir() 
        if file.is_file() and file.suffix.lower() in supported_formats
    ]
    
    processed_count = 0
    skipped_count = 0

    # Start parallel processing using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        futures = []
        
        # Submit each image for processing in parallel
        for input_path in input_files:
            output_filename = input_path.stem + '.jpg'  # Use jpg as the output format
            output_path = output_dir / output_filename
            futures.append(executor.submit(process_image, input_path, output_path))

        # Wait for all tasks to complete
        for future in futures:
            input_path, output_path, status = future.result()
            
            if output_path:
                print(f"Processed: {input_path.name}")
                print(f"  - Output: {output_path.name}")
                print(f"  - Status: {status}")
                processed_count += 1
            else:
                print(f"Failed to process {input_path.name}: {status}")
                skipped_count += 1

    print("\nCompression complete!")
    print(f"Successfully processed: {processed_count} images")
    print(f"Skipped/Failed: {skipped_count} files")


if __name__ == "__main__":
    main()
