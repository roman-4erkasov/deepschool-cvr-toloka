# deepschool-cvr-toloka

Automated creation of the following crowdsourcing projects on Toloka.ai:
1. **Collection of barcode photos.** The purpose of this project is to collect photos with barcodes using crowdsourcing service toloka.ai.
2. **Detection of barcodes on photos.** This project is formed to outline barceodes with their number on photos from the project above.
3. **Text recognition of the barcodes.** The goal of the project is to write out number of every outlined barcode from the second project. 


## Getting started

To install the requirements run the following command from the repositorty directory:
```bash
make install
```

To host the first project run:
 - for sandbox: `TOLOKA_TOKEN=<TOKEN> make run_collection`
 - for production: `TOLOKA_TOKEN=<TOKEN> make run_collection CFG=production.yml`

Where "<TOKEN>" is token of your profile in "toloka.ai".

To host the second project run:
```bash
TOLOKA_TOKEN=<TOKEN> make run_bbox_labeling 
```

To host the third project run:
```bash
TOLOKA_TOKEN=<TOKEN> make run_ocr_labeling 
```

