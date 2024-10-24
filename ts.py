import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from sklearn.metrics import accuracy_score, roc_auc_score
import numpy as np

# 1. Create synthetic input data for the image, OD segmentation, vessel segmentation, and glaucoma label
def generate_synthetic_data(batch_size=4, img_size=512):
    # Random synthetic image batch (4-channel: 3 for image + 1 for segmentation)
    image = torch.rand(batch_size, 3, img_size, img_size)  # Simulated RGB fundus image
    seg_od = torch.rand(batch_size, 1, img_size, img_size)  # Simulated Optic Disc segmentation mask
    seg_vessel = torch.rand(batch_size, 1, img_size, img_size)  # Simulated Blood Vessel segmentation mask
    
    # Ensure that glaucoma labels contain both 0 and 1
    glaucoma_labels = torch.cat([torch.zeros(batch_size // 2), torch.ones(batch_size // 2)]).float()
    
    # Shuffle the labels and data to randomize the positions
    perm = torch.randperm(batch_size)
    return image[perm], seg_od[perm], seg_vessel[perm], glaucoma_labels[perm]

# 2. ResNet50-based Glaucoma Detection Network
class GlaucomaDetectionNetwork(nn.Module):
    def __init__(self):
        super(GlaucomaDetectionNetwork, self).__init__()
        # Pretrained ResNet50 model
        self.resnet = models.resnet50(pretrained=True)
        # Modify the input to accept 5-channel input (3 for RGB + 2 for segmentation outputs)
        self.resnet.conv1 = nn.Conv2d(5, 64, kernel_size=7, stride=2, padding=3, bias=False)
        nn.init.kaiming_normal_(self.resnet.conv1.weight, mode='fan_out', nonlinearity='relu')  # Initialize weights
        self.resnet.fc = nn.Linear(self.resnet.fc.in_features, 1)  # Binary classification

    def forward(self, image, seg_od, seg_vessel):
        # Concatenate the image and segmentation outputs (5 channels total)
        combined_input = torch.cat((image, seg_od, seg_vessel), dim=1)  # Concatenate along channel axis
        return torch.sigmoid(self.resnet(combined_input))

# 3. Loss function: Binary Cross Entropy Loss
criterion = nn.BCELoss()

# 4. Function to evaluate metrics (accuracy and AUC)
def evaluate_metrics(preds, labels):
    # Convert predictions to binary format
    preds_binary = (preds > 0.5).float()
    accuracy = accuracy_score(labels.cpu(), preds_binary.cpu())
    
    # Compute AUC (Area Under Curve) only if both classes are present
    if len(torch.unique(labels)) > 1:
        auc = roc_auc_score(labels.cpu().numpy(), preds.cpu().detach().numpy())
    else:
        auc = None  # AUC is undefined if only one class is present
    
    return accuracy, auc

# 5. Training loop (for synthetic data)
def train_glaucoma_detection(num_epochs=5, batch_size=4):
    # Generate synthetic data
    image, seg_od, seg_vessel, glaucoma_labels = generate_synthetic_data(batch_size=batch_size)

    # Initialize model
    model = GlaucomaDetectionNetwork()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    image, seg_od, seg_vessel, glaucoma_labels = image.to(device), seg_od.to(device), seg_vessel.to(device), glaucoma_labels.to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    for epoch in range(num_epochs):
        model.train()
        optimizer.zero_grad()

        # Forward pass
        preds = model(image, seg_od, seg_vessel).squeeze()
        loss = criterion(preds, glaucoma_labels)

        # Backward pass and optimization
        loss.backward()
        optimizer.step()

        # Evaluate metrics
        model.eval()
        with torch.no_grad():  # Disable gradient calculation for evaluation
            accuracy, auc = evaluate_metrics(preds, glaucoma_labels)

        if auc is not None:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}, AUC: {auc:.4f}')
        else:
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}, Accuracy: {accuracy:.4f}, AUC: Undefined (only one class present)')

# Run training for glaucoma detection (synthetic example)
train_glaucoma_detection(num_epochs=5, batch_size=4)
