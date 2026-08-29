"""
Phase 6 — PPE Model Training Script
Executed on: Google Colab (NVIDIA T4 GPU)
Description: This script trains the YOLOv8 Nano model on the Phase 5 PPE dataset.
"""

from ultralytics import YOLO

def main():
    print("Initializing YOLOv8 Nano model...")
    model = YOLO("yolov8n.pt")

    print("Starting training on GPU...")
    results = model.train(
        data="dataset/data.yaml",   # Path to the Phase 5 data.yaml
        epochs=50,                  # Target epochs for convergence
        imgsz=640,                  # High resolution
        batch=16,                   # GPU-optimized batch size
        device=0,                   # 0 refers to the CUDA GPU
        project="ppe_experiments",
        name="final_yolov8n",
        
        # Phase 5 Augmentation Plan parameters
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        scale=0.5,
        fliplr=0.5
    )
    
    print("Training complete. Evaluating on the test set...")
    
    # Evaluate the model on the unseen test set
    metrics = model.val(
        data="dataset/data.yaml", 
        split="test",
        project="ppe_experiments",
        name="test_evaluation"
    )
    print("Test evaluation complete!")

if __name__ == "__main__":
    main()