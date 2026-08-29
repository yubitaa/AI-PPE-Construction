📦 Found dataset.zip (1271.71 MB)
Unzipping dataset, please wait...
✅ Unzipping complete!
✅ Found data.yaml at: /content/dataset/data.yaml
Ultralytics 8.4.131 🚀 Python-3.13.15 torch-2.11.0+cu128 CUDA:0 (Tesla T4, 14913MiB)
engine/trainer: agnostic_nms=False, amp=True, angle=1.0, augment=False, auto_augment=randaugment, batch=16, bgr=0.0, box=7.5, cache=False, cfg=None, channels_last=False, classes=None, close_mosaic=10, cls=0.5, cls_pw=0.0, cls_remap=True, compile=False, conf=None, copy_paste=0.0, copy_paste_mode=flip, cos_lr=False, cutmix=0.0, data=/content/dataset/data.yaml, degrees=10.0, deterministic=True, device=0, dfl=1.5, dgrad=0.5, dis=6.0, distill_model=None, dlam=1.0, dlog=1.0, dnn=False, dropout=0.0, dynamic=False, embed=None, end2end=None, epochs=50, erasing=0.4, exist_ok=False, fliplr=0.5, flipud=0.0, format=torchscript, fraction=1.0, freeze=None, hsv_h=0.015, hsv_s=0.7, hsv_v=0.4, imgsz=640, iou=0.7, keras=False, kobj=1.0, line_width=None, lr0=0.01, lrf=0.01, mask_ratio=4, max_det=300, mixup=0.0, mode=train, model=yolov8n.pt, momentum=0.937, mosaic=1.0, multi_scale=0.0, name=colab_yolov8n-2, nbs=64, nms=False, opset=None, optimize=False, optimizer=auto, overlap_mask=True, patience=100, perspective=0.0, plots=True, pose=12.0, pretrained=True, profile=False, project=ppe_experiments, quantize=None, rect=False, resume=False, retina_masks=False, rle=1.0, save=True, save_conf=False, save_crop=False, save_dir=/content/runs/detect/ppe_experiments/colab_yolov8n-2, save_frames=False, save_json=False, save_period=-1, save_txt=False, scale=0.5, seed=0, shear=0.0, show=False, show_boxes=True, show_conf=True, show_labels=True, simplify=True, single_cls=False, source=None, split=val, stream_buffer=False, task=detect, time=None, tracker=tracktrack.yaml, translate=0.1, val=True, verbose=True, vid_stride=1, visualize=False, warmup_bias_lr=0.1, warmup_epochs=3.0, warmup_momentum=0.8, weight_decay=0.0005, workers=8, workspace=None
Downloading https://ultralytics.com/assets/Arial.ttf to '/root/.config/Ultralytics/Arial.ttf': 100% ━━━━━━━━━━━━ 755.1KB 24.4MB/s 0.0s
Overriding model.yaml nc=80 with nc=3

                   from  n    params  module                                       arguments                     
  0                  -1  1       464  ultralytics.nn.modules.conv.Conv             [3, 16, 3, 2]                 
  1                  -1  1      4672  ultralytics.nn.modules.conv.Conv             [16, 32, 3, 2]                
  2                  -1  1      7360  ultralytics.nn.modules.block.C2f             [32, 32, 1, True]             
  3                  -1  1     18560  ultralytics.nn.modules.conv.Conv             [32, 64, 3, 2]                
  4                  -1  2     49664  ultralytics.nn.modules.block.C2f             [64, 64, 2, True]             
  5                  -1  1     73984  ultralytics.nn.modules.conv.Conv             [64, 128, 3, 2]               
  6                  -1  2    197632  ultralytics.nn.modules.block.C2f             [128, 128, 2, True]           
  7                  -1  1    295424  ultralytics.nn.modules.conv.Conv             [128, 256, 3, 2]              
  8                  -1  1    460288  ultralytics.nn.modules.block.C2f             [256, 256, 1, True]           
  9                  -1  1    164608  ultralytics.nn.modules.block.SPPF            [256, 256, 5]                 
 10                  -1  1         0  torch.nn.modules.upsampling.Upsample         [None, 2, 'nearest']          
 11             [-1, 6]  1         0  ultralytics.nn.modules.conv.Concat           [1]                           
 12                  -1  1    148224  ultralytics.nn.modules.block.C2f             [384, 128, 1]                 
 13                  -1  1         0  torch.nn.modules.upsampling.Upsample         [None, 2, 'nearest']          
 14             [-1, 4]  1         0  ultralytics.nn.modules.conv.Concat           [1]                           
 15                  -1  1     37248  ultralytics.nn.modules.block.C2f             [192, 64, 1]                  
 16                  -1  1     36992  ultralytics.nn.modules.conv.Conv             [64, 64, 3, 2]                
 17            [-1, 12]  1         0  ultralytics.nn.modules.conv.Concat           [1]                           
 18                  -1  1    123648  ultralytics.nn.modules.block.C2f             [192, 128, 1]                 
 19                  -1  1    147712  ultralytics.nn.modules.conv.Conv             [128, 128, 3, 2]              
 20             [-1, 9]  1         0  ultralytics.nn.modules.conv.Concat           [1]                           
 21                  -1  1    493056  ultralytics.nn.modules.block.C2f             [384, 256, 1]                 
 22        [15, 18, 21]  1    751897  ultralytics.nn.modules.head.Detect           [3, 16, None, [64, 128, 256]] 
Model summary: 130 layers, 3,011,433 parameters, 3,011,417 gradients, 8.2 GFLOPs

Remapped 1/3 cls head rows from pretrained weights by class name
Transferred 322/355 items from pretrained weights
Freezing layer 'model.22.dfl.conv.weight'
AMP: running Automatic Mixed Precision (AMP) checks...
AMP: downloading yolo26n.pt for AMP checks (one-time, not used for training)...
Downloading https://github.com/ultralytics/assets/releases/download/v8.4.0/yolo26n.pt to 'weights/yolo26n.pt': 100% ━━━━━━━━━━━━ 5.3MB 100.6MB/s 0.1s
AMP: checks passed ✅
train: Fast image access ✅ (ping: 0.0±0.0 ms, read: 2753.2±806.7 MB/s, size: 186.9 KB)
train: Scanning /content/dataset/train/labels... 1888 images, 0 backgrounds, 0 corrupt: 100% ━━━━━━━━━━━━ 1888/1888 2.1Kit/s 0.9s
train: New cache created: /content/dataset/train/labels.cache
albumentations: Blur(p=0.01, blur_limit=(3, 7)), MedianBlur(p=0.01, blur_limit=(3, 7)), ToGray(p=0.01, method='weighted_average', num_output_channels=3), CLAHE(p=0.01, clip_limit=(1.0, 4.0), tile_grid_size=(8, 8))
val: Fast image access ✅ (ping: 0.0±0.0 ms, read: 999.6±706.8 MB/s, size: 146.8 KB)
val: Scanning /content/dataset/val/labels... 236 images, 0 backgrounds, 0 corrupt: 100% ━━━━━━━━━━━━ 236/236 1.8Kit/s 0.1s
val: New cache created: /content/dataset/val/labels.cache
optimizer: 'optimizer=auto' found, ignoring 'lr0=0.01' and 'momentum=0.937' and determining best 'optimizer', 'lr0' and 'momentum' automatically... 
optimizer: AdamW(lr=0.001429, momentum=0.9) with parameter groups 57 weight(decay=0.0), 64 weight(decay=0.0005), 63 bias(decay=0.0)
Plotting labels to /content/runs/detect/ppe_experiments/colab_yolov8n-2/labels.jpg... 
Using 1888 train, 236 val images for fraction=1.0 at imgsz=640
Using 2 dataloader workers
Logging results to /content/runs/detect/ppe_experiments/colab_yolov8n-2
Starting training for 50 epochs...

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       1/50      2.08G      1.533      1.715      1.446        197        640: 100% ━━━━━━━━━━━━ 118/118 3.4it/s 34.3s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.3it/s 6.0s
                   all        236       1962      0.702      0.628      0.678      0.292

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       2/50      2.56G      1.428      1.175       1.37        204        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.1s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.5it/s 3.2s
                   all        236       1962      0.705      0.643      0.712      0.306

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       3/50      2.56G      1.445       1.13      1.377        167        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962      0.677      0.704      0.727      0.346

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       4/50      2.56G      1.413      1.042      1.354        280        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 32.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.0s
                   all        236       1962      0.769      0.747      0.773      0.372

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       5/50      2.56G      1.384      0.983       1.34        270        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.6s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.5it/s 3.2s
                   all        236       1962      0.775      0.719      0.793      0.399

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       6/50      2.56G      1.376     0.9428      1.331        228        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.0it/s 2.7s
                   all        236       1962      0.761      0.808      0.834       0.43

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       7/50      2.56G      1.371     0.9163      1.327        296        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.1s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.0it/s 3.9s
                   all        236       1962       0.78       0.79      0.836      0.443

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       8/50      2.56G      1.345     0.8864      1.313        304        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.2it/s 2.5s
                   all        236       1962      0.789      0.782       0.83      0.439

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
       9/50      2.56G      1.343     0.8694      1.313        202        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.8s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.5it/s 3.2s
                   all        236       1962       0.79      0.789      0.841      0.441

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      10/50      2.56G       1.32     0.8535      1.297        281        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.1s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.9it/s 2.7s
                   all        236       1962      0.808       0.79      0.841      0.468

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      11/50      2.56G      1.294     0.8156      1.282        226        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.4s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962       0.82       0.76       0.83      0.453

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      12/50      2.56G      1.297     0.8218      1.288        209        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.5s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.8it/s 4.5s
                   all        236       1962      0.811      0.785      0.851      0.451

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      13/50      2.56G       1.28     0.7952      1.265        280        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 30.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.0it/s 2.7s
                   all        236       1962      0.804      0.793      0.844      0.464

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      14/50      2.56G      1.271     0.7744       1.27        238        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.6s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962      0.805      0.795      0.853      0.441

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      15/50      2.56G      1.258      0.761      1.263        209        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.4it/s 3.3s
                   all        236       1962      0.805       0.81      0.857      0.474

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      16/50      2.56G      1.268     0.7676      1.269        300        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.1s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.1it/s 2.6s
                   all        236       1962      0.832      0.831      0.874      0.469

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      17/50      2.56G       1.25     0.7497      1.262        262        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962      0.762      0.793      0.835      0.449

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      18/50      2.56G      1.242     0.7455      1.257        280        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.7it/s 3.0s
                   all        236       1962      0.817      0.787      0.857      0.474

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      19/50      2.56G      1.243     0.7355      1.248        350        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 32.7s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.7it/s 2.9s
                   all        236       1962      0.808      0.797      0.856      0.469

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      20/50      2.56G      1.211     0.7129      1.236        281        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 32.7s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962      0.838      0.815      0.866      0.486

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      21/50      2.56G      1.216     0.7126      1.237        330        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 32.6s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.5it/s 3.2s
                   all        236       1962      0.823      0.803      0.858      0.483

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      22/50      2.56G      1.224     0.7116       1.24        252        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 33.0s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.0it/s 2.7s
                   all        236       1962      0.818      0.818      0.863      0.482

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      23/50      2.56G      1.206     0.6933      1.231        258        640: 100% ━━━━━━━━━━━━ 118/118 3.5it/s 33.4s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.8it/s 2.9s
                   all        236       1962      0.814      0.825      0.869      0.483

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      24/50      2.56G      1.203     0.6947      1.231        253        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 32.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.7it/s 4.7s
                   all        236       1962      0.812       0.82      0.869      0.487

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      25/50      2.56G       1.21     0.6955       1.23        314        640: 100% ━━━━━━━━━━━━ 118/118 3.5it/s 33.5s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962      0.806       0.84      0.863      0.486

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      26/50      2.56G      1.195     0.6858      1.222        251        640: 100% ━━━━━━━━━━━━ 118/118 3.4it/s 34.3s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.8it/s 2.8s
                   all        236       1962       0.82      0.809      0.863      0.483

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      27/50      2.56G      1.199     0.6791      1.226        287        640: 100% ━━━━━━━━━━━━ 118/118 3.4it/s 34.8s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.9it/s 2.8s
                   all        236       1962      0.813      0.825      0.864      0.488

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      28/50      2.56G      1.175     0.6739      1.217        191        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 32.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.1it/s 3.9s
                   all        236       1962      0.821      0.807      0.857      0.483

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      29/50      2.56G      1.169     0.6553      1.213        293        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.0it/s 2.6s
                   all        236       1962      0.814      0.832       0.87       0.49

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      30/50      2.56G      1.164      0.654      1.203        210        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 33.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.9it/s 2.8s
                   all        236       1962      0.819      0.833      0.869      0.477

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      31/50      2.56G      1.156     0.6533      1.203        268        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.6s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.9it/s 4.3s
                   all        236       1962      0.827      0.819      0.869       0.48

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      32/50      2.56G      1.158     0.6445       1.21        191        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.8s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.7it/s 3.0s
                   all        236       1962      0.813      0.813      0.862       0.49

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      33/50      2.56G      1.154     0.6423        1.2        257        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 32.8s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.8it/s 2.9s
                   all        236       1962      0.824        0.8      0.861       0.48

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      34/50      2.56G      1.146     0.6344      1.193        254        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 32.0s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.9it/s 4.2s
                   all        236       1962       0.81       0.83      0.869        0.5

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      35/50      2.56G      1.139     0.6292      1.191        292        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.5s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.0s
                   all        236       1962      0.825      0.835      0.876      0.498

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      36/50      2.56G      1.127     0.6209      1.183        310        640: 100% ━━━━━━━━━━━━ 118/118 3.5it/s 33.3s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.2it/s 2.5s
                   all        236       1962      0.838      0.825      0.874      0.494

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      37/50      2.56G      1.121     0.6178      1.184        261        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.0it/s 4.1s
                   all        236       1962      0.824      0.825      0.872      0.493

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      38/50      2.56G      1.119     0.6108       1.18        271        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 31.3s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.8it/s 2.9s
                   all        236       1962      0.816      0.806      0.862      0.485

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      39/50      2.56G      1.116     0.6071      1.174        294        640: 100% ━━━━━━━━━━━━ 118/118 3.6it/s 32.5s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.6it/s 3.1s
                   all        236       1962      0.827      0.825       0.87      0.493

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      40/50      2.56G        1.1     0.6038      1.175        249        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.8s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.2it/s 3.6s
                   all        236       1962      0.831      0.826       0.87      0.501
Closing dataloader mosaic
albumentations: Blur(p=0.01, blur_limit=(3, 7)), MedianBlur(p=0.01, blur_limit=(3, 7)), ToGray(p=0.01, method='weighted_average', num_output_channels=3), CLAHE(p=0.01, clip_limit=(1.0, 4.0), tile_grid_size=(8, 8))

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      41/50      2.56G      1.088     0.5574      1.172         89        640: 100% ━━━━━━━━━━━━ 118/118 3.5it/s 33.2s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.0it/s 2.6s
                   all        236       1962      0.832      0.831      0.874      0.497

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      42/50      2.56G      1.068     0.5381      1.168         81        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 31.7s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.9it/s 2.8s
                   all        236       1962      0.825      0.824      0.871      0.496

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      43/50      2.56G      1.062     0.5353      1.164        135        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.3s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.3it/s 3.5s
                   all        236       1962      0.837      0.807      0.869      0.494

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      44/50      2.56G      1.045     0.5247      1.151        107        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 30.9s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.1it/s 2.6s
                   all        236       1962      0.836      0.821      0.869      0.498

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      45/50      2.56G      1.038     0.5196      1.147        122        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.6s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.8it/s 4.5s
                   all        236       1962      0.841      0.803      0.866      0.497

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      46/50      2.56G      1.034     0.5119      1.142        102        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.1s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.7it/s 3.0s
                   all        236       1962       0.82      0.825      0.869      0.496

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      47/50      2.56G      1.021     0.5095       1.14         98        640: 100% ━━━━━━━━━━━━ 118/118 3.8it/s 30.7s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.9it/s 4.1s
                   all        236       1962      0.829      0.827      0.873      0.499

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      48/50      2.56G      1.018     0.5051      1.138        111        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.6s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.2it/s 2.5s
                   all        236       1962      0.821      0.829      0.873      0.498

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      49/50      2.56G      1.008     0.4988      1.133        105        640: 100% ━━━━━━━━━━━━ 118/118 3.7it/s 32.0s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 2.8it/s 2.8s
                   all        236       1962      0.827      0.837      0.878        0.5

      Epoch    GPU_mem   box_loss   cls_loss   dfl_loss  Instances       Size
      50/50      2.56G      1.004     0.4952       1.13        120        640: 100% ━━━━━━━━━━━━ 118/118 3.9it/s 30.3s
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 3.1it/s 2.6s
                   all        236       1962      0.826      0.827      0.873      0.499

50 epochs completed in 0.498 hours.
Optimizer stripped from /content/runs/detect/ppe_experiments/colab_yolov8n-2/weights/last.pt, 6.2MB
Optimizer stripped from /content/runs/detect/ppe_experiments/colab_yolov8n-2/weights/best.pt, 6.2MB

Validating /content/runs/detect/ppe_experiments/colab_yolov8n-2/weights/best.pt...
Ultralytics 8.4.131 🚀 Python-3.13.15 torch-2.11.0+cu128 CUDA:0 (Tesla T4, 14913MiB)
Model summary (fused): 73 layers, 3,006,233 parameters, 0 gradients, 8.1 GFLOPs
                 Class     Images  Instances      Box(P          R      mAP50  mAP50-95): 100% ━━━━━━━━━━━━ 8/8 1.4it/s 5.6s
                   all        236       1962      0.831      0.827       0.87      0.501
                Person        236        736       0.86      0.932      0.937        0.6
                Helmet        234        713      0.811      0.835      0.858      0.466
                  Vest        188        513      0.823      0.713      0.817      0.437
Speed: 0.5ms preprocess, 2.4ms inference, 0.0ms loss, 5.3ms postprocess per image
Results saved to /content/runs/detect/ppe_experiments/colab_yolov8n-2
