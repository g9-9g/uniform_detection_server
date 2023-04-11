from roboflow import Roboflow
import os 




class RoboflowController:

    def __init__(self, project_name, api_key, env):
        self.project_name = project_name
        self.api_key = api_key
        self.model = None
        # Set environment
        os.environ["DATASET_DIRECTORY"] = env

        # Load project

        rf = Roboflow(api_key=api_key)
        self.project = rf.workspace().project(self.project_name)

    def download(self, dataset_version, model_format):
        if self.project:
            return self.project.version(dataset_version).download(model_format)
        else:
            return 0

    def fixPath(self):
        pass

    def upload(self, files=[]):
        if not self.project:
            raise Exception("No project available")

        # Local images

        for file in files:
            if not allowed_file(file):
                raise Exception("File is not allowed")

            print(self.project.upload(file))

    def predict(self, dataset_version, confidence=40, overlap=30, files=[], save=None):
        if not self.project:
            return 0


        results = []

        # Get model
        self.model = self.project.version(dataset_version).model

        # Infer on a local image
        for file in files:

            # preprocessing
            filename = os.path.basename(file)
            predict_model = self.model.predict(file, confidence=confidence, overlap=overlap)

            # Append res
            results.append({filename: predict_model.json()})
            if save:
                predict_model.save(os.path.join(save, filename))

        return results

if __name__ == '__main__':
    rfa = RoboflowController(project_name="2yeardataset",
                             api_key="mfrbcbsvA7OvqaeeQHac",
                             env="Dataset")

    from PIL import Image
    image = Image.open('a.jpg').resize((640, 640))
    image.save('new.jpg')
    
    print(rfa.predict(5, files=["new.jpg"],
                      ))

    # rfa.upload(image_dir=[{"dir":'new.jpg'}])