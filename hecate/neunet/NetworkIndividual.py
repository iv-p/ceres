''' Neural network individual in genetic algorithms '''
import os
import numpy as np
import uuid
import random

from genalg.individual import Individual
from caffe2.python import workspace, model_helper, optimizer, core, brew
from caffe2.proto import caffe2_pb2

class NetworkIndividual(Individual):
    ''' Defines how an neural network is generated, mutated, etc. '''
    gpu_no = 0
    device_option = caffe2_pb2.DeviceOption(device_type=caffe2_pb2.CUDA)

    def __init__(self, params, layers=[]):
        self.fitness = 0
        self.name = str(uuid.uuid4())
        self.params = params
        self.layers = np.array(layers)
        
        self.accuracy = np.zeros(self.params["total_iters"])
        self.loss = np.zeros(self.params["total_iters"])

        if len(self.layers) == 0:
            self.generate_layers()
        
        self.define_training_model()
        self.define_validation_model()

    def crossover(self, other):
        ''' Defines how we crossover two individuals and produce
            two new ones '''
        my_point = random.randint(1, len(self.layers))
        other_point = random.randint(0, len (other.layers) - 1)

        layers = np.concatenate((self.layers[:my_point], other.layers[other_point:]))

        for layer in layers:
            if "object" in layer.keys():
                del layer["object"]
        return NetworkIndividual(
            self.params,
            layers)

    def mutate(self):
        ''' Defines how we mutate an individual '''
        layer = random.randint(0, len(self.layers) - 1)
        self.layers[layer]["neurons"] = random.randint(self.params["min_neurons"], self.params["max_neurons"])

    def evaluate(self):
        ''' Defines how we evaluate an individual.'''
        workspace.ResetWorkspace()

        workspace.RunNetOnce(self.training_model.param_init_net)
        workspace.CreateNet(self.training_model.net,overwrite=True,input_blobs=['data','label'])

        for i in range(self.params["total_iters"]):
            workspace.RunNet(self.training_model.net)
            self.accuracy[i] = workspace.FetchBlob('accuracy')
            self.loss[i] = workspace.FetchBlob('loss')

        self.fitness = np.amax(self.accuracy)
        workspace.RunNetOnce(self.validation_model.param_init_net)
        workspace.CreateNet(self.validation_model.net,overwrite=True,input_blobs=['data','label'])

        workspace.RunNet(self.validation_model.net)
        self.fitness = workspace.FetchBlob('accuracy')
        print ".",

    def get_fitness(self):
        ''' Gets the fitness of this individual - (0 .. 1] if training successful
            or 0 if training failed '''
        return self.fitness

    def add_training(self, model, softmax):
        # Loss Calculation
        xent = model.LabelCrossEntropy([softmax, 'label'])
        loss = model.AveragedLoss(xent, "loss")
        # Calculating Accuracy
        self.add_accuracy(model, softmax)
        # Add loss to gradient for backpropogation
        model.AddGradientOperators([loss])
        # Initializing the SGD the solver
        opt = optimizer.build_sgd(model, base_learning_rate=self.params["base_learning_rate"], policy="step", stepsize=1, gamma=self.params["gamma"])

    def add_accuracy(self, model, softmax):
        brew.accuracy(model, [softmax, 'label'], "accuracy")

    def add_input(self, model, db, db_type):
        # load the data
        data_uint8, label = model.TensorProtosDBInput(
            [], 
            ["data_uint8", "label"], 
            batch_size=self.params["batch_size"],
            db=db, db_type=db_type)
        # cast the data to float
        data = model.Cast(data_uint8, "data", to=core.DataType.FLOAT)
        # don't need the gradient for the backward pass
        data = model.StopGradient(data, data)
        return data, label

    def generate_layers(self):
        num_layers = random.randint(self.params["min_layers"], self.params["max_layers"])
        for _ in range(0, num_layers):
            self.layers = np.append(self.layers, {
                "neurons" : random.randint(self.params["min_neurons"], self.params["max_neurons"]),
                "name" : str(uuid.uuid4())
            })

    def add_model(self, model):
        with core.DeviceScope(self.device_option):
            for i, layer in enumerate(self.layers):
                if i > 0:
                    layer_input = {
                        "name": self.layers[i-1]["object"],
                        "neurons": self.layers[i-1]["neurons"]
                    }
                else:
                    layer_input = {
                        "name": "data",
                        "neurons": self.params["input_size"]
                    }
                layer_object = brew.fc(
                    model,
                    layer_input["name"],
                    layer["name"],
                    layer_input["neurons"],
                    layer["neurons"])
                layer_object = brew.relu(model, layer_object, layer_object) #try with sigmoid

                self.layers[i]["object"] = layer_object

            prediction = brew.fc(
                model,
                self.layers[-1]["object"],
                "prediction-" + self.name,
                self.layers[-1]["neurons"],
                self.params["categories"])
            softmax = brew.softmax(model, prediction, str(uuid.uuid4()))
        return softmax

    def define_training_model(self):
        self.training_model = model_helper.ModelHelper(name="training-" + self.name)
        self.training_model.net.RunAllOnGPU(
            gpu_id=self.gpu_no, 
            use_cudnn=True)
        self.training_model.param_init_net.RunAllOnGPU(
            gpu_id=self.gpu_no, 
            use_cudnn=True)

        data, label = self.add_input(
            self.training_model, 
            db=os.path.join('data/crowdflower/train.minidb'),
            db_type='minidb')

        soft=self.add_model(self.training_model)
        self.add_training(self.training_model, soft)

    def define_validation_model(self):
        self.validation_model = model_helper.ModelHelper(name="validation-" + self.name, init_params=False)
        self.validation_model.net.RunAllOnGPU(
            gpu_id=self.gpu_no, 
            use_cudnn=True)
        self.validation_model.param_init_net.RunAllOnGPU(
            gpu_id=self.gpu_no, 
            use_cudnn=True)

        data, label = self.add_input(
            self.training_model, 
            db=os.path.join('data/crowdflower/test.minidb'),
            db_type='minidb')

        soft=self.add_model(self.validation_model)
        self.add_accuracy(self.validation_model, soft)
