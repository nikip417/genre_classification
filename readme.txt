Nikita Patel
CS 615 - Deep Learning
README

Included is all the code that allowed me to produce the results expressed in
my paper and as part of this project.

My source code is included as a python file and contains relevant methods to reproduce all of my work. Depending on what you would like to reproduce, different methods will have to be called.

Generating Data
The Generate section takes the GTZAN dataset broken into multiple directories based on genre and saves off a compressed JSON file of relevant data. If attempting to recreate the the generating of the json, the GTZAN dataset will need to be downloaded and the file path will need to be passed in to the save_mfcc along with the path of where you would like to store the JSON file. The other optional arguments should not be passed in, the default values are the configurations values I used as the basis of this experiment.
save_mfcc(dataset_path, json_path, num_mfcc=13, n_fft=2048, 
              hop_length=512, num_segments=5)


Load JSON
If a Json file already exists, it must be loaded so the value can be used in all the experimental models.
inputs, targets = load_data(data_json_path)

MLP
There are 3 types of MLPs implemented as part of this project and they vary between having 1, 3 and 5 hidden layers. To run the MLP training and classification call the following methods:
audio_classification_mlp(inputs, targets) # 3 layers, no dropout
audio_classification_mlp_dropouts(inputs, targets) # 3 layers, with dropout
audio_classification_mlp5_dropouts(inputs, targets, dropout=.3) # 5 layers, with dropout
audio_classification_mlp1_dropouts(inputs, targets, dropout=.3) # 1 layers, with dropout

CNN
to run the CNN trainer and classifier run:
audio_classification_cnn(inputs, targets, dropout=0.3)

RNN
to run the RNN trainer and classifier run:
audio_classification_rnn_lstm(inputs, targets, dropout)

The following python libraries were used as part of this project:
json
os
math
librosa
numpy
matplotlib
sklearn
tensorflow
seaborn