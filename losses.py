from theanets.losses import Loss
import theano.tensor as TT

class CrossEntropyLoss(Loss):

    def __call__(self, outputs):
        output = outputs[self.output_name]
        target = self._target
        xe = target * TT.log(output) + (1 - target) * \
            TT.log(1 - output)  # Cross-entropy
        return -xe.sum()