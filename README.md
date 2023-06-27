# CPC1HN Uniform Detection

CPC1HN Uniform Detection is built exclusively to detect CPC1HN Pharmacy's uniform (namely, bag, helmet, shirt), employees' faces, mainly for taking attendance purposes. 

## Installation
Clone repo and install [requirements.txt](https://github.com/g9-9g/uniform_detection_server/blob/main/requirements.txt) in a [Python>=3.7.0](https://www.python.org/) environment.

```
git clone https://github.com/g9-9g/uniform_detection_server
cd uniform_detection_server
pip install -r requirements.txt
```

## Usage
Run:
```
python src\app.py
```

Upload an image of the employee and input their user ID. 
* Face Verification: Verify and output if the detected face in the image is the same person as given user ID.
* Uniform Detection: Check if bags, helmets and shirts (with company's logo) are included in the image.

## API Guide (work in progress)
* POST User/UserLogin - description
* POST User/GetUserLst - description
