import argparse
import os
import torch
from torch import nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data.dataloader import DataLoader
from tqdm import tqdm
from model import DnCNN_leacky
import matplotlib.pyplot as plt
from utils import AverageMeter
import torch.backends.cudnn as cudnn

cudnn.benchmark = True
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


from PIL import Image
from torch.utils.data import Dataset
import torch
import os
import numpy as np

from PIL import Image, ImageFilter, ImageEnhance
from torch.utils.data import Dataset
import torch
import os
import numpy as np
import random

model=DnCNN_leacky(num_layers=17)
model = model.to(device)
#criterion = nn.MSELoss(reduction='sum')
criterion = nn.MSELoss(size_average=False)
optimizer = optim.Adam(model.parameters())
scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)

class NoisyCustomDataset(Dataset):
    def __init__(self, img_dir, transform=None, noise_factor=0.5, salt_pepper_ratio=0.05):
        self.img_dir = img_dir
        self.img_names = os.listdir(img_dir)
        self.transform = transform
        self.noise_factor = noise_factor
        self.salt_pepper_ratio = salt_pepper_ratio

      # Convert numpy array back to PIL Image


    def add_brightness_contrast_change(self, image):
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(random.uniform(0.5, 1.2))  # ランダムに明度を変更 もともと　0.5 ,1.5
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(random.uniform(0.5, 1.2))  # ランダムにコントラストを変更0.5 ,1.5
        return image

    def add_blur(self, image):

        return image.filter(ImageFilter.GaussianBlur(radius=random.randint(0, 2)))  # ランダムにぼかしを追加
             #もともと　３
    def add_radial_noise(self, image):
        x, y = image.size
        center_x, center_y = np.random.randint(0, x), np.random.randint(0, y)
        strength = np.random.uniform(0, 255)
        for i in range(x):
            for j in range(y):
                distance = np.sqrt((center_x - i) ** 2 + (center_y - j) ** 2)
                if distance == 0:
                    distance = 1  # 0除算を防ぐために距離が0のときは1を代入します
            change = np.random.uniform(0, 1) * strength / distance
            pixel = image.getpixel((i, j)) + change
            image.putpixel((i, j), int(pixel))
        return image


    def __getitem__(self, index):
        img_path = os.path.join(self.img_dir, self.img_names[index])
        image = Image.open(img_path).convert('L')


        

        # ランダムにノイズのタイプを選びます
        noise_type = random.choice(['gaussian',  'brightness_contrast', 'blur', 'radial'])

        if noise_type == 'gaussian':
           image_np = np.array(image)  # Convert PIL Image to numpy array
           noisy_image_np = image_np + self.noise_factor * np.random.randn(*image_np.shape)
           noisy_image_np = np.clip(noisy_image_np, 0, 255)  # Ensure the value is in [0, 255]
           noisy_image = Image.fromarray(noisy_image_np.astype(np.uint8))  # Convert numpy array back to PIL Image
        #elif noise_type == 'salt_pepper':
            #noisy_image = self.add_salt_pepper_noise(image)
        elif noise_type == 'brightness_contrast':
            noisy_image = self.add_brightness_contrast_change(image)
        elif noise_type == 'blur':
            noisy_image = self.add_blur(image)
        elif noise_type == 'radial':
            noisy_image = self.add_radial_noise(image)
        
        if self.transform:
            image = self.transform(image)
            noisy_image=self.transform(noisy_image)


        return noisy_image, image

    def __len__(self):
        return len(self.img_names)




# 変換を定義（必要に応じて調整）
transform = transforms.Compose([
    transforms.ToTensor(),
])

# 自作のデータセットを作成
dataset = NoisyCustomDataset(img_dir='', transform=transform)
batch_size=7

dataloader = DataLoader(dataset=dataset,
                            batch_size=batch_size,
                            shuffle=True,
                           )

epochs=50
save_number=

history={'loss':[]}

for epoch in range(epochs):
        #epoch_losses = AverageMeter()
    train_loss=0
       
    for data in tqdm(dataloader):
            inputs, labels = data
            inputs = inputs.to(device)
            labels = labels.to(device)
            optimizer.zero_grad()
            preds = model(inputs)

            loss = criterion(preds, labels) / (2 * len(inputs))
            train_loss+=loss.item()

            loss.backward()
            optimizer.step()

            avg_train_loss = train_loss / len(dataloader)

    history['loss'].append(avg_train_loss)



    if (epoch + 1) % 1 == 0:
                 print("epoch{} train_loss:{:.4} ".format(epoch,avg_train_loss))


plt.plot(history['loss'],
         marker='.',
         label='loss(Training)')


plt.legend(loc='best')
plt.grid()
plt.xlabel('epoch')
plt.ylabel('loss')
plt.savefig("./lodd/loss_own{}.png".format(save_number))

PATH = ''
torch.save(model.state_dict(), PATH)
