# LJSpeech Dataset Creator

## Overview

The LJSpeech Dataset Creator is a Python script designed to convert a long audio file into an LJSpeech-formatted dataset. This tool segments the audio into shorter clips and generates the necessary metadata for training speech synthesis models.

## Features

- **Automatic Audio Segmentation**: The script divides the input audio into `.wav` files, each ranging between 1 to 15 seconds.
- **LJSpeech-Compatible**: The output dataset includes a `dataset/wavs` folder with the segmented audio files and a `dataset/metadata.csv` file containing the transcriptions, all formatted according to LJSpeech standards.
- **Simple Command-Line Interface**: Easily create a dataset by specifying the path to your audio file.
- **Metadata Processor**: The repository includes a `metadata_processor.py` script that cleans and corrects the vocabulary in the metadata CSV file using OpenAI's API, ensuring high-quality text data.

## Requirements

- Python version 3.x
- Download a [Whisper Model](https://huggingface.co/Mozilla/whisperfile/tree/main) as `.llamafile` to handle the audio transcription and put it in the root of the project.
- Run `pip install -r requirements.txt` to install the dependencies.
- Install `ffmpeg` in your system to handle the audio file conversion.

## Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/Jonfr0/ljspeech-dataset-creator.git
cd ljspeech-dataset-creator
```

## Execution

### LJSpeech Dataset Creator

```bash
python ljspeech_dataset_creator.py --audio_path "path/to/your/audio/file.mp3" --language "es"
```

#### Language options:

- es: Spanish
- en: English
- fr: French
- de: German
- it: Italian
- nl: Dutch
- pt: Portuguese
- zh: Chinese
- ja: Japanese
- ko: Korean
- ru: Russian
- ar: Arabic

### Metadata Processor

1. Create a `.env` file in the project directory with your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key
   ```

2. Run the script:

   ```bash
   python metadata_processor.py
   ```

3. The script will process the `metadata.csv` file, clean the data, and correct the vocabulary using OpenAI's API. The cleaned data will be saved as `cleaned_metadata.csv` in the same `dataset/` directory.
