'''
Created on 08.03.2013

@author: andre
'''
import algo
import os
import patch_generator
from PIL import Image, ImageDraw
import json

### NEEDS: svm model + codebook file (k-means clusters for generating the histograms)
SVM_MODEL_FILE = '../data/svm.pkl'
SIFT_CODEBOOK_FILE = '../data/codebook'
HYPERPARAMETERS_FILE = '../data/svm.pkl.info.json'

DATASET_DIR = '../data/patches/test'
TMP_DIR = '../data/tmp/test/'

IMG_BBOX=(11.60339,48.17708,11.61304,48.18326) ; IMG_SIZE=(1500, 1000) ; IMG_NAME="dopA" # between Grasmeier and Crailsheimerstr.
SATELLITE_IMG_VISUALIZATION_INPUT="dopA/dop-annotated.png"
SATELLITE_IMG_VISUALIZATION_OUTPUT="../data/dopA-predictions.png"
#IMG_BBOX =(11.59221,48.17038,11.61233,48.18380) ; IMG_SIZE=(2000, 2000) ; SATELLITE_IMG_TMP="dopB.png" # bigger as above.
#SATELLITE_IMG_VISUALIZATION_INPUT="dopB-annotated.png"
#SATELLITE_IMG_VISUALIZATION_OUTPUT="dopB-predictions.png"
#important: a must be smaller than c, b must be smaller then d


if (__name__ == "__main__"):
    
    # init
    algo.__try_mkdirs(DATASET_DIR)
    algo.__clear_dir(DATASET_DIR)
    algo.__try_mkdirs(TMP_DIR)
    algo.__clear_dir(TMP_DIR)
    
    with open(HYPERPARAMETERS_FILE, "r") as f:
        params = json.loads(f.read())
    
    
    # generate patches
    print "---------------------"
    print "## generating patches from '" + IMG_NAME + "' (" + str(IMG_SIZE[0])+"x"+str(IMG_SIZE[1]) + "; " + str(IMG_BBOX) + ")"
    patch_generator.generate_patches(IMG_BBOX, IMG_SIZE,
        patch_size=params['hyperparameters']['patch_size'], 
        offset_steps=params['hyperparameters']['patch_offset'],
        target_folder=DATASET_DIR,
        force_refresh=False,
        data_folder=IMG_NAME,
    )
    print ""
    
    # predict
    print "---------------------"
    print "## predicting"
    predictions = algo.predict(SVM_MODEL_FILE, SIFT_CODEBOOK_FILE, DATASET_DIR, TMP_DIR)
    
    
    # generate visualization
    print "---------------------"
    print "## generating visualization"
    
    img = Image.open(SATELLITE_IMG_VISUALIZATION_INPUT)
    overlay = Image.new('RGB', img.size, 0)
    draw = ImageDraw.Draw(overlay)  
    
    print "\n\nPredictions:"
    for filepath, is_building in predictions.items():
        filename = os.path.basename(filepath)
        print filename
        coverage, x, y = os.path.splitext(filename)[0].split('_')
        x = int(x); y = int(y)
        print '{coverage}: {is_building}'.format(coverage=coverage, is_building=is_building[0])
        if is_building[0] == 1:
            draw.rectangle([x,y,x+48, y+48], fill='violet', outline='grey')
        else:
            draw.rectangle([x,y,x+48, y+48], fill='yellow', outline='grey')
    
    combined = Image.blend(img, overlay, 0.3) 
    combined.show()  
    combined.save(SATELLITE_IMG_VISUALIZATION_OUTPUT) 
    
    print "saved visualization to '" + SATELLITE_IMG_VISUALIZATION_OUTPUT + "' (violet := building detected; yellow := no building detected) "


print 'done'

