Detect and log all segments in the full MP3 that match the sample with similarity above a chosen threshold.
it can detect horn and mark all the times.

python merge_intervals.py --input_log match_log.txt --output_log logall.txt --gap_ms 3000 
merg the all lines within 3000ms to one line(assuming horn lasts 3s)
