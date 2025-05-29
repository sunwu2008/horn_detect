import argparse
import re

def timestamp_to_ms(timestamp):
    """Convert a timestamp string 'MM:SS.mmm' to milliseconds."""
    minutes, seconds = map(float, timestamp.split(":"))
    return int((minutes * 60 + seconds) * 1000)

def ms_to_timestamp(ms):
    """Convert milliseconds to a timestamp string 'MM:SS.mmm'."""
    seconds, milliseconds = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02}:{int(seconds):02}.{int(milliseconds):03}"

def parse_log_line(line):
    """Extract start_ms, end_ms, and similarity from a log line."""
    match = re.match(r"Match: (\d{2}:\d{2}\.\d{3}) → (\d{2}:\d{2}\.\d{3}) \| Similarity: ([\d\.]+)", line)
    if match:
        start_str, end_str, similarity_str = match.groups()
        start_ms = timestamp_to_ms(start_str)
        end_ms = timestamp_to_ms(end_str)
        similarity = float(similarity_str)
        return (start_ms, end_ms, similarity)
    return None

def merge_intervals(intervals, gap_ms=3000):
    """Merge intervals that are within 'gap_ms' milliseconds of each other."""
    if not intervals:
        return []

    # Sort intervals by start time
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]

    for current in intervals[1:]:
        last = merged[-1]
        if current[0] - last[1] <= gap_ms:
            # Merge intervals
            new_start = last[0]
            new_end = max(last[1], current[1])
            new_similarity = max(last[2], current[2])  # You can choose how to handle similarity
            merged[-1] = (new_start, new_end, new_similarity)
        else:
            merged.append(current)

    return merged

def process_log_file(input_path, output_path, gap_ms=3000):
    """Read the input log file, merge intervals, and write to the output file."""
    intervals = []

    # Read and parse the input log file
    with open(input_path, 'r') as infile:
        for line in infile:
            parsed = parse_log_line(line)
            if parsed:
                intervals.append(parsed)

    # Merge intervals
    merged_intervals = merge_intervals(intervals, gap_ms=gap_ms)

    # Write merged intervals to the output file
    with open(output_path, 'w') as outfile:
        for start_ms, end_ms, similarity in merged_intervals:
            start_str = ms_to_timestamp(start_ms)
            end_str = ms_to_timestamp(end_ms)
            outfile.write(f"Match: {start_str} → {end_str} | Similarity: {similarity:.2f}\n")

# Command-line interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge intervals from a log file based on a specified gap.")
    parser.add_argument("--i", required=True, help="Path to the input log file (e.g., match_log.txt).")
    parser.add_argument("--o", required=True, help="Path to the output merged log file (e.g., logall.txt).")
    parser.add_argument("--gap_ms", type=int, default=3000, help="Maximum gap in milliseconds to merge intervals (default: 3000).")

    args = parser.parse_args()
    process_log_file(args.i, args.o, gap_ms=args.gap_ms)

    #python log_merge.py --i match_log.txt --o logall.txt --gap_ms 3000 
