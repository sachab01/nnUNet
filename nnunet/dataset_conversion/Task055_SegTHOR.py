#    Copyright 2020 Division of Medical Image Computing, German Cancer Research Center (DKFZ), Heidelberg, Germany
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from collections import OrderedDict
from nnunet.paths import nnUNet_raw_data
from batchgenerators.utilities.file_and_folder_operations import *
import shutil
import SimpleITK as sitk


def convert_for_submission(source_dir, target_dir):
    """
    I believe they want .nii, not .nii.gz
    :param source_dir:
    :param target_dir:
    :return:
    """
    files = subfiles(source_dir, suffix=".nii.gz", join=False)
    maybe_mkdir_p(target_dir)
    for f in files:
        img = sitk.ReadImage(join(source_dir, f))
        out_file = join(target_dir, f[:-7] + ".nii")
        sitk.WriteImage(img, out_file)



if __name__ == "__main__":
    base = "/data/segthor_train"

    task_id = 55
    task_name = "SegTHOR"

    foldername = "Task%03.0d_%s" % (task_id, task_name)

    nnUNet_raw_data = "/Users/sachabuijs/Documents/AI4MI/nnUNet_raw_data"  # Use a directory in your home folder
    out_base = os.path.join(nnUNet_raw_data, foldername)
    imagestr = os.path.join(out_base, "imagesTr")
    imagests = os.path.join(out_base, "imagesTs")
    labelstr = os.path.join(out_base, "labelsTr")
    maybe_mkdir_p(imagestr)
    maybe_mkdir_p(imagests)
    maybe_mkdir_p(labelstr)

    train_patient_names = []
    test_patient_names = []


    for patient_folder in os.listdir(f"../../..{base}/train"):
        patient_path = os.path.join(f"../../..{base}/train", patient_folder)
        if os.path.isdir(patient_path) and patient_folder.startswith("Patient_"):
            p = patient_folder.split('_')[1]  # Extract patient number
            label_file = os.path.join(patient_path, "GT.nii.gz")
            image_file = os.path.join(patient_path, f"Patient_{p}.nii.gz")

            shutil.copy(image_file, join(imagestr, p + "_0000.nii.gz"))
            shutil.copy(label_file, join(labelstr, p + ".nii.gz"))
            train_patient_names.append(p)

    # test_patients = subfiles(join(base, "test"), join=False, suffix=".nii.gz")
    # for p in test_patients:
    #     p = p[:-7]
    #     curr = join(base, "test")
    #     image_file = join(curr, p + ".nii.gz")
    #     shutil.copy(image_file, join(imagests, p + "_0000.nii.gz"))
    #     test_patient_names.append(p)

    for patient_folder in os.listdir(f"../../..{base}/test"):
        patient_path = os.path.join(f"../../..{base}/test", patient_folder)
        if os.path.isdir(patient_path) and patient_folder.startswith("Patient_"):
            p = patient_folder.split('_')[1]  # Extract patient number
            image_file = os.path.join(patient_path, f"Patient_{p}.nii.gz")
            
            # # Rename and move ground truth (GT) file
            # new_gt_filename = f"BRATS_{str(patient_num).zfill(3)}.nii.gz"
            # shutil.copy(gt_file, os.path.join(dest_dir, "labelsTr", new_gt_filename))
            
            # # Rename and move image file for a single modality
            # new_img_filename = f"BRATS_{str(patient_num).zfill(3)}_0000.nii.gz"
            # shutil.copy(img_file, os.path.join(dest_dir, "imagesTr", new_img_filename))
            shutil.copy(image_file, join(imagests, p + "_0000.nii.gz"))
            test_patient_names.append(p)


    json_dict = OrderedDict()
    json_dict['name'] = "SegTHOR"
    json_dict['description'] = "SegTHOR"
    json_dict['tensorImageSize'] = "4D"
    json_dict['reference'] = "see challenge website"
    json_dict['licence'] = "see challenge website"
    json_dict['release'] = "0.0"
    json_dict['modality'] = {
        "0": "CT",
    }
    json_dict['labels'] = {
        "0": "background",
        "1": "esophagus",
        "2": "heart",
        "3": "trachea",
        "4": "aorta",
    }
    json_dict['numTraining'] = len(train_patient_names)
    json_dict['numTest'] = len(test_patient_names)
    json_dict['training'] = [{'image': "./imagesTr/%s.nii.gz" % i.split("/")[-1], "label": "./labelsTr/%s.nii.gz" % i.split("/")[-1]} for i in
                             train_patient_names]
    json_dict['test'] = ["./imagesTs/%s.nii.gz" % i.split("/")[-1] for i in test_patient_names]

    save_json(json_dict, os.path.join(out_base, "dataset.json"))
