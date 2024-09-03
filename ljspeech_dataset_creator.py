import argparse
import subprocess
import pandas as pd
import re
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from num2words import num2words
import os
import math


# Argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="Create LJSpeech dataset from audio file")
    parser.add_argument("--audio_path", required=True, help="Path to the input audio file")
    return parser.parse_args()

# Dataset creation
def create_dataset_directory():
    dataset_dir = 'dataset'
    os.makedirs(dataset_dir, exist_ok=True)
    os.makedirs(os.path.join(dataset_dir, "wavs"), exist_ok=True)
    return dataset_dir

# Audio processing
def slice_audio(audio_path, dataset_dir, start_buffer_ms=250, end_buffer_ms=480, sample_rate=22050):
    # Load the audio file
    audio = AudioSegment.from_file(audio_path)

    # Detect non-silent segments
    non_silent_ranges = detect_nonsilent(audio, min_silence_len=500, silence_thresh=-40)

    print(f"Non-silent segments detected: {len(non_silent_ranges)}")

    # Export chunks as wav files
    wav_files = []
    for i, (chunk_start, chunk_end) in enumerate(non_silent_ranges):
        # Add buffer to start and end, ensuring we don't go out of bounds
        buffered_start = max(0, chunk_start - start_buffer_ms)
        buffered_end = min(len(audio), chunk_end + end_buffer_ms)
        
        output_path = os.path.join(dataset_dir, "wavs", f"{os.path.splitext(os.path.basename(audio_path))[0]}_{i+1:04d}.wav")
        
        # Use ffmpeg to extract the segment with buffer
        subprocess.run([
            "ffmpeg", "-i", audio_path,
            "-ss", str(buffered_start / 1000),  # Convert milliseconds to seconds
            "-to", str(buffered_end / 1000),    # Convert milliseconds to seconds
            "-c:a", "pcm_s16le", "-ar", str(sample_rate),  # Use the specified sample rate
            output_path
        ])
        wav_files.append(output_path)

    # Verify total duration
    total_wav_duration = sum((end - start + start_buffer_ms + end_buffer_ms) / 1000 for start, end in non_silent_ranges)
    original_duration = len(audio) / 1000  # Convert milliseconds to seconds

    print(f"Original audio duration: {original_duration:.2f}s")
    print(f"Total WAV files duration: {total_wav_duration:.2f}s")
    print(f"Difference: {original_duration - total_wav_duration:.2f}s")

    if math.isclose(original_duration, total_wav_duration, rel_tol=1e-2):
        print("The sum of all WAV durations is basically the same as the original audio duration.")
    else:
        print("There is a noticeable difference between the original audio duration and the sum of WAV durations.")

    return wav_files

# Transcription and text processing
def transcribe_audio(wav_file):
    try:
        result = subprocess.run(["./whisper-small.llamafile", "-f", wav_file, "-l", "es"], capture_output=True, text=True, check=True, encoding='utf-8')
        transcription = clean_transcription(result.stdout.strip())
        return transcription
    except subprocess.CalledProcessError as e:
        print(f"Error transcribing {wav_file}: {e}")
        print(f"STDERR: {e.stderr}")
        return ""
    except UnicodeDecodeError as e:
        print(f"Unicode decode error for {wav_file}: {e}")
        return ""

def clean_transcription(transcription):
    cleaned_text = re.sub(r'\[\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\]', '', transcription)
    formatted_text = ' '.join(cleaned_text.split())
    formatted_text = formatted_text.replace('. ', '.\n\n')
    return cleaned_text

# Metadata creation
def create_metadata(wav_files, dataset_dir):
    metadata = []
    for wav_file in wav_files:
        transcription = transcribe_audio(wav_file)
        if transcription:
            cleaned_transcription = clean_text(transcription)
            wav_name = os.path.basename(wav_file)
            metadata.append([wav_name, transcription, cleaned_transcription])
        else:
            print(f"Skipping {wav_file} due to transcription error")
    
    if metadata:
        df = pd.DataFrame(metadata, columns=["wav_file_name", "transcription_text", "cleaned_transcription"])
        df.to_csv(os.path.join(dataset_dir, "metadata.csv"), sep="|", index=False, header=False)
        print(f"Metadata created with {len(metadata)} entries")
    else:
        print("No valid transcriptions. Metadata file not created.")

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9\s,!?]', '', text)
    text = re.sub(r'\d+', lambda m: num2words(int(m.group(0)), lang='es'), text)
    return text

# Main execution
def main():
    args = parse_arguments()
    dataset_dir = create_dataset_directory()
    wav_files = slice_audio(args.audio_path, dataset_dir)
    create_metadata(wav_files, dataset_dir)
    print(f"Dataset created successfully in {dataset_dir}")


if __name__ == "__main__":
    main()