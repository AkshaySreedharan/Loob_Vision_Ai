from abc import ABC, abstractmethod


class BaseModel(ABC):

    @abstractmethod
    def predict(self, image):
        """
        Run inference on an image.
        """
        pass