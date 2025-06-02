import argparse
from pydub import AudioSegment
import numpy as np
from scipy.spatial.distance import cosine

# Normalize audio to mono, 16kHz, and consistent loudness
def normalize(audio):
    return (
        audio.set_frame_rate(16000)
             .set_channels(1)
             .apply_gain(-audio.max_dBFS)
    )

# Convert pydub AudioSegment to NumPy array
def audio_to_np(audio_segment):
    return np.array(audio_segment.get_array_of_samples()).astype(np.float32)

# Fast cosine similarity using dot product
def fast_cosine_similarity(a, b):
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    if a_norm == 0 or b_norm == 0:
        return 0.0
    return np.dot(a, b) / (a_norm * b_norm)

# Convert milliseconds to timestamp string
def ms_to_timestamp(ms):
    seconds = ms // 1000
    return f"{seconds // 60:02}:{seconds % 60:02}.{ms % 1000:03}"

# Match segments
def match_segments(full_audio, sample_audio, step_ms=50, similarity_threshold=0.70):
    full_np = audio_to_np(full_audio)
    sample_np = audio_to_np(sample_audio)
    sample_len = len(sample_np)
    matches = []

    step_samples = int((step_ms / 1000) * full_audio.frame_rate)
    total_steps = (len(full_np) - sample_len) // step_samples

    print(f"Scanning {total_steps} segments (step: {step_ms} ms)...")
    for idx, i in enumerate(range(0, len(full_np) - sample_len, step_samples)):
        if total_steps > 0 and idx % max(1, total_steps // 20) == 0:
            print(f"Progress: {100 * idx // total_steps}%")

        segment_np = full_np[i:i + sample_len]
        similarity = fast_cosine_similarity(sample_np, segment_np)
        if similarity > similarity_threshold:
            start_ms = int((i / full_audio.frame_rate) * 1000)
            end_ms = start_ms + len(sample_audio)
            matches.append((start_ms, end_ms, similarity))
    return matches

# Write log file
def log_matches(matches, log_path):
    with open(log_path, "w",encoding="utf-8") as f:
        for start_ms, end_ms, similarity in matches:
            f.write(f"Match: {ms_to_timestamp(start_ms)} → {ms_to_timestamp(end_ms)} | Similarity: {similarity:.2f}\n")

# Main execution
def main(full_mp3_path, sample_mp3_path, similarity_percent, step_ms=50, log_file="match_log.txt"):
    similarity_threshold = similarity_percent / 100.0

    print("Loading and normalizing MP3 files...")
    full_audio = normalize(AudioSegment.from_mp3(full_mp3_path))
    sample_audio = normalize(AudioSegment.from_mp3(sample_mp3_path))

    print(f"Searching for segments with similarity > {similarity_percent}%...")
    matches = match_segments(full_audio, sample_audio, step_ms=step_ms, similarity_threshold=similarity_threshold)

    print(f"\n {len(matches)} matches found.")
    log_matches(matches, log_file)
    print(f" Log written to {log_file}")

# CLI parser
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and log segments in a given MP3 that match a sample MP3.")
    parser.add_argument("--i", required=True, dest="input", help="Path to the given MP3 file.")
    parser.add_argument("--r", required=True, dest="reference", help="Path to the sample MP3 file.")
    parser.add_argument("--s", type=float, required=True, dest="similarity", help="Similarity threshold (0–100).")
    parser.add_argument("--st", type=int, default=50, dest="step", help="Step size in milliseconds (default: 50).")

    args = parser.parse_args()
    main(args.input, args.reference, args.similarity, step_ms=args.step)
    #--s 10 cosine_similarity>10%
    # --st 100 # step size in milliseconds
    #python train_horn.py --i train.mp3 --r tsample.mp3 --s 10 --st 100
